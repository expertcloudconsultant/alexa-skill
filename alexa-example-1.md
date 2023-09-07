Certainly! Below is the updated code for your Alexa skill that allows you to store patient information and schedules in MongoDB. Please note that this code assumes you have already set up the necessary MongoDB connection and have the appropriate MongoDB schema for storing patient information and schedules.

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
from ask_sdk_model import Response

# Configure the MongoDB connection
client = pymongo.MongoClient("mongodb+srv://your_username:your_password@your_cluster_url/your_database_name")
database = client["appointments"]
appointments_collection = database["patients"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sb = SkillBuilder()

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "LaunchRequest"

    def handle(self, handler_input):
        speech_output = "Welcome to the appointment scheduler. How can I assist you today?"
        reprompt = "You can add a new patient or schedule an appointment. What would you like to do?"
        return (
            handler_input.response_builder
            .speak(speech_output)
            .ask(reprompt)
            .response
        )

class AddPatientIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and \
               handler_input.request_envelope.request.intent.name == "AddPatientIntent"

    def handle(self, handler_input):
        first_name = handler_input.request_envelope.request.intent.slots["PatientNameSlot"].value
        date_of_birth = handler_input.request_envelope.request.intent.slots["DateOfBirthSlot"].value

        try:
            # Store patient information in MongoDB
            appointments_collection.insert_one({
                "first_name": first_name,
                "date_of_birth": date_of_birth,
                "schedules": []  # Initialize an empty list for schedules
            })

            speech_output = f"Thank you, {first_name}. Your information has been stored."
        except Exception as e:
            logger.error("Error adding patient to MongoDB: %s", str(e))
            speech_output = "Sorry, there was an issue adding the patient. Please try again later."

        return handler_input.response_builder.speak(speech_output).response

class AddScheduleIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and \
               handler_input.request_envelope.request.intent.name == "AddScheduleIntent"

    def handle(self, handler_input):
        first_name = handler_input.request_envelope.request.intent.slots["PatientNameSlot"].value
        schedule_name = handler_input.request_envelope.request.intent.slots["ScheduleNameSlot"].value
        schedule_time = handler_input.request_envelope.request.intent.slots["ScheduleTimeSlot"].value

        try:
            # Check if the patient exists in MongoDB
            patient_data = appointments_collection.find_one({"first_name": first_name})

            if patient_data:
                # Update the patient's schedules
                appointments_collection.update_one(
                    {"first_name": first_name},
                    {"$push": {"schedules": {"name": schedule_name, "time": schedule_time}}}
                )

                speech_output = f"Thank you, {first_name}. The schedule {schedule_name} at {schedule_time} has been added."
            else:
                speech_output = f"Sorry, I couldn't find a patient with the name {first_name}. Please add the patient first."

        except Exception as e:
            logger.error("Error adding schedule to MongoDB: %s", str(e))
            speech_output = "Sorry, there was an issue adding the schedule. Please try again later."

        return handler_input.response_builder.speak(speech_output).response

# Add other intent handlers here for checking schedules, listing patients, etc.

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speech_output = "Sorry, there was an error. Please try again later."
        return (
            handler_input.response_builder
            .speak(speech_output)
            .response
        )

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AddPatientIntentHandler())
sb.add_request_handler(AddScheduleIntentHandler())
# Add other intent handlers here

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
```

This code includes handlers for adding patients and schedules, as well as exception handling. You can add more intent handlers for checking schedules, listing patients, and any other functionality you need. Make sure to replace `"your_username"`, `"your_password"`, `"your_cluster_url"`, and `"your_database_name"` with your actual MongoDB credentials and database information.

Remember to update your interaction model in the Alexa Developer Console to include the new intents and slots. Once you've made these changes, you can test your skill with Alexa to ensure it works as expected.





Sure, here are some sample utterances that you can use in your interaction model for the intents related to adding patients and schedules:

**AddPatientIntent:**
- "Add a new patient"
- "I want to add a new patient"
- "Register a new patient named {PatientNameSlot} with date of birth {DateOfBirthSlot}"
- "Record a new patient named {PatientNameSlot} born on {DateOfBirthSlot}"

**AddScheduleIntent:**
- "Add a schedule for {PatientNameSlot}"
- "Schedule an appointment for {PatientNameSlot}"
- "Create a new schedule for {PatientNameSlot} with name {ScheduleNameSlot} at {ScheduleTimeSlot}"
- "Schedule {ScheduleNameSlot} for {PatientNameSlot} at {ScheduleTimeSlot}"

You should include variations of these utterances to improve the recognition accuracy of your skill. Additionally, you can add more specific examples based on your target user scenarios.


