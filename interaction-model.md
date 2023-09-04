```json
{
    "interactionModel": {
        "languageModel": {
            "invocationName": "stored appointments",
            "intents": [
                {
                    "name": "AMAZON.CancelIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.HelpIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.StopIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.NavigateHomeIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.FallbackIntent",
                    "samples": []
                },
                {
                    "name": "AddNewPatientIntent",
                    "slots": [],
                    "samples": [
                        "add a new birthday",
                        "I want to add a new birthday",
                        "add a birthday entry to the skill",
                        "add new birthday"
                    ]
                },
                {
                    "name": "SpecifyPatientNameIntent",
                    "slots": [
                        {
                            "name": "PatientNameSlot",
                            "type": "AMAZON.FirstName"
                        },
                        {
                            "name": "DOBSlot",
                            "type": "AMAZON.DATE"
                        }
                    ],
                    "samples": [
                        "{PatientNameSlot}",
                        "he is called {PatientNameSlot} and date of birth is {DOBSlot}",
                        "She is called {PatientNameSlot}",
                        "He is called {PatientNameSlot}",
                        "The patient's name is {PatientNameSlot}",
                        "The patient is called {PatientNameSlot}"
                    ]
                },
                {
                    "name": "SpecifyPatientBirthdayIntent",
                    "slots": [
                        {
                            "name": "PatientDOBSlot",
                            "type": "AMAZON.FirstName"
                        },
                        {
                            "name": "day",
                            "type": "AMAZON.Ordinal"
                        },
                        {
                            "name": "month",
                            "type": "AMAZON.Month"
                        },
                        {
                            "name": "year",
                            "type": "AMAZON.FOUR_DIGIT_NUMBER"
                        }
                    ],
                    "samples": [
                        "she was born on {day} {month} {year}",
                        "he was born on {day} {month} {year}",
                        "his date of birth is {day} {month} {year}",
                        "{year} {month} {day}",
                        "{day} {month} {year}",
                        "her date of birth is {day} {month} {year}",
                        "my date of birth is {PatientDOBSlot}",
                        "I was born on {PatientDOBSlot}",
                        "{PatientDOBSlot} is my date of birth",
                        "{PatientDOBSlot} is when I was born",
                        "born on {PatientDOBSlot}",
                        "His date of birth is {PatientDOBSlot}",
                        "he was born on {PatientDOBSlot}",
                        "her date of birth is {PatientDOBSlot}",
                        "she was born on {PatientDOBSlot}",
                        "the date of birth is {PatientDOBSlot}",
                        "{PatientDOBSlot}"
                    ]
                },
                {
                    "name": "CheckPatientBirthdayIntent",
                    "slots": [
                        {
                            "name": "ExistingPatientNameSlot",
                            "type": "AMAZON.FirstName"
                        }
                    ],
                    "samples": [
                        "when is {ExistingPatientNameSlot} birthday",
                        "when is the birthday of {ExistingPatientNameSlot}",
                        "{ExistingPatientNameSlot}"
                    ]
                },
                {
                    "name": "NextPatientBirthdayIntent",
                    "slots": [],
                    "samples": [
                        "Whose birthday is coming up next",
                        "tell me about the upcoming birthday",
                        "whose birthday is next",
                        "when is the next birthday coming up",
                        "next birthday"
                    ]
                },
                {
                    "name": "DeleteAllBirthdaysIntent",
                    "slots": [],
                    "samples": [
                        "delete all birthdays",
                        "delete all the birthdays",
                        "delete all birthdays from the database",
                        "delete all birthday records from mongodb"
                    ]
                },
                {
                    "name": "DeleteSpecificPatientBirthdayIntent",
                    "slots": [
                        {
                            "name": "DeletePatientNameSlot",
                            "type": "AMAZON.FirstName"
                        }
                    ],
                    "samples": [
                        "delete {DeletePatientNameSlot} birthday",
                        "delete {DeletePatientNameSlot} birhtday record",
                        "delete the birthday record of {DeletePatientNameSlot}",
                        "remove {DeletePatientNameSlot} birthday from the database"
                    ]
                },
                {
                    "name": "HandleNotInDatabaseIntent",
                    "slots": [],
                    "samples": []
                }
            ],
            "types": []
        },
        "dialog": {
            "intents": [
                {
                    "name": "SpecifyPatientBirthdayIntent",
                    "confirmationRequired": false,
                    "prompts": {},
                    "slots": [
                        {
                            "name": "PatientDOBSlot",
                            "type": "AMAZON.FirstName",
                            "confirmationRequired": false,
                            "elicitationRequired": true,
                            "prompts": {
                                "elicitation": "Elicit.Slot.1123561900187.1331370658578"
                            }
                        },
                        {
                            "name": "day",
                            "type": "AMAZON.Ordinal",
                            "confirmationRequired": false,
                            "elicitationRequired": true,
                            "prompts": {
                                "elicitation": "Elicit.Slot.1123561900187.757187064863"
                            }
                        },
                        {
                            "name": "month",
                            "type": "AMAZON.Month",
                            "confirmationRequired": false,
                            "elicitationRequired": true,
                            "prompts": {
                                "elicitation": "Elicit.Slot.1123561900187.1355488942108"
                            }
                        },
                        {
                            "name": "year",
                            "type": "AMAZON.FOUR_DIGIT_NUMBER",
                            "confirmationRequired": false,
                            "elicitationRequired": true,
                            "prompts": {
                                "elicitation": "Elicit.Slot.1123561900187.36480736714"
                            }
                        }
                    ]
                }
            ],
            "delegationStrategy": "ALWAYS"
        },
        "prompts": [
            {
                "id": "Elicit.Slot.1123561900187.1331370658578",
                "variations": [
                    {
                        "type": "PlainText",
                        "value": "and the date of birth of the patient is"
                    },
                    {
                        "type": "PlainText",
                        "value": "what is the date of birth of the patient"
                    }
                ]
            },
            {
                "id": "Elicit.Slot.1123561900187.757187064863",
                "variations": [
                    {
                        "type": "PlainText",
                        "value": "and the {day} is"
                    },
                    {
                        "type": "PlainText",
                        "value": "which {day}"
                    },
                    {
                        "type": "PlainText",
                        "value": "and the day is"
                    },
                    {
                        "type": "PlainText",
                        "value": "what day is it again"
                    }
                ]
            },
            {
                "id": "Elicit.Slot.1123561900187.1355488942108",
                "variations": [
                    {
                        "type": "PlainText",
                        "value": "which {month} "
                    },
                    {
                        "type": "PlainText",
                        "value": "specify the {month} please"
                    },
                    {
                        "type": "PlainText",
                        "value": "what {month}"
                    }
                ]
            },
            {
                "id": "Elicit.Slot.1123561900187.36480736714",
                "variations": [
                    {
                        "type": "PlainText",
                        "value": "what is the {year}"
                    },
                    {
                        "type": "PlainText",
                        "value": "which {year}"
                    }
                ]
            }
        ]
    }
}
```
