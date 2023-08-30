
Sure, I've adapted the code to use MongoDB instead of DynamoDB for persistence. Note that you would need to set up a MongoDB database and provide the appropriate connection details (such as the URI) in the code. Here's the modified code:

```python
# ... (other import statements)

from pymongo import MongoClient
from datetime import datetime

# ... (other code)

# Defining the MongoDB connection
mongodb_uri = "YOUR_MONGODB_URI"  # Replace this with your MongoDB URI
client = MongoClient(mongodb_uri)
db = client.get_database()

# ... (other code)

class SpecifyBirthdayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SpecifyBirthdayIntent")(handler_input)
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        date_of_birth = handler_input.request_envelope.request.intent.slots["DOBSlot"].value
        name = session_attributes["name"]
        
        # Save data to MongoDB
        db.birthday_collection.update_one(
            {"_id": name},
            {"$set": {"date_of_birth": date_of_birth}},
            upsert=True
        )
        
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
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        name = handler_input.request_envelope.request.intent.slots["PersonNameSlot"].value
        
        # Retrieve data from MongoDB
        person = db.birthday_collection.find_one({"_id": name})
        
        if person:
            date_of_birth = person["date_of_birth"]
            speech_output = random.choice(language_prompts["TELL_DOB"]).format(name, date_of_birth)
            reprompt = random.choice(language_prompts["TELL_DOB_REPROMPT"])
        else:
            speech_output = random.choice(language_prompts["PERSON_NOT_FOUND"]).format(name)
            reprompt = random.choice(language_prompts["PERSON_NOT_FOUND_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
        )

# ... (other intent handlers)

# Skill Builder
# Define a skill builder instance and add all the request handlers,
# exception handlers and interceptors to it.

sb = CustomSkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AddNewBirthdayIntentHandler())
sb.add_request_handler(SpecifyNameIntentHandler())
sb.add_request_handler(SpecifyBirthdayIntentHandler())
sb.add_request_handler(CheckBirthdayIntentHandler())
# ... (add other request handlers)

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_response_interceptor(RepeatInterceptor())
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()
```

Please replace `"YOUR_MONGODB_URI"` with the actual MongoDB URI you're using for your database. Also, make sure you have the necessary libraries installed (`pymongo` in this case) before running the code.
