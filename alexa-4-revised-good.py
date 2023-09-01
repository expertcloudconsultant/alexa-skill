import logging
import json
import pymongo
import random
import requests
from datetime import datetime
from pymongo import MongoClient
#import ask_sdk_core.utils as ask_utils
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


 # MongoDB Connection
client = pymongo.MongoClient("mongodb+srv://samueloppong:51UVyecsZ3sLCOPC@cluster0.52xfihh.mongodb.net/?retryWrites=true&w=majority")
database = client["appointments"]
appointments_collection = database["patients"]

 #Original LaunchRequestHandler
class LaunchRequestHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        skill_name = language_prompts["SKILL_NAME"]
        
        speech_output = random.choice(language_prompts["GREETING"]).format(skill_name)
        reprompt = random.choice(language_prompts["GREETING_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
                )
 
 #Add New Patient
class AddNewPatientIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_intent_name("AddNewPatientIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        
        speech_output = random.choice(language_prompts["ASK_NAME"])
        reprompt = random.choice(language_prompts["ASK_NAME_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
                )
 

 # SpecifyPatientName Intent Handler
class SpecifyPatientNameIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_intent_name("SpecifyPatientNameIntent")(handler_input)

    def handle(self, handler_input):
        try:
            name = handler_input.request_envelope.request.intent.slots["PatientNameSlot"].value
            appointments_collection.insert_one({"name": name})

            speak_output = f"Thank you, {name}. Your name has been added to the collection."
        except Exception as e:
            logger.error("Error inserting name into MongoDB: %s", str(e))
            speak_output = "Sorry, there was an issue saving your name. Please try again later."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )
