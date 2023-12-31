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
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        name = handler_input.request_envelope.request.intent.slots["PatientNameSlot"].value
        dob = handler_input.request_envelope.request.intent.slots["DOBSlot"].value
        
        # Insert the patient data into MongoDB
        appointments_collection.insert_one({"name": name, "dob": dob})
        
        session_attributes["name"] = name
        session_attributes["dob"] = dob
        
        speech_output = random.choice(language_prompts["INSERT_DOB"]).format(name)
        reprompt = random.choice(language_prompts["INSERT_DOB_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

# Another Intent Handler to handle cases when name is not in database
class HandleNotInDatabaseIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return (
            is_intent_name("HandleNotInDatabaseIntent")(handler_input) and
            "name" not in handler_input.attributes_manager.session_attributes
        )

    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = random.choice(language_prompts["NOT_IN_DATABASE"]).format(
            handler_input.attributes_manager.session_attributes["name"]
        )
        
        return handler_input.response_builder.speak(speech_output).response


# SpecifyPatientBirthday Intent Handler
class SpecifyPatientBirthdayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SpecifyPatientBirthdayIntent")(handler_input)
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        date_of_birth = handler_input.request_envelope.request.intent.slots["PatientDOBSlot"].value
        name = session_attributes["name"]
        
        # Save data to MongoDB
        appointments_collection.update_one({"name": name}, {"$set": {"date_of_birth": date_of_birth}}, upsert=True)
        
        speech_output = random.choice(language_prompts["BIRTHDAY_STORED"])
        reprompt = random.choice(language_prompts["BIRTHDAY_STORED_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

# CheckPatientBirthday Intent Handler
class CheckPatientBirthdayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and handler_input.request_envelope.request.intent.name == "CheckPatientBirthdayIntent"
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        name = handler_input.request_envelope.request.intent.slots["ExistingPatientNameSlot"].value
        
        # Retrieve data from MongoDB
        patient_data = appointments_collection.find_one({"name": name})
        
        if patient_data:
            date_of_birth = patient_data["date_of_birth"]
            speech_output = random.choice(language_prompts["ANNOUNCE_DOB"]).format(name, date_of_birth)
            reprompt = random.choice(language_prompts["ANNOUNCE_DOB_REPROMPT"])
        else:
            speech_output = random.choice(language_prompts["UNKNOWN_PATIENT"]).format(name)
            reprompt = random.choice(language_prompts["UNKNOWN_PATIENT_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

# NextPatientBirthday Intent Handler
class NextPatientBirthdayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and handler_input.request_envelope.request.intent.name == "NextPatientBirthdayIntent"
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        nearest_appointment_name = ""
        nearest_appointment_days = 0
        todays_date = datetime.now()
        current_year = datetime.today().year
        name_list = persistent_attributes.keys()
        
        for name in name_list:
            date_of_birth = datetime.strptime(persistent_attributes[name], "%Y-%m-%d")
            appointment_this_year = date_of_birth.replace(year=current_year)
            appointment_next_year = date_of_birth.replace(year=current_year + 1)
            
            if appointment_this_year > todays_date:
                no_of_days = (appointment_this_year - todays_date).days
            else:
                no_of_days = (appointment_next_year - todays_date).days
            
            if nearest_appointment_days == 0:
                nearest_appointment_days = no_of_days
                nearest_appointment_name = name
            elif no_of_days < nearest_appointment_days:
                nearest_appointment_days = no_of_days
                nearest_appointment_name = name
        
        speech_output = random.choice(language_prompts["ANNOUNCE_CLOSEST_DOB"]).format(nearest_appointment_name, nearest_appointment_days)
        reprompt = random.choice(language_prompts["ANNOUNCE_CLOSEST_DOB_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

# DeleteAllPatientBirthdays Intent Handler
class DeleteAllPatientBirthdaysIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and handler_input.request_envelope.request.intent.name == "DeleteAllPatientBirthdaysIntent"
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        handler_input.attributes_manager.delete_persistent_attributes()
        
        speech_output = random.choice(language_prompts["DELETE_DB"])
        reprompt = random.choice(language_prompts["DELETE_DB_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

# DeleteSpecificPatientBirthday Intent Handler
class DeleteSpecificPatientBirthdayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and handler_input.request_envelope.request.intent.name == "DeleteSpecificPatientBirthdayIntent"
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        name = handler_input.request_envelope.request.intent.slots["DeletePatientNameSlot"].value
        persistent_attributes.pop(name, None)
        handler_input.attributes_manager.save_persistent_attributes()
        
        speech_output = random.choice(language_prompts["DELETE_SPECIFIC"]).format(name)
        reprompt = random.choice(language_prompts["DELETE_SPECIFIC_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

# Repeat Intent Handler
class RepeatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and handler_input.request_envelope.request.intent.name == "AMAZON.RepeatIntent"
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        repeat_speech_output = session_attributes["repeat_speech_output"]
        repeat_reprompt = session_attributes["repeat_reprompt"]
        
        speech_output = random.choice(language_prompts["REPEAT"]).format(repeat_speech_output)
        reprompt = random.choice(language_prompts["REPEAT_REPROMPT"]).format(repeat_reprompt)
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

# Cancel or Stop Intent Handler
class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.type == "IntentRequest" and
                (handler_input.request_envelope.request.intent.name == "AMAZON.CancelIntent" or
                 handler_input.request_envelope.request.intent.name == "AMAZON.StopIntent"))
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = random.choice(language_prompts["GOODBYE"])
        return handler_input.response_builder.speak(speech_output).response

# Help Intent Handler
class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and handler_input.request_envelope.request.intent.name == "AMAZON.HelpIntent"
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = random.choice(language_prompts["HELP"])
        reprompt = random.choice(language_prompts["HELP_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

# Fallback Intent Handler
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and handler_input.request_envelope.request.intent.name == "AMAZON.FallbackIntent"
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = random.choice(language_prompts["FALLBACK"])
        reprompt = random.choice(language_prompts["FALLBACK_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

# Session Ended Request Handler
class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "SessionEndedRequest"
    
    def handle(self, handler_input):
        logger.info("Session ended with the reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response

# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = language_prompts["ERROR"]
        reprompt = language_prompts["ERROR_REPROMPT"]
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )
        
 # Request Interceptor to Load Language Prompts
class LocalizationInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        try:
            with open(f"languages/{locale}.json") as language_data:
                language_prompts = json.load(language_data)
        except:
            with open(f"languages/{locale[:2]}.json") as language_data:
                language_prompts = json.load(language_data)
        handler_input.attributes_manager.request_attributes["_"] = language_prompts

# Response Interceptor to Store Repeat Speech
class RepeatInterceptor(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes["repeat_speech_output"] = response.output_speech.ssml.replace("<speak>", "").replace("</speak>", "")
        try:
            session_attributes["repeat_reprompt"] = response.reprompt.output_speech.ssml.replace("<speak>", "").replace("</speak>", "")
        except:
            session_attributes["repeat_reprompt"] = response.output_speech.ssml.replace("<speak>", "").replace("</speak>", "")
            

# Skill Builder
sb = SkillBuilder()

# Adding Handlers to Skill Builder
sb.add_request_handler(LaunchRequestHandler())

sb.add_request_handler(AddNewPatientIntentHandler())
sb.add_request_handler(SpecifyPatientNameIntentHandler())
sb.add_request_handler(SpecifyPatientBirthdayIntentHandler())
sb.add_request_handler(HandleNotInDatabaseIntentHandler())
sb.add_request_handler(CheckPatientBirthdayIntentHandler())
sb.add_request_handler(NextPatientBirthdayIntentHandler())
sb.add_request_handler(DeleteAllPatientBirthdaysIntentHandler())
sb.add_request_handler(DeleteSpecificPatientBirthdayIntentHandler())


sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Adding Exception Handler
sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_response_interceptor(RepeatInterceptor())

# Lambda Handler
lambda_handler = sb.lambda_handler()
