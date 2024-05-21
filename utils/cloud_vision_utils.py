from google.cloud import vision
from google.cloud.vision_v1 import ImageAnnotatorClient
from werkzeug.datastructures.file_storage import FileStorage


def is_valid_image(file: FileStorage) -> bool:
    """
    Check if the file is valid
    :param file:
    :return: true if the file is valid, false if not
    """
    if file is None:
        return False
    if file.filename.endswith('.jpg') or file.filename.endswith('.jpeg') or file.filename.endswith('.png'):
        return True
    return False


def read_ocr(vision_client: ImageAnnotatorClient, image: bytes) -> str:
    """
    Call Cloud Vision API to read OCR
    :param vision_client: The Cloud Vision client
    :param image: The image content in bytes
    :return: The OCR content
    """
    features = [vision.Feature(type=vision.Feature.Type.TEXT_DETECTION), ]
    ocr_request = {
        'image': {
            'content': image
        },
        'features': features,
    }
    response = vision_client.annotate_image(request=ocr_request)
    return response.full_text_annotation.text


def __create_google_map_link(latitude: float, longitude: float, zoom=15):
    """
    Simple function to create a google map link
    :param latitude: The latitude
    :param longitude: The longitude
    :param zoom: The zoom level, default is 15
    :return: The google map link
    """
    return f"https://maps.google.com/maps?z={zoom}&t=m&q=loc:{latitude}+{longitude}"


def find_location(vision_client: ImageAnnotatorClient, image: bytes) -> dict:
    """
    Call Cloud Vision API to find landmark location
    :param vision_client: The Cloud Vision client
    :param image: The image content in bytes
    :return: The location result with name, latitude, longitude, and google map url
    """
    features = [vision.Feature(type=vision.Feature.Type.LANDMARK_DETECTION), ]
    landmark_request = {
        'image': {
            'content': image
        },
        'features': features,
    }
    response = vision_client.annotate_image(request=landmark_request)
    latitude = response.landmark_annotations.pb[0].locations[0].lat_lng.latitude
    longitude = response.landmark_annotations.pb[0].locations[0].lat_lng.longitude
    name = response.landmark_annotations.pb[0].description
    return {
        'name': name,
        'latitude': latitude,
        'longitude': longitude,
        'google_map_url': __create_google_map_link(latitude, longitude),
    }
