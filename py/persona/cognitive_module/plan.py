
import datetime

from persona.cognitive_module.retrieve import Retrieve
from persona.prompt_template.llm_manager import LLMManager
from persona.prompt_template.prompt_structure import PromptStructure

class Plan:
    def __init__(self):
        pass

    @staticmethod
    def plan(persona, retrieved, new_day):
        #part 1 : check first day, new day, non
        if new_day:
            _plan_daily_schedule(persona, new_day)

        #part 2 : check current action expired, if expired create new plan
        if persona.scratch:# TODO : act_check_finished()
            _determine_action(persona)

        #part 3 : 대응할 이벤트인지 인지 후 관련 정보 검색
        # step 1 : determine which of the event to focus on for the persona
        focused_events = _choose_retrieved(persona, retrieved)


        # step 2 : 선택한 event들에 어떤 대응을 할지 결정
        #           3가지 reaction 있음
        #               1) chat with {target_persona}
        #               2) react
        #               3) False
        if focused_events:
            reaction_mode = _get_reaction_mode(persona, focused_events)
            if reaction_mode:
                if reaction_mode[:9] == "chat with":
                    #_chat_react()
                    pass
                elif reaction_mode[:4] == "wait":
                    #_wait_react()
                    pass


        # step 3 : Chat-related state clean up.

        # if persona.scratch.act_event[1] != "chat with":
        #     persona.scratch.chatting_with = None
        #     persona.scratch.chat = None
        #     persona.scratch.chatting_end_time = None


        # 채팅 loop에 빠지지 않도록 하고 싶다 -> buffer 사용

        # curr_persona_chat_buffer = persona.scratch.chatting_with_buffer
        # for persona_name, buffer_count in curr_persona_chat_buffer.items():
        #     if persona_name != persona.scratch.chatting_with:
        #         persona.scratch.chatting_with_buffer[persona_name] -= 1

        #TODO : 모임...
        return persona.scratch.act_address

    pass


def _plan_daily_schedule(persona, new_day):
    wake_up_hour = generate_wake_up_hour(persona)

    #part 1 : update scratch.daily_plan, scratch.daily_plan_rep
    if new_day == "First day":
        persona.scratch.daily_plan = generate_first_daily_plan(persona, wake_up_hour)
    elif new_day == "New day":
        revise_identity(persona)
        # TODO : generate daily_plan
        persona.scratch.daily_plan = persona.scratch.daily_plan

    #part 2 : update scratch.full_daily_schedule, scratch.full_daily_schedule_hourly_org
    persona.scratch.full_daily_schedule = generate_hourly_schedule(persona, wake_up_hour)
    persona.scratch.full_daily_schedule_hourly_org = (persona.scratch.full_daily_schedule[:])

    #part 3 : add plan to the memory
    thought = f"This is {persona.scratch.name}'s plan for {persona.scratch.curr_time.strftime('%A %B %d')}:"
    for i in persona.scratch.daily_plan:
        thought += f" {i},"
    thought = thought[:-1] + "."
    created = persona.scratch.curr_time
    expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
    sub, pre, obj = (persona.scratch.name, "plan", persona.scratch.curr_time.strftime('%A %B %d'))
    keywords = {"plan"}
    thought_poignancy = 5
    thought_embedding_pair = (thought, PromptStructure.get_embedding(thought))

    new_memory_node = persona.a_mem.add_thought().set_depth(1).set_created(created).set_expiration(expiration).\
        set_subject(sub).set_predicate(pre).set_object(obj).set_description(thought).\
        set_keywords(keywords).set_poignancy(thought_poignancy).set_embedding_pair(thought_embedding_pair).\
        set_filling(None)
    persona.a_mem.set_memory_nodes([new_memory_node])
    pass

def _determine_action(persona):
    pass

def _choose_retrieved(persona, retrieve):
    pass

def _get_reaction_mode(persona, focusd_events):
    def lets_talk(init_persona, target_persona, retrieved):
        pass

    pass

# ---------------------------------------------------

def generate_wake_up_hour(persona):
    return int(LLMManager.run_prompt_wake_up_hour(persona))

def generate_first_daily_plan(persona, wake_up_hour):
    return LLMManager.run_prompt_daily_plan(persona, wake_up_hour)

def generate_hourly_schedule(persona, wake_up_hour):
    pass

def generate_decide_to_talk(init_persona, target_persona, retrieved):
    x = LLMManager.run_prompt_decide_to_talk(init_persona, target_persona, retrieved)

def revise_identity(persona):
    p_name = persona.scratch.name

    focal_point = [f"{p_name}'s plan for {persona.scratch.get_str_curr_date_str()}.",
                   f"Important recent events for {p_name}'s life."]
    retrieved = Retrieve.retrieve_with_focal(persona, focal_point)

    statements = "[Statements]\n"
    for key, val in retrieved.items():
        for i in val:
            statements += f"{i.created.strftime('%A %B %d -- %H:%M %p')}: {i.embedding_key}\n"

    plan_prompt = statements + "\n"
    plan_prompt += f"Given the statements above, is there anything that {p_name} should remember as they plan for"
    plan_prompt += f" *{persona.scratch.curr_time.strftime('%A %B %d')}*? "
    plan_prompt += f"If there is any scheduling information, be as specific as possible (include date, time, and location if stated in the statement)\n\n"
    plan_prompt += f"Write the response from {p_name}'s perspective."
    plan_note = PromptStructure.LLama_request(plan_prompt)

    thought_prompt = statements + "\n"
    thought_prompt += f"Given the statements above, how might we summarize {p_name}'s feelings about their days up to now?\n\n"
    thought_prompt += f"Write the response from {p_name}'s perspective."
    thought_note = PromptStructure.LLama_request(thought_prompt)

    currently_prompt = f"{p_name}'s status from {(persona.scratch.curr_time - datetime.timedelta(days=1)).strftime('%A %B %d')}:\n"
    currently_prompt += f"{persona.scratch.currently}\n\n"
    currently_prompt += f"{p_name}'s thoughts at the end of {(persona.scratch.curr_time - datetime.timedelta(days=1)).strftime('%A %B %d')}:\n"
    currently_prompt += (plan_note + thought_note).replace('\n', '') + "\n\n"
    currently_prompt += f"It is now {persona.scratch.curr_time.strftime('%A %B %d')}. Given the above, write {p_name}'s status for {persona.scratch.curr_time.strftime('%A %B %d')} that reflects {p_name}'s thoughts at the end of {(persona.scratch.curr_time - datetime.timedelta(days=1)).strftime('%A %B %d')}. Write this in third-person talking about {p_name}."
    currently_prompt += f"If there is any scheduling information, be as specific as possible (include date, time, and location if stated in the statement).\n\n"
    currently_prompt += "Follow this format below:\nStatus: <new status>"

    new_currently = PromptStructure.LLama_request(currently_prompt)
    persona.scratch.currently = new_currently

    daily_req_prompt = persona.scratch.get_str_iss() + "\n"
    daily_req_prompt += f"Today is {persona.scratch.curr_time.strftime('%A %B %d')}. Here is {persona.scratch.name}'s plan today in broad-strokes (with the time of the day. e.g., have a lunch at 12:00 pm, watch TV from 7 to 8 pm).\n\n"
    daily_req_prompt += f"Follow this format (the list should have 4~6 items but no more):\n"
    daily_req_prompt += f"1. wake up and complete the morning routine at <time>, 2. ..."

    new_daily_plan = PromptStructure.LLama_request(daily_req_prompt)
    new_daily_plan = new_daily_plan.replace("\n", " ")
    persona.scratch.daily_plan_req = new_daily_plan