
from persona.memory_structure.spatial_memory import SpatialMemory
from persona.memory_structure.associative_memory import AssociativeMemory
from persona.memory_structure.scratch import Scratch

from persona.cognitive_module.perceive import Perceive
from persona.cognitive_module.retrieve import Retrieve
from persona.cognitive_module.plan import Plan
from persona.cognitive_module.reflect import Reflect
from persona.cognitive_module.execute import Execute

class Persona:
    def __init__(self, name, f_memory_saved=False):
        #name : full name of persona , unique identifier for persona whitin Reverie
        self.name = name
        self.s_mem = SpatialMemory(f"{f_memory_saved}/spatial_memory.json")
        self.a_mem = AssociativeMemory(f"{f_memory_saved}/associative_memory")
        self.scratch = Scratch(f"{f_memory_saved}/scratch.json")
        self.before_event = {}

    def save(self, save_folder):
        self.s_mem.save(f"{save_folder}/spatial_memory.json")
        self.a_mem.save(f"{save_folder}/associative_memory")
        self.scratch.save(f"{save_folder}/scratch.json")
    def receive_event(self, event, personas, day_type):
        # 임시 변수 : day_type : False, First day, New day


        # event 발생 시 호출
        perceived = self.perceive(event)
        self.before_event = event
        retrieved = self.retrieve(perceived)
        plan = self.plan(personas, day_type, retrieved)
        self.reflect()
        return self.execute(personas, plan)

    def perceive(self, event):
        return Perceive.perceive(self, event, self.before_event)
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

    def execute(self, personas, plan):
        return Execute.execute(self, personas, plan)
        pass

    def reflect(self):
        Reflect.reflect(self)
        pass