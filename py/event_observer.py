
import json

from persona.persona import Persona

class EventObserver:
    def __init__(self):
        self.personas = dict()

        with open("environment/meta.json") as json_file:
            meta = json.load(json_file)
        for persona_name in meta["persona_names"]:
            persona_folder = f"environment/persona/{persona_name}"
            self.personas[persona_name] = Persona(persona_name, persona_folder)

    def save(self):
        for persona_name, persona in self.personas.items():
            persona.save(f"environment/persona/{persona_name}")

    def observe(self, persona_name, event):
        #event["subject"] : "Isabella Rodriguez"
        #event["predicate"] : "be"
        #event["object"] : "regular"
        #event["description"] : "Isabella Rodriguez is a regular at Hobbs Cafe"
        self.personas[persona_name].receive_event(event)



if __name__ == '__main__':
    test_event = {
        "subject" : "Isabella Rodriguez",
        "predicate" : "be",
        "object" : "regular",
        "description" : "Isabella Rodriguez is a regular at Hobbs Cafe"
    }
    event_observer = EventObserver()
    event_observer.observe("Isabella Rodriguez", test_event)

    print("done")