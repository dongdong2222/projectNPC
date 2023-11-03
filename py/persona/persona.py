
from persona.memory_structure.spatial_memory import SpatialMemory
from persona.memory_structure.associative_memory import AssociativeMemory
from persona.memory_structure.scratch import Scratch

from persona.cognitive_module.perceive import Perceive
from persona.cognitive_module.retrieve import Retrieve
from persona.cognitive_module.plan import Plan

class Persona:
    def __init__(self, name, f_memory_saved=False):
        #name : full name of persona , unique identifier for persona whitin Reverie
        self.name = name
        self.s_mem = SpatialMemory(f"{f_memory_saved}/spatial_memory.json")
        self.a_mem = AssociativeMemory(f"{f_memory_saved}/associative_memory")
        self.scratch = Scratch(f"{f_memory_saved}/scratch.json")

    def save(self, save_folder):
        self.s_mem.save(f"{save_folder}/spatial_memory.json")
        self.a_mem.save(f"{save_folder}/associative_memory")
        self.scratch.save(f"{save_folder}/scratch.json")
    def receive_event(self, event, personas):
        # 임시 변수 : new_day : False, First day, New day
        new_day = "First_day"


        # event 발생 시 호출
        perceived = self.perceive(event)
        retrieved = self.retrieve(perceived)
        plan = self.plan(personas, new_day, retrieved)
        # TODO : self.reflect()
        # TODO : return self.execute(plan)

    def perceive(self, event):
        return Perceive.perceive(self, event)
        pass

    def retrieve(self, perceived):
        '''
        INPUT:
            perceive:   a list of <ConceptNode> that are perceived and new.
        OUTPUT:
            retrieved:  dictionary of dictionary. The first layer specifies an event,
                        while the latter layer specifies the "curr_event", "events",
                        and "thoughts" that are relevant.
        '''
        return Retrieve.retrieve(self, perceived)


    def plan(self, personas, new_day, retrieve):
        return Plan.plan(self, personas, new_day, retrieve)

    def execute(self, plan):
        pass

    def reflect(self):
        pass