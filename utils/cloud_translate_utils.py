from google.cloud import translate_v2


def __translate(translate_client: translate_v2.Client, text: str, target_language: str) -> dict | list:
    """
    Call Cloud Translate API to translate given text
    :param translate_client: The Cloud Translate client
    :param text: The input
    :param target_language: The target language
    :return: The full response of the API
    """
    return translate_client.translate(text, target_language=target_language)


def translate_and_get_text(translate_client: translate_v2.Client, text: str, target_language: str) -> str:
    """
    Call Cloud Translate API to translate given text
    :param translate_client: The Cloud Translate client
    :param text: The input
    :param target_language: The target language
    :return: The translated text only
    """
    return __translate(translate_client, text, target_language)['translatedText']


def translate_and_get_detail(translate_client: translate_v2.Client, text: str, target_language: str) -> tuple[str, str]:
    """
    Call Cloud Translate API to translate given text
    :param translate_client: The Cloud Translate client
    :param text: The input
    :param target_language: The target language
    :return: The translated text and the detected source language
    """
    translation = __translate(translate_client, text, target_language)
    return translation['translatedText'], translation['detectedSourceLanguage']