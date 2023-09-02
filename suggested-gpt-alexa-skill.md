```python
import logging
import json
import pymongo
import random
from datetime import datetime
from pymongo import MongoClient
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response
from ask_sdk_mongodb.adapter import MongoDbPersistenceAdapter

# Initializing the logger and setting the level to "INFO"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# MongoDB Connection
client = pymongo.MongoClient("mongodb+srv://samueloppong:51UVyecsZ3sLCOPC@cluster0.52xfihh.mongodb.net/?retryWrites=true&w=majority")
database = client["appointments"]
appointments_collection = database["patients"]

# Create the MongoDB Persistence Adapter
mongo_adapter = MongoDbPersistenceAdapter(
    collection_name="patients",
    client=client,  # Use the MongoDB client you created
)

# Intent Handlers
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

class AddNewBirthdayIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_intent_name("AddNewBirthdayIntent")(handler_input)
    
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

class SpecifyNameIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_intent_name("SpecifyNameIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        name = handler_input.request_envelope.request.intent.slots["NameSlot"].value
        session_attributes["name"] = name
        
        speech_output = random.choice(language_prompts["ASK_DOB"]).format(name)
        reprompt = random.choice(language_prompts["ASK_DOB_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

class SpecifyBirthdayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SpecifyBirthdayIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        date_of_birth = handler_input.request_envelope.request.intent.slots["DOBSlot"].value
        name = session_attributes["name"]
        
        # Save persistent attribute
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        persistent_attributes[name] = date_of_birth
        handler_input.attributes_manager.save_persistent_attributes()
        
        # Create a dictionary to store the data you want to insert into MongoDB
        data = {
            "name": name,
            "date_of_birth": date_of_birth
        }

        # Insert the data into the MongoDB collection
        appointments_collection.insert_one(data)
        logger.info("Birthday added to MongoDB: %s", data)
        
        speech_output = random.choice(language_prompts["BIRTHDAY_SAVED"])
        reprompt = random.choice(language_prompts["BIRTHDAY_SAVED_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

class CheckBirthdayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CheckBirthdayIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        name = handler_input.request_envelope.request.intent.slots["PersonNameSlot"].value
        date_of_birth = persistent_attributes.get(name, "").split('-', 1)[1]
        
        speech_output = random.choice(language_prompts["TELL_DOB"]).format(name, date_of_birth)
        reprompt = random.choice(language_prompts["TELL_DOB_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

class NextBirthdayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("NextBirthdayIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        nearest_birthday_name = ""
        nearest_birthday_days = 0
        todays_date = datetime.now()
        current_year = datetime.today().year
        name_list = persistent_attributes.keys()
        
        for name in name_list:
            date_of_birth = datetime.strptime(persistent_attributes[name], "%Y-%m-%d")
            birthday_this_year = date_of_birth.replace(year=current_year)
            birthday_next_year = date_of_birth.replace(year=current_year + 1)
            
            if birthday_this_year > todays_date:
                no_of_days = (birthday_this_year - todays_date).days
            else:
                no_of_days = (birthday_next_year - todays_date).days
            
            if nearest_birthday_days == 0:
                nearest_birthday_days = no_of_days
                nearest_birthday_name = name
            elif no_of_days < nearest_birthday_days:
                nearest_birthday_days = no_of_days
                nearest_birthday_name = name
        
        speech_output = random.choice(language_prompts["TELL_NEAREST_DOB"]).format(nearest_birthday_name, nearest_birthday_days)
        reprompt = random.choice(language_prompts["TELL_NEAREST_DOB_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

class DeleteAllBirthdaysIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("DeleteAllBirthdaysIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        # Clear persistent attributes
        handler_input.attributes_manager.delete_persistent_attributes()
        
        speech_output = random.choice(language_prompts["DELETE_ALL"])
        reprompt = random.choice(language_prompts["DELETE_ALL_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

class DeleteSpecificBirthdayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("DeleteSpecificBirthdayIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        name = handler_input.request_envelope.request.intent.slots["DeleteNameSlot"].value
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

class RepeatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)
    
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

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["CANCEL_STOP_RESPONSE"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .set_should_end_session(True)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
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

# This handler handles utterances that can't be matched to any other intent handler.
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
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

class SessionEndedRequesthandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Session ended with the reason: %s", handler_input.request_envelope.request.reason)
        return handler_input.response_builder.response

# Exception Handlers
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

# Interceptors
class RequestLogger(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.debug("Alexa Request: %s", handler_input.request_envelope.request)

class ResponseLogger(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        logger.debug("Alexa Response: %s", response)

class LocalizationInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is %s", locale)
        
        try:
            with open("languages/" + str(locale) + ".json") as language_data:
                language_prompts = json.load(language_data)
        except:
            with open("languages/" + str(locale[:2]) + ".json") as language_data:
                language_prompts = json.load(language_data)
        
        handler_input.attributes_manager.request_attributes["_"] = language_prompts

class RepeatInterceptor(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes["repeat_speech_output"] = response.output_speech.ssml.replace("<speak>", "").replace("</speak>", "")
        try:
            session_attributes["repeat_reprompt"] = response.reprompt.output_speech.ssml.replace("<speak>", "").replace("</speak>", "")
        except:
            session_attributes["repeat_reprompt"] = response.output_speech.ssml.replace("<speak>", "").replace("</speak>", "")

# Skill Builder
sb = SkillBuilder(persistence_adapter=mongo_adapter)

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AddNewBirthdayIntentHandler())
sb.add_request_handler(SpecifyNameIntentHandler())
sb.add_request_handler(SpecifyBirthdayIntentHandler())
sb.add_request_handler(CheckBirthdayIntentHandler())
sb.add_request_handler(NextBirthdayIntentHandler())
sb.add_request_handler(DeleteSpecificBirthdayIntentHandler())
sb.add_request_handler(DeleteAllBirthdaysIntentHandler())
sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequesthandler())

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_response_interceptor(RepeatInterceptor())
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()
```
