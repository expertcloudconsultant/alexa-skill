class SpecifyPatientNameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SpecifyPatientNameIntent")(handler_input)

    def handle(self, handler_input):
        try:
            name = handler_input.request_envelope.request.intent.slots["PatientNameSlot"].value
        except:
            name = None

        try:
            dob = handler_input.request_envelope.request.intent.slots["PatientDOBSlot"].value
        except:
            dob = None

        if name and dob:
            # Both name and date of birth are provided
            appointments_collection.insert_one({"name": name, "dob": dob})
            speak_output = f"Thank you, {name}. Your name and date of birth {dob} have been added to the collection."
        elif name:
            # Only name is provided
            speak_output = f"Thank you, {name}. Please also provide your date of birth."
        elif dob:
            # Only date of birth is provided
            speak_output = "Thank you for providing your date of birth. Please also provide your name."
        else:
            # Neither name nor date of birth is provided
            speak_output = "Sorry, I couldn't understand your response. Please provide your name and date of birth."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )
