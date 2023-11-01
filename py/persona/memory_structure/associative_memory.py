
import json

from global_methods import *
from persona.memory_structure.memory_node import MemoryNode

class AssociativeMemory:
    #TODO : f_saved에 있던 내용 upload하기
    def __init__(self, f_saved):
        self.id_to_node = dict()

        # self.seq_event = []
        # self.seq_chat = []
        # self.seq_thought = []

        self.kw_to_event = dict()
        self.kw_to_chat = dict()
        self.kw_to_thought = dict()

        self.embeddings = json.load(open(f_saved + "/embeddings.json"))
        pass

    def save(self, out_json):
        out = dict()
        for count in range(len(self.id_to_node.keys()), 0, -1):
            node_id = f"node_{str(count)}"
            node = self.id_to_node[node_id]

            out[node_id] = dict()
            out[node_id]["node_count"] = node.node_count
            # out[node_id]["type_count"] = node.type_count
            out[node_id]["type"] = node.type
            out[node_id]["depth"] = node.depth

            out[node_id]["created"] = node.created.strftime('%Y-%m-%d %H:%M:%S')
            out[node_id]["expiration"] = None
            if node.expiration:
                out[node_id]["expiration"] = (node.expiration.strftime('%Y-%m-%d %H:%M:%S'))

            out[node_id]["subject"] = node.subject
            out[node_id]["predicate"] = node.predicate
            out[node_id]["object"] = node.object

            out[node_id]["description"] = node.description
            out[node_id]["embedding_key"] = node.embedding_key
            out[node_id]["poignancy"] = node.poignancy
            out[node_id]["keywords"] = list(node.keywords)
            out[node_id]["filling"] = node.filling

        with open(out_json+"/nodes.json", "w") as outfile:
            json.dump(out, outfile)


    def add_event(self):
        node_count = len(self.id_to_node.keys()) + 1
        new_memory_node = MemoryNode(node_count).set_type("event")

        return new_memory_node

    def add_chat(self):
        pass

    def add_thought(self):
        node_count = len(self.id_to_node.keys()) + 1
        new_memory_node = MemoryNode(node_count).set_type("thought")
        pass

    def set_memory_nodes(self, nodes):
        for node in nodes:
            # self.seq_event[0:0] = [node]
            keywords = [i.lower() for i in node.keywords]
            for kw in keywords:
                if kw in self.kw_to_event:
                    self.kw_to_event[kw][0:0] = [node]
                else:
                    self.kw_to_event[kw] = [node]
            self.id_to_node[node.node_id] = node

            #TODO : set kw_strength
        pass

    def retrieve_relevant_event(self, sub, pre, obj):
        contents = [sub, pre, obj]

        ret = []
        for i in contents:
            if i in self.kw_to_event:
                ret += self.kw_to_event[i]

        ret = set(ret)
        return ret

    def retrieve_relevant_thought(self, sub, pre, obj):
        content = [sub, pre, obj]

        ret = []
        for i in content:
            if i in self.kw_to_thought:
                ret += self.kw_to_thought[i.lower()]

        ret = set(ret)
        return ret
