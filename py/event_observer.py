
import json
import os
from persona.persona import Persona
from persona.prompt_template.prompt_structure import PromptStructure

class EventObserver:
    def __init__(self):
        self.personas = dict()
        # print(os.getcwd())
        with open("environment/meta.json") as json_file:
            meta = json.load(json_file)
        for persona_name in meta["persona_names"]:
            persona_folder = f"environment/persona/{persona_name}"
            self.personas[persona_name] = Persona(persona_name, persona_folder)

    def save(self):
        for persona_name, persona in self.personas.items():
            persona.save(f"environment/persona/{persona_name}")

    def observe(self, persona_name, event, day_type):
        #event["subject"] : "Isabella Rodriguez"
        #event["predicate"] : "be"
        #event["object"] : "regular"
        #event["description"] : "Isabella Rodriguez be regular"
        return self.personas[persona_name].receive_event(event, self.personas, day_type)



if __name__ == '__main__':
    persona_name = "Rick Novak"
    test_event = {
        "subject" : "bed",
        "predicate" : "is",
        "object" : "idle",
        "description": "idle" # "object의 state : e.g idle, unmade, used"
    }
    # test_event = {
    #     "subject" : "the Ville:Hobbs Cafe:cafe:table",
    #     "predicate" : "is",
    #     "object" : "burn",
    #     "description": "burn" # "object의 state : e.g idle, unmade, used"
    # }
    # test_event = {
    #     "subject" : "Klaus Mueller",
    #     "predicate" : "is",
    #     "object" : "idle",
    #     "description": "idle" # "object의 state : e.g idle, unmade, used"
    # }
    event_observer = EventObserver()
    PromptStructure.load_llama_7B_chat_hf("../../llama2chat7Bhf")
    PromptStructure.load_embedding_model()
    destination = event_observer.observe(persona_name, test_event, "First day")
    print(destination)