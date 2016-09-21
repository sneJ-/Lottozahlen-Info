# coding=utf8
"""
@Author: Jens Röwekamp
@Last modified: 21.09.2016

Parses Alexa input, gets the actual Lotto numbers and returns them to the user.

Adapted from the Amazon Python Blueprint.
"""

from __future__ import print_function
import random
import urllib2
import re


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_help_response():
    #List of Ziehungen
    Ziehungen = ['sechs aus neunundvierzig', 'spiel siebenundsiebzig', 'super sechs']
    #Sample Utterances Set
    GetLottozahlenUtterances = [
        "was sind die Lottozahlen", 
        "was sind die aktuellen Lottozahlen", 
        "was sind die Lottozahlen für " + random.choice(Ziehungen), 
        "was sind die aktuellen Lottozahlen für " + random.choice(Ziehungen), 
        "Lottozahlen", 
        "Lottozahlen " + random.choice(Ziehungen), 
        "aktuelle Lottozahlen", 
        "aktuelle Lottozahlen " + random.choice(Ziehungen), 
        "Ziehung " + random.choice(Ziehungen), 
        "was sind die Ziehergebnisse", 
        "was sind die Ziehergebnisse " + random.choice(Ziehungen), 
        "was sind die Ziehergebnisse für " + random.choice(Ziehungen), 
        "gib mir die Lottozahlen", 
        "gib mir die aktuellen Lottozahlen", 
        "gib mir die Lottozahlen für " + random.choice(Ziehungen), 
        "gib mir die aktuellen Lottozahlen für " + random.choice(Ziehungen), 
        "gib mir die Ziehergebnisse", 
        "gib mir die aktuellen Ziehergebnisse", 
        "gib mir die Ziehergebnisse für " + random.choice(Ziehungen), 
        "gib mir die aktuellen Ziehergebnisse für " + random.choice(Ziehungen), 
        "sag mir die Lottozahlen", 
        "sag mir die Ziehergebnisse", 
        "sag mir die aktuellen Lottozahlen", 
        "sag mir die aktuellen Ziehergebnisse", 
        "sag mir die Lottozahlen für " + random.choice(Ziehungen), 
        "sag mir die Ziehergebnisse für " + random.choice(Ziehungen), 
        "sag mir die aktuellen Lottozahlen für " + random.choice(Ziehungen), 
        "sag mir die aktuellen Ziehergebnisse für " + random.choice(Ziehungen)
    ]
    
    card_title = "Welcome_Help"
    speech_output = "Willkommen bei Lotto Info. Bitte sag mir welche Ziehergebnisse du wünscht. Du könntest zum Beispiel sagen: " + random.choice(GetLottozahlenUtterances)
    # If the user either does not reply to the welcome_help message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Bitte sag mir welche Ziehergebnisse du wünscht indem du zum Beispiel sagst: " + random.choice(GetLottozahlenUtterances)
    should_end_session = False
    return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Lotto Info wünscht noch einen schönen Tag."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def get_Lottozahlen(intent, session):
    card_title = "Lottozahlen"
    should_end_session = True
    disclaimer = " ,. Alle Angaben wie immer ohne Gewähr."
    if 'value' in intent['slots']['Ziehung']:
        requested_ziehung = intent['slots']['Ziehung']['value']
        if(requested_ziehung == "sechs aus neunundvierzig" or requested_ziehung == "6 aus 49" or requested_ziehung == "sechs aus neun und vierzig"):
            l = fetch_lottozahlen()
            speech_output = "Die Ziehung sechs aus neunundvierzig vom " + l[0] + " lautet: " + l[1] + ",. Superzahl: " + `l[2]` + disclaimer
        elif(requested_ziehung == "Spiel siebenundsiebzig" or requested_ziehung == "spiel siebenundsiebzig" or requested_ziehung == "spiel 77" or requested_ziehung == "Spiel 77" or requested_ziehung == "Spiel sieben und siebzig" or requested_ziehung == "spiel sieben und siebzig"):
            l = fetch_lottozahlen()
            speech_output = "Am " + l[0] + " wurden im Spiel 77 folgende Zahlen gezogen: " + l[3] + disclaimer
        elif(requested_ziehung == "Super sechs" or requested_ziehung == "super sechs" or requested_ziehung == "super 6" or requested_ziehung == "Super 6"):
            l = fetch_lottozahlen()
            speech_output = "Das Ergebnis der Ziehung Super 6 vom " + l[0] + " lautet: " + l[4] + disclaimer
        else:
            speech_output = "Ziehung " + requested_ziehung + " nicht gefunden. Bitte probiere es noch einmal."
            should_end_session = False
        
        reprompt_text = "Bitte sag mir welche Ziehergebnisse du wünscht indem du zum Beispiel sagst, Lottozahlen Spiel siebenundsiebzig"
    else:
        l = fetch_lottozahlen()
        speech_output = "Die Lottozahlen vom " + l[0] + " lauten: " + l[1] + ",. Superzahl: " + `l[2]` + ",. Im Spiel 77 wurden folgende Zahlen gezogen: " + l[3] + ",. Hier die Ergebnisse der Ziehung Super 6: " + l[4] + disclaimer
        reprompt_text = "Bitte sag mir welche Ziehergebnisse du wünscht indem du zum Beispiel sagst, Lottozahlen sechs aus neunundvierzig"
    return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def fetch_lottozahlen():
    date = "unbekannt"
    lottozahlen = "unbekannt"
    superzahl = "unbekannt"
    spiel77 = "unbekannt"
    super6 = "unbekannt"

    response = urllib2.urlopen('https://ergebnisse.westlotto.com/wlinfo/WL_InfoService?client=frss&gruppe=Gewinnzahlen&spielart=LOTTO')
    html = response.read()

    #extract relevant information
    title_elements = re.findall(r'<title>.*</title>', html)
    date = title_elements[1][11:19]
    lottozahlen = re.findall(':.*:',title_elements[1])[0][2:-3]
    superzahl = int(re.findall('S:.*<',title_elements[1])[0][2:-1])
    spiel77 = title_elements[2][17:24]
    spiel77 = [i for i in spiel77]
    spiel77 = ', '.join(spiel77)
    super6 = title_elements[3][16:22]
    super6 = [i for i in super6]
    super6 = ', '.join(super6)
    return [date,lottozahlen,superzahl,spiel77,super6]
    

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_help_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetLottozahlen":
        return get_Lottozahlen(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])