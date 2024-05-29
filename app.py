import os
import uuid

from dotenv import load_dotenv
from flask import Flask, request, session, jsonify, render_template
from flask_cors import CORS
from google.cloud import translate_v2 as translate
from google.cloud import vision_v1 as vision
from pymongo import errors

from controller.tour_controller import get_tour_by_params, get_tour_by_id, get_all_tours
from utils import cloud_vision_utils, cloud_translate_utils, dialogflow_utils

# Load .env
load_dotenv()
TARGET_LANGUAGE = os.getenv("TARGET_LANGUAGE")
PROJECT_ID = os.getenv("PROJECT_ID")
SECRET_KEY = os.getenv("FLASK_SECRET")

# Setup client
translate_client = translate.Client()
vision_client = vision.ImageAnnotatorClient()

# Create Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
# Enable CORS
CORS(app)


@app.route("/")
def index():
    """
    Render the index.html page
    """
    return render_template('index.html')


@app.route('/api/v1/chat', methods=['POST'])
def handle_chat():
    """
    This function handles POST requests to the /chat endpoint.
    It retrieves message, intent, and file data from the request form.

    responses:
        200:
            {
                "response": "Hi! I'm Travelica"
            }
        200:
            {
                "location_response": {
                    "google_map_url": "https://maps.google.com/maps?z=15&t=m&q=loc:21.0277332+105.8522469",
                    "latitude": 21.0277332,
                    "longitude": 105.8522469,
                    "name": "Sword Lake"
                },
                "response": "Sure! I will find the location and send it to you!"
            }
        200:
            {
                "ocr_response": "Mixed sweet soup 15,000 VND",
                "response": "Sure! I will read text from your image and translated it for you"
            }
        400:
            {
                "error": "Invalid image file or missing file"
            }
    """
    # Get data from the request form
    message = request.form.get('message')
    file = request.files.get('file')

    # Validate data
    if not message:
        return jsonify({'error', 'Message is required'}), 400

    if session.get('id') is None:
        session['id'] = str(uuid.uuid4())

    # Translate given message to english, and get client's language
    translated_message, predicted_lang = cloud_translate_utils.translate_and_get_detail(translate_client, text=message,
                                                                                        target_language=TARGET_LANGUAGE)

    # If user language is set before, prefer using it
    session['lang'] = session['lang'] if 'lang' in session else predicted_lang

    # Get dialogflow response
    dialogflow_response = dialogflow_utils.detect_intent(PROJECT_ID, session.get('id'), translated_message,
                                                         TARGET_LANGUAGE)
    response = str(dialogflow_response.query_result.fulfillment_text)
    intent = str(dialogflow_response.query_result.intent.display_name)

    # Translated response message back to client's language
    final_response = {
        'response': cloud_translate_utils.translate_and_get_text(translate_client, text=response,
                                                                 target_language=session['lang']),
    }

    # Handle FAQ TourDetail intent
    if intent.strip().startswith('FAQ'):
        output_contexts = [context.name.split('/')[-1] for context in dialogflow_response.query_result.output_contexts]
        if 'faq-tour-detail' in output_contexts and len(output_contexts) == 1:
            places, budget, duration_day, duration_night = dialogflow_utils.extract_params_from_dialogflow(
                dialogflow_response)
            tour_detail_json = get_tour_by_params(budget, places, duration_day, duration_night)
            # If there is no matched tour
            if not tour_detail_json:
                tour_detail_message = 'There are no tours that match your requirements'
                final_response['no_tour'] = cloud_translate_utils.translate_and_get_text(translate_client,
                                                                                         text=tour_detail_message,
                                                                                         target_language=session[
                                                                                             'lang'])
            else:
                translated_json = []
                for item in tour_detail_json:
                    details = item['destination']
                    translated_details = cloud_translate_utils.translate_and_get_text(translate_client,
                                                                                      text=details,
                                                                                      target_language=session['lang'])
                    new_item = {
                        'id': item['id'],
                        'details': translated_details
                    }
                    translated_json.append(new_item)

                tour_detail_message = 'Click to see detailed information'
                final_response['tour_detail'] = translated_json
                final_response['click'] = cloud_translate_utils.translate_and_get_text(translate_client,
                                                                                       text=tour_detail_message,
                                                                                       target_language=session['lang'])

    # Handle OCR or LOC intent
    if intent.strip().startswith('OCR') or intent.strip().startswith('LOC'):
        if not cloud_vision_utils.is_valid_image(file):
            return jsonify({'error': 'Invalid image file or missing file'}), 400
        if intent.strip().startswith('OCR'):
            # Read OCR
            ocr_response = cloud_vision_utils.read_ocr(vision_client, file.stream.read())
            # Translate OCR response to client's language
            translated_ocr_response = cloud_translate_utils.translate_and_get_text(translate_client,
                                                                                   text=ocr_response,
                                                                                   target_language=session['lang'])
            final_response['ocr_response'] = translated_ocr_response
        elif intent.strip().startswith('LOC'):
            # Find location
            location_response = cloud_vision_utils.find_location(vision_client, file.stream.read())
            # Translate the location name to client's language
            location_name = location_response['name']
            translated_location_name = cloud_translate_utils.translate_and_get_text(translate_client,
                                                                                    text=location_name,
                                                                                    target_language=session['lang'])
            location_response['name'] = translated_location_name
            final_response['location_response'] = location_response

    return jsonify(final_response), 200


@app.route('/api/v1/tour_detail/<int:id>', methods=['GET'])
def get_tour_detail(id: int):
    """
    Handle GET request, return detail of tour with id
    :param id: the tour id
    :return: the tour detail in json
    """
    try:
        tour_detail = get_tour_by_id(id)
        if tour_detail:
            return tour_detail, 200
        else:
            return jsonify({"error": "Tour not found"}), 404
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/tours', methods=['GET'])
def get_tours():
    """
    Handle GET request, return detail of all tours
    :return: the tour detail of all tours in json
    """
    try:
        tours = get_all_tours()
        return tours, 200
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
