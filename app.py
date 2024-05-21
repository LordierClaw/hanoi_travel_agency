import os
import uuid

from dotenv import load_dotenv
from flask import Flask, request, session, jsonify, render_template
from flask_cors import CORS
from google.cloud import translate_v2 as translate
from google.cloud import vision_v1 as vision

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
CORS(app)


@app.route("/")
def index():
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
        return "Message is required", 400

    if session.get('id') is None:
        session['id'] = str(uuid.uuid4())

    # Translate given message to english, and get client's language
    translated_message, session['lang'] = cloud_translate_utils.translate_and_get_detail(translate_client, text=message,
                                                                                         target_language=TARGET_LANGUAGE)

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

    # Handle OCR or LOC intent
    if intent.strip().startswith('OCR') or intent.strip().startswith('LOC'):
        if not cloud_vision_utils.is_valid_image(file):
            return {
                'error': 'Invalid image file or missing file'
            }, 400
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


if __name__ == '__main__':
    app.run(debug=True)
