

```python

import logging
import json
import pymongo
import random
import requests
from ask_sdk_model.dialog import ElicitSlotDirective
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
                
                
 #Add New Patient Intent Block
 # add a new birthday
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


 # Specify Patient First Name Intent Handler
 # his name is John
class SpecifyPatientNameIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_intent_name("SpecifyPatientNameIntent")(handler_input)

    def handle(self, handler_input):
        try:
            first_name = handler_input.request_envelope.request.intent.slots["PatientNameSlot"].value

            # Store the first name in the session
            handler_input.attributes_manager.session_attributes["first_name"] = first_name

            speak_output = f"Thank you, {first_name}. Your first name has been stored in the session. You can now specify the day, month and year."
            # Include a line to reveal what is stored in the session
            speak_output += f" Just to confirm, your first name in the session is {first_name}."

        except Exception as e:
            logger.error("Error storing first name in session: %s", str(e))
            speak_output = "Sorry, there was an issue storing your first name. Please try again later."
            reprompt_text = "I am called Tiacloud.io, what is your first name?" #added reprompt to help insertion of data

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


# Specify Patient Date of Birth Intent Handler
# his date of birth is 17th March 1981
class SpecifyPatientBirthdayIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("SpecifyPatientBirthdayIntent")(handler_input)

    def handle(self, handler_input):
        try:
            day = handler_input.request_envelope.request.intent.slots["day"].value
            month = handler_input.request_envelope.request.intent.slots["month"].value
            year = handler_input.request_envelope.request.intent.slots["year"].value

            date_of_birth = f"{day}-{month}-{year}"

            first_name = handler_input.attributes_manager.session_attributes.get("first_name")

            if first_name:
                # Insert the first name and date of birth into MongoDB
                appointments_collection.insert_one({"first_name": first_name, "date_of_birth": date_of_birth})
                
                speak_output = f"Thank you, {first_name}. Your date of birth ({date_of_birth}) has been added to the collection."
            else:
                speak_output = "Sorry, I couldn't find your first name in the session. Please specify your first name first."

        except Exception as e:
            logger.error("Error inserting data into MongoDB: %s", str(e))
            speak_output = "Sorry, there was an issue saving your data. Please try again later."

        return (
            handler_input.response_builder
            .speak(speak_output)
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
        
        
 # Check Patient Date of Birth Intent Handler 
 # what is the birthday of {ExistingPatientNameSlot}
class CheckPatientBirthdayIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("CheckPatientBirthdayIntent")(handler_input)

    def handle(self, handler_input):
        try:
            # Retrieve the first name from the user's input
            first_name = handler_input.request_envelope.request.intent.slots["ExistingPatientNameSlot"].value
            # Query the database to find the patient's date of birth
            patient_data = appointments_collection.find_one({"first_name": first_name})

            if patient_data:
                date_of_birth = patient_data.get("date_of_birth")
                if date_of_birth:
                    speak_output = f"The date of birth for {first_name} is {date_of_birth}."
                else:
                    speak_output = f"Sorry, the date of birth for {first_name} is not available."
            else:
                speak_output = f"Sorry, I couldn't find a patient with the name {first_name} in the database."

        except Exception as e:
            logger.error("Error querying the database: %s", str(e))
            speak_output = "Sorry, there was an issue retrieving the date of birth. Please try again later."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )




# Next Birthday Intent Handler
# Who has the next birthday?
class NextPatientBirthdayIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("NextPatientBirthdayIntent")(handler_input)

    def handle(self, handler_input):
        try:
            # Query the database to find the next upcoming birthday
            today = datetime.date.today()
            next_birthday = appointments_collection.find_one(
                {"date_of_birth": {"$gte": today.strftime("%d-%m")}},
                sort=[("date_of_birth", 1)]
            )

            if next_birthday:
                first_name = next_birthday.get("first_name")
                date_of_birth = next_birthday.get("date_of_birth")
                speak_output = f"The next birthday is for {first_name} on {date_of_birth}."
            else:
                speak_output = "There are no upcoming birthdays in the database."

        except Exception as e:
            logger.error("Error querying the database: %s", str(e))
            speak_output = "Sorry, there was an issue retrieving the next birthday. Please try again later."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )



# DeleteSpecificPatientBirthday Intent Handler
# remove ernest from database
class DeleteSpecificPatientBirthdayIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("DeleteSpecificPatientBirthdayIntent")(handler_input)

    def handle(self, handler_input):
        try:
            # Retrieve the first name from the user's input
            first_name = handler_input.request_envelope.request.intent.slots["DeletePatientNameSlot"].value

            # Check if the patient with the specified first name exists in the database
            patient_data = appointments_collection.find_one({"first_name": first_name})

            if patient_data:
                # Delete the patient's record from the database
                appointments_collection.delete_one({"first_name": first_name})
                speak_output = f"The birthday record for {first_name} has been deleted."
            else:
                speak_output = f"Sorry, there is no patient with the name {first_name} in the database."

        except Exception as e:
            logger.error("Error deleting specific patient birthday: %s", str(e))
            speak_output = "Sorry, there was an issue deleting the patient birthday. Please try again later."

        return handler_input.response_builder.speak(speak_output).response


# DeleteAllPatientBirthdays Intent Handler
class DeleteAllPatientBirthdaysIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("DeleteAllPatientBirthdaysIntent")(handler_input)

    def handle(self, handler_input):
        try:
            # Delete all patient records from the database
            appointments_collection.delete_many({})

            speak_output = "All patient birthdays have been deleted from the database."
        except Exception as e:
            logger.error("Error deleting all patient birthdays: %s", str(e))
            speak_output = "Sorry, there was an issue deleting patient birthdays. Please try again later."

        return handler_input.response_builder.speak(speak_output).response



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

```



![image](https://github.com/expertcloudconsultant/alexa-skill/assets/69172523/37fe054d-9b33-4cb0-9a2b-e39e1b31fccb)


![dbs-create](https://github.com/expertcloudconsultant/alexa-skill/assets/69172523/c3cc7c04-7ead-4054-a00b-df767490b709)


