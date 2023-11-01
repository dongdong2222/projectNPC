

class Retrieve:
    def __init__(self):
        pass

    @staticmethod
    def retrieve(persona, perceived):
        retrieved = dict()
        for event in perceived:
            retrieved[event.description] = dict()
            retrieved[event.description]["curr_event"] = event

            relevant_events = persona.a_mem.retrieve_relevant_event(
                event.subject, event.predicate, event.object)
            retrieved[event.description]["events"] = list(relevant_events)

            relevant_thoughts = persona.a_mem.retrieve_relevant_thoughts(
                event.subject, event.predicate, event.object)
            retrieved[event.description]["thoughts"] = list(relevant_thoughts)

        return retrieved

    @staticmethod
    def retrieve_with_focal(persona, focal_points, n_count=30):
        pass