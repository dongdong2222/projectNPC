
from persona.memory_structure.spatial_memory import SpatialMemory
from persona.memory_structure.associative_memory import AssociativeMemory
from persona.memory_structure.scratch import Scratch

from persona.cognitive_module.perceive import Perceive

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
    def receive_event(self, event):
        # event 발생 시 호출
        perceived = self.perceive(event)
        retrieved = self.retrieve(perceived)
        # TODO : plan = self.plan(retrieved) -> 진행중...
        # TODO : self.reflect()
        # TODO : return self.execute(plan)

    def perceive(self, event):
        return Perceive.perceive(self, event)
        pass

    def retrieve(self, perceived):
        pass

    def plan(self, retrieve):
        pass

    def execute(self, plan):
        pass

    def reflect(self):
        pass