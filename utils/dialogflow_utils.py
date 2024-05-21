from google.cloud import dialogflow
from google.cloud.dialogflow_v2 import DetectIntentResponse


def detect_intent(project_id: str, session_id: str, text: str, language_code: str) -> DetectIntentResponse:
    """
    Call Dialogflow API to get response
    :param project_id: The GCP project ID
    :param language_code: The language code
    :param session_id: The session id
    :param text: The given input
    :return: The response
    """
    session_client = dialogflow.SessionsClient()
    current_session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(session=current_session, query_input=query_input)
    return response
