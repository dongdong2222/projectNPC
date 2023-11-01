
from persona.memory_structure.memory_node import MemoryNode

class Perceive:
    # perceive_observation
    # 호출 하나 당 한 번의 event 처리 일단은
    # TODO : 다른 agent들의 chat observation 시 처리
    # TODO : 한번에 여러 event 처리 시 update
    @staticmethod
    def perceive_event(persona, event):
        subject = event["subject"]
        predicate = event["predicate"]
        object = event["object"]
        description = event["description"]

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
        new_memory_nodes += [ persona.a_mem.add_observation().\
            set_depth(0).\
            set_created(persona.scratch.curr_time).set_expiration().\
            set_subject(subject).set_predicate(predicate).set_object(object).set_description(description).\
            set_embedding_key(event_embedding_pair[0]).set_poignancy(event_poignancy).\
            set_keywords(keywords).set_filling(None) ]
        persona.a_mem.set_memory_nodes(new_memory_nodes)

        return new_memory_nodes

    @staticmethod
    def perceive_chat(persona, event):
        #내가 chat with이라는 이벤트 발생되면
        #scratch의 chat내용을 보고 chat type memory node 생성
        subject = event["subject"]
        predicate = event["predicate"]
        object = event["object"]
        description = event["description"]

        #if subject == f"{persona.name}" and predicate == "chat with":
        pass
    pass



def generate_poignancy_score(persona, event_type, description):
    if "is idle" in description:
        return 1

    if event_type == "event":
        #TODO : return run_gpt_prompt_observation_poignancy(persona, description)[0]
        return 1
    elif event_type == "chat":
        #TODO : return run_gpt_prompt_chat_poignancy(persona, description)[0]
        return 1
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
        #TODO : event_embedding = get_embedding(desc_embedding_in)
        event_embedding = None

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
