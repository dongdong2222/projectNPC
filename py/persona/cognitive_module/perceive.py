
from persona.memory_structure.memory_node import MemoryNode
from persona.prompt_template.llm_manager import LLMManager
from persona.prompt_template.prompt_structure import PromptStructure
class Perceive:
    # perceive_observation
    # 호출 하나 당 한 번의 event 처리 일단은
    # TODO : 다른 agent들의 chat observation 시 처리
    # TODO : 한번에 여러 event 처리 시 update
    @staticmethod
    def perceive(persona, event, before_event):
        subject = event["subject"]
        predicate = event["predicate"]
        object = event["object"]
        description = event['description']
        if not predicate: #predicate가 0이면
            predicate = "is"
            object = "idle"
            description = "idle"
        description = f"{subject.split(':')[-1]} is {description}"

        # Get keywords
        keywords = generate_keyword_set(subject, object)

        # Get event embedding
        event_embedding_pair = generate_event_embedding_pair(persona, description)

        # Get event poignancy
        event_poignancy = generate_poignancy_score(persona, "event", description)

        # Generate memory node
        new_memory_nodes = []
        chat_node_ids = []
        # if self chat -> create chat memorynode and set in association memory
        if event["subject"] == f"{persona.name}" and event["predicate"] == "chat with":
            chat_node_ids = generate_self_chat_node(persona, event, keywords)

        #
        if before_event == event:
            new_memory_nodes += [persona.a_mem.make_node(persona.scratch.curr_time, None,
                               subject, predicate, object, description, keywords, event_poignancy,
                               event_embedding_pair, chat_node_ids)]
        else:
            new_memory_nodes += [ persona.a_mem.add_event(persona.scratch.curr_time, None,
                               subject, predicate, object, description, keywords, event_poignancy,
                               event_embedding_pair, chat_node_ids)]

        return new_memory_nodes


def generate_poignancy_score(persona, event_type, description):
    if "is idle" in description:
        return 1

    if event_type == "event":
        return LLMManager.run_prompt_event_poignancy(persona, description)[0]
    elif event_type == "chat":
        return LLMManager.run_prompt_chat_poignancy(persona, description)[0]
    pass


def generate_event_embedding_pair(persona, description):
    desc_embedding_in = description
    #TODO : 왜 괄호 안 문자열만 남기지..?
    if "(" in description:
        desc_embedding_in = (desc_embedding_in.split("(")[1]
                             .split(")")[0]
                             .strip())
    if desc_embedding_in in persona.a_mem.embeddings:
        event_embedding = persona.a_mem.embeddings[desc_embedding_in]
    else:
        event_embedding = PromptStructure.get_embedding(desc_embedding_in)

    event_embedding_pair = (desc_embedding_in, event_embedding)
    return event_embedding_pair

def generate_keyword_set(sub, obj):
    keywords = set()
    if ":" in sub:
        sub = sub.split(":")[-1]
    if ":" in obj:
        obj = obj.split(":")[-1]
    keywords.update([sub, obj])
    return keywords

def generate_self_chat_node(persona, p_event, keywords):
    chat_node_ids = []
    curr_event = persona.scratch.act_event
    if persona.scratch.act_description in persona.a_mem.embeddings:
        chat_embedding = persona.a_mem.embeddings[
            persona.scratch.act_description]
    else:
        chat_embedding = PromptStructure.get_embedding(persona.scratch
                                       .act_description)
        pass
    chat_embedding_pair = (persona.scratch.act_description,
                           chat_embedding)
    chat_poignancy = generate_poignancy_score(persona, "chat",
                                         persona.scratch.act_description)
    chat_node = persona.a_mem.add_chat(persona.scratch.curr_time, None,
                                       curr_event[0], curr_event[1], curr_event[2],
                                       persona.scratch.act_description, keywords,
                                       chat_poignancy, chat_embedding_pair,
                                       persona.scratch.chat)
    chat_node_ids = [chat_node.node_id]
    return chat_node_ids