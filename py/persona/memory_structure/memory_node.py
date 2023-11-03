


class MemoryNode:
    def __init__(self,
               node_id, node_count, type_count, node_type, depth,
               created, expiration,
               s, p, o,
               description, embedding_key, poignancy, keywords, filling):
        self.node_id = node_id
        self.node_count = node_count
        self.type_count = type_count
        self.type = node_type  # thought / event / chat
        self.depth = depth

        self.created = created
        self.expiration = expiration
        self.last_accessed = self.created

        self.subject = s
        self.predicate = p
        self.object = o

        self.description = description
        self.embedding_key = embedding_key
        self.poignancy = poignancy
        self.keywords = keywords
        self.filling = filling


        # self.node_id = f"node_{str(node_count)}"
        # self.node_count = node_count
        # ###### set by set_function
        # self.type = ""
        # self.depth = 0
        #
        # self.created = ""
        # self.expiration = ""
        # self.last_accessed = ""
        #
        # self.subject = ""
        # self.predicate = ""
        # self.object = ""
        #
        # self.description = ""
        # self.embedding_key = ""
        # self.poignancy = 0
        # self.keywords = ()
        # self.filling = []
        # pass

    # def set_type(self, type):
    #     self.type = type
    #     return self
    #
    # def set_depth(self, depth):
    #     self.depth = depth
    #     return self
    #
    # def set_created(self, created):
    #     self.created = created
    #     return self
    #
    # def set_expiration(self):
    #     self.expiration = None
    #     return self
    #
    # def set_subject(self, subject):
    #     self.subject = subject
    #     return self
    #
    # def set_predicate(self, predicate):
    #     self.predicate = predicate
    #     return self
    #
    # def set_object(self, object):
    #     self.object = object
    #     return self
    #
    # def set_description(self, description):
    #     self.description = description
    #     return self
    #
    # def set_embedding_key(self, event_embedding_key):
    #     self.event_embedding_key = event_embedding_key
    #     return self
    #
    # def set_poignancy(self, poignancy):
    #     self.poignancy = poignancy
    #     return self
    #
    # def set_keywords(self, keywords):
    #     self.keywords = keywords
    #     return self
    #
    # def set_filling(self, filling):
    #     self.filling = filling
    #     return self