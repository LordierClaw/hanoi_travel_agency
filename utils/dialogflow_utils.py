from typing import Any

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


def extract_params_from_dialogflow(dialogflow_response) -> tuple[list[str] | list[Any], int, int, int]:
    """
    Extract params from dialogflow response
    :param dialogflow_response: The dialogflow response
    :return: The tuple of the list places, biggest budget, duration day and night
    """
    params_query = dialogflow_response.query_result.parameters
    params_context = dialogflow_response.query_result.output_contexts[0].parameters
    durations = []
    budgets = []
    places = []
    # Extract duration params
    if 'duration' in params_query:
        durations = sorted([int(value['amount']) for value in params_query['duration']])
    elif 'duration' in params_context:
        durations = sorted([int(value['amount']) for value in params_context['duration']])
    # Extract budget params
    if 'budget' in params_query:
        budgets = sorted([int(value['amount']) for value in params_query['budget']])
    elif 'budget' in params_context:
        budgets = sorted([int(value['amount']) for value in params_context['budget']])
    # Extract place params
    if 'place' in params_query:
        places = [str(value) for value in params_query['place']]
    elif 'place' in params_query:
        places = [str(value) for value in params_context['place']]
    places = [''.join(value.lower().split()) for value in places]
    return places, budgets[-1], durations[-1], durations[-1]-1
