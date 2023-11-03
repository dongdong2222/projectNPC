
import random
import string
import datetime
import ast
import re
import json
import sys

# sys.path.append("../../")
from utils import *
from global_methods import *
from persona.prompt_template.prompt_structure import PromptStructure
from print_prompt import *

class LLMManager:

    @staticmethod
    def get_random_alphanumeric(i=6, j=6):
        """
        Returns a random alpha numeric strength that has the length of somewhere
        between i and j.

        INPUT:
          i: min_range for the length
          j: max_range for the length
        OUTPUT:
          an alpha numeric str with the length of somewhere between i and j.
        """
        k = random.randint(i, j)
        x = ''.join(random.choices(string.ascii_letters + string.digits, k=k))
        # x = "1 5 d a A 7"
        return x

    @staticmethod
    def run_prompt_wake_up_hour(persona, test_input=None):
        '''persona의 일어나는 시간은?'''
        def create_prompt_input(persona, test_input=None):
            if test_input:
                return test_input
            prompt_input = [persona.scratch.get_str_iss(),
                            persona.scratch.get_str_lifestyle(),
                            persona.scratch.get_str_firstname()]
            return prompt_input

        def __func_clean_up(llm_response, prompt=""):
            cr = int(llm_response.strip().lower().split("am")[0])
            return cr

        def __func_validate(llm_response, prompt=""):
            try: __func_clean_up(llm_response, prompt="")
            except: return False
            return True

        #response 생성에 실패시 할당할 값
        def get_fail_safe():
            fs = 8
            return fs

        llm_param = { "max_new_tokens": 5,
                      "temperature": 0.8,
                      "top_p": 1}
        prompt_template = "templates_v1/wake_up_hour_v1.txt"
        prompt_input = create_prompt_input(persona, test_input)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        fail_safe = get_fail_safe()

        output = PromptStructure.generate_response(prompt, llm_param, 5, fail_safe,
                                                   __func_validate, __func_clean_up)
        return output

    @staticmethod
    def run_prompt_daily_plan(persona, wake_up_hour, test_input=None):
        '''대략적인 하루 일과 짜줘'''
        def create_prompt_input(persona, wake_up_hour, test_input):
            if test_input:
                return test_input
            prompt_input = [persona.scratch.get_str_iss(),
                            persona.scratch.get_str_lifestyle(),
                            persona.scratch.get_str_curr_date_str(),
                            persona.scratch.get_str_firstname(),
                            f"{str(wake_up_hour)}:00 am"]
            return prompt_input

        def __func_clean_up(llm_response, prompt=""):
            cr = []
            _cr = llm_response.split(")")
            for i in _cr:
                if i[-1].isdigit():
                    i = i[:-1].strip()
                    if i[-1] == "." or i[-1] == ",":
                        cr += [i[:-1].strip()]
            return cr

        def __func_validate(llm_response, prompt=""):
            try: __func_clean_up(llm_response, prompt="")
            except: return False
            return True

        def get_fail_safe():
            fs = ['wake up and complete the morning routine at 6:00 am',
                  'eat breakfast at 7:00 am',
                  'read a book from 8:00 am to 12:00 pm',
                  'have lunch at 12:00 pm',
                  'take a nap from 1:00 pm to 4:00 pm',
                  'relax and watch TV from 7:00 pm to 8:00 pm',
                  'go to bed at 11:00 pm']
            return fs

        llm_param = { "max_new_tokens": 500,
                      "temperature": 1,
                      "top_p": 1}
        prompt_template = "templates_v1/daily_planning_v1.txt"
        prompt_input = create_prompt_input(persona, wake_up_hour, test_input)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        fail_safe = get_fail_safe()

        output = PromptStructure.generate_response(prompt, llm_param, 5, fail_safe,
                                                   __func_validate, __func_clean_up)
        output = ([f"wake up and complete the morning routine at {wake_up_hour}:00 am"] + output)

        return output

    @staticmethod
    def run_prompt_generate_hourly_schedule(persona,
                                                curr_hour_str,
                                                p_f_ds_hourly_org,
                                                hour_str,
                                                intermission2=None,
                                                test_input=None,
                                                verbose=False):
        def create_prompt_input(persona,
                                curr_hour_str,
                                p_f_ds_hourly_org,
                                hour_str,
                                intermission2=None,
                                test_input=None):
            if test_input: return test_input

            # step 1 : schedule format 만들기
            schedule_format = ""
            for i in hour_str:
                schedule_format += f"[{persona.scratch.get_str_curr_date_str()} -- {i}]"
                schedule_format += f" Activity: [Fill in]\n"
            schedule_format = schedule_format[:-1]

            # step 2 : intermission_str 만들기, daily req 요약느낌
            intermission_str = f"Here the originally intended hourly breakdown of"
            intermission_str += f" {persona.scratch.get_str_firstname()}'s schedule today: "
            for count, i in enumerate(persona.scratch.daily_req):
                intermission_str += f"{str(count + 1)}) {i}, "
            intermission_str = intermission_str[:-2]

            # step 3 : prior_schedule 만들기
            prior_schedule = ""
            if p_f_ds_hourly_org:
                prior_schedule = "\n"
                for count, i in enumerate(p_f_ds_hourly_org):
                    prior_schedule += f"[(ID:{LLMManager.get_random_alphanumeric()})"
                    prior_schedule += f" {persona.scratch.get_str_curr_date_str()} --"
                    prior_schedule += f" {hour_str[count]}] Activity:"
                    prior_schedule += f" {persona.scratch.get_str_firstname()}"
                    prior_schedule += f" is {i}\n"

            prompt_ending = f"[(ID:{LLMManager.get_random_alphanumeric()})"
            prompt_ending += f" {persona.scratch.get_str_curr_date_str()}"
            prompt_ending += f" -- {curr_hour_str}] Activity:"
            prompt_ending += f" {persona.scratch.get_str_firstname()} is"

            if intermission2:
                intermission2 = f"\n{intermission2}"

            prompt_input = []
            prompt_input += [schedule_format]
            prompt_input += [persona.scratch.get_str_iss()]

            prompt_input += [prior_schedule + "\n"]
            prompt_input += [intermission_str]
            if intermission2:
                prompt_input += [intermission2]
            else:
                prompt_input += [""]
            prompt_input += [prompt_ending]

            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            cr = gpt_response.strip()
            if cr[-1] == ".":
                cr = cr[:-1]
            return

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt="")
            except:
                return False
            return True

        def get_fail_safe():
            fs = "asleep"
            return fs

        llm_param = { "max_new_tokens": 50,
                      "temperature": 0.5,
                      "top_p": 1}
        # gpt_param = {"engine": "text-davinci-003", "max_tokens": 50,
        #              "temperature": 0.5, "top_p": 1, "stream": False,
        #              "frequency_penalty": 0, "presence_penalty": 0, "stop": ["\n"]}
        prompt_template = "templates_v1/generate_hourly_schedule_v1.txt"
        prompt_input = create_prompt_input(persona,
                                           curr_hour_str,
                                           p_f_ds_hourly_org,
                                           hour_str,
                                           intermission2,
                                           test_input)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        fail_safe = get_fail_safe()

        output = PromptStructure.generate_response(prompt, llm_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)

        # if debug or verbose:
        #     print_run_prompts(prompt_template, persona, gpt_param,
        #                       prompt_input, prompt, output)

        return output

    # CLEAR!!
    @staticmethod
    def run_prompt_action_sector(action_description,
                                     persona,
                                     test_input=None,
                                     verbose=False):
        def create_prompt_input(action_description, persona, test_input=None):
            act_world = world_name # TODO : 임시 world_name

            prompt_input = []

            prompt_input += [persona.scratch.get_str_name()]
            prompt_input += [persona.scratch.living_area.split(":")[1]]
            x = f"{act_world}:{persona.scratch.living_area.split(':')[1]}"
            prompt_input += [persona.s_mem.get_str_accessible_sector_arenas(x)]

            prompt_input += [persona.scratch.get_str_name()]
            prompt_input += [f"{persona.scratch.curr_address['sector']}"]
            x = f"{act_world}:{persona.scratch.curr_address['sector']}"
            prompt_input += [persona.s_mem.get_str_accessible_sector_arenas(x)]

            if persona.scratch.get_str_daily_plan_req() != "":
                prompt_input += [f"\n{persona.scratch.get_str_daily_plan_req()}"]
            else:
                prompt_input += [""]

            # MAR 11 TEMP
            accessible_sector_str = persona.s_mem.get_str_accessible_sectors(act_world)
            curr = accessible_sector_str.split(", ")
            fin_accessible_sectors = []
            for i in curr:
                if "'s house" in i:
                    if persona.scratch.last_name in i:
                        fin_accessible_sectors += [i]
                else:
                    fin_accessible_sectors += [i]
            accessible_sector_str = ", ".join(fin_accessible_sectors)
            # END MAR 11 TEMP

            prompt_input += [accessible_sector_str]

            action_description_1 = action_description
            action_description_2 = action_description
            if "(" in action_description:
                action_description_1 = action_description.split("(")[0].strip()
                action_description_2 = action_description.split("(")[-1][:-1]
            prompt_input += [persona.scratch.get_str_name()]
            prompt_input += [action_description_1]

            prompt_input += [action_description_2]
            prompt_input += [persona.scratch.get_str_name()]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            cleaned_response = gpt_response.split("}")[0]
            return cleaned_response

        def __func_validate(gpt_response, prompt=""):
            if len(gpt_response.strip()) < 1:
                return False
            if "}" not in gpt_response:
                return False
            if "," in gpt_response:
                return False
            return True

        def get_fail_safe():
            fs = ("kitchen")
            return fs

        # # ChatGPT Plugin ===========================================================
        # def __chat_func_clean_up(gpt_response, prompt=""): ############
        #   cr = gpt_response.strip()
        #   return cr

        # def __chat_func_validate(gpt_response, prompt=""): ############
        #   try:
        #     gpt_response = __func_clean_up(gpt_response, prompt="")
        #   except:
        #     return False
        #   return True

        # print ("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 20") ########
        # gpt_param = {"engine": "text-davinci-002", "max_tokens": 15,
        #              "temperature": 0, "top_p": 1, "stream": False,
        #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
        # prompt_template = "persona/prompt_template/v3_ChatGPT/action_location_sector_v2.txt" ########
        # prompt_input = create_prompt_input(action_description, persona, maze)  ########
        # prompt = generate_prompt(prompt_input, prompt_template)
        # example_output = "Johnson Park" ########
        # special_instruction = "The value for the output must contain one of the area options above verbatim (including lower/upper case)." ########
        # fail_safe = get_fail_safe() ########
        # output = ChatGPT_safe_generate_response(prompt, example_output, special_instruction, 3, fail_safe,
        #                                         __chat_func_validate, __chat_func_clean_up, True)
        # if output != False:
        #   return output, [output, prompt, gpt_param, prompt_input, fail_safe]
        # # ChatGPT Plugin ===========================================================

        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.01,
                     "top_p": 1}
        prompt_template = "templates_v1/action_location_sector_v1.txt"
        prompt_input = create_prompt_input(action_description, persona)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)

        fail_safe = get_fail_safe()
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)
        y = persona.scratch.curr_address['world'] #f"{maze.access_tile(persona.scratch.curr_tile)['world']}"
        x = [i.strip() for i in persona.s_mem.get_str_accessible_sectors(y).split(",")]
        if output not in x:
            # output = random.choice(x)
            output = persona.scratch.living_area.split(":")[1]

        print("DEBUG", random.choice(x), "------", output)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # CLEAR!!
    @staticmethod
    def run_prompt_action_arena(action_description,
                                    persona,
                                    act_world, act_sector,
                                    test_input=None,
                                    verbose=False):
        def create_prompt_input(action_description, persona, act_world, act_sector, test_input=None):
            prompt_input = []
            # prompt_input += [persona.scratch.get_str_name()]
            # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["arena"]]
            # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["sector"]]
            prompt_input += [persona.scratch.get_str_name()]
            x = f"{act_world}:{act_sector}"
            prompt_input += [act_sector]

            # MAR 11 TEMP
            accessible_arena_str = persona.s_mem.get_str_accessible_sector_arenas(x)
            curr = accessible_arena_str.split(", ")
            fin_accessible_arenas = []
            for i in curr:
                if "'s room" in i:
                    if persona.scratch.last_name in i:
                        fin_accessible_arenas += [i]
                else:
                    fin_accessible_arenas += [i]
            accessible_arena_str = ", ".join(fin_accessible_arenas)
            # END MAR 11 TEMP

            prompt_input += [accessible_arena_str]

            action_description_1 = action_description
            action_description_2 = action_description
            if "(" in action_description:
                action_description_1 = action_description.split("(")[0].strip()
                action_description_2 = action_description.split("(")[-1][:-1]
            prompt_input += [persona.scratch.get_str_name()]
            prompt_input += [action_description_1]

            prompt_input += [action_description_2]
            prompt_input += [persona.scratch.get_str_name()]

            prompt_input += [act_sector]

            prompt_input += [accessible_arena_str]
            # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["arena"]]
            # x = f"{maze.access_tile(persona.scratch.curr_tile)['world']}:{maze.access_tile(persona.scratch.curr_tile)['sector']}:{maze.access_tile(persona.scratch.curr_tile)['arena']}"
            # prompt_input += [persona.s_mem.get_str_accessible_arena_game_objects(x)]

            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            cleaned_response = gpt_response.split("}")[0]
            return cleaned_response

        def __func_validate(gpt_response, prompt=""):
            if len(gpt_response.strip()) < 1:
                return False
            if "}" not in gpt_response:
                return False
            if "," in gpt_response:
                return False
            return True

        def get_fail_safe():
            fs = ("kitchen")
            return fs

        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1,
                     }
        prompt_template = "templates_v1/action_location_object_vMar11.txt"
        prompt_input = create_prompt_input(action_description, persona, act_world, act_sector)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)

        fail_safe = get_fail_safe()
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)
        print(output)
        # y = f"{act_world}:{act_sector}"
        # x = [i.strip() for i in persona.s_mem.get_str_accessible_sector_arenas(y).split(",")]
        # if output not in x:
        #   output = random.choice(x)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # CLEAR!!
    @staticmethod
    def run_prompt_action_game_object(action_description,
                                          persona,
                                          temp_address,
                                          test_input=None,
                                          verbose=False):
        def create_prompt_input(action_description,
                                persona,
                                temp_address,
                                test_input=None):
            prompt_input = []
            if "(" in action_description:
                action_description = action_description.split("(")[-1][:-1]

            prompt_input += [action_description]
            prompt_input += [persona
                             .s_mem.get_str_accessible_arena_game_objects(temp_address)]
            return prompt_input

        def __func_validate(gpt_response, prompt=""):
            if len(gpt_response.strip()) < 1:
                return False
            return True

        def __func_clean_up(gpt_response, prompt=""):
            cleaned_response = gpt_response.strip()
            return cleaned_response

        def get_fail_safe():
            fs = ("bed")
            return fs

        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/action_object_v2.txt"
        prompt_input = create_prompt_input(action_description,
                                           persona,
                                           temp_address,
                                           test_input)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)

        fail_safe = get_fail_safe()
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)

        x = [i.strip() for i in persona.s_mem.get_str_accessible_arena_game_objects(temp_address).split(",")]
        if output not in x:
            output = random.choice(x)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # def run_gpt_prompt_pronunciatio(action_description, persona, verbose=False):

    # CLEAR !!
    @staticmethod
    def run_prompt_event_triple(action_description, persona, verbose=False):
        def create_prompt_input(action_description, persona):
            if "(" in action_description:
                action_description = action_description.split("(")[-1].split(")")[0]
            prompt_input = [persona.name,
                            action_description,
                            persona.name]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            cr = gpt_response.strip()
            cr = [i.strip() for i in cr.split(")")[0].split(",")]
            return cr

        def __func_validate(gpt_response, prompt=""):
            try:
                gpt_response = __func_clean_up(gpt_response, prompt="")
                if len(gpt_response) != 2:
                    return False
            except:
                return False
            return True

        def get_fail_safe(persona):
            fs = (persona.name, "is", "idle")
            return fs

        # ChatGPT Plugin ===========================================================
        # def __chat_func_clean_up(gpt_response, prompt=""): ############
        #   cr = gpt_response.strip()
        #   cr = [i.strip() for i in cr.split(")")[0].split(",")]
        #   return cr

        # def __chat_func_validate(gpt_response, prompt=""): ############
        #   try:
        #     gpt_response = __func_clean_up(gpt_response, prompt="")
        #     if len(gpt_response) != 2:
        #       return False
        #   except: return False
        #   return True

        # print ("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 5") ########
        # gpt_param = {"engine": "text-davinci-002", "max_tokens": 15,
        #              "temperature": 0, "top_p": 1, "stream": False,
        #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
        # prompt_template = "persona/prompt_template/v3_ChatGPT/generate_event_triple_v1.txt" ########
        # prompt_input = create_prompt_input(action_description, persona)  ########
        # prompt = generate_prompt(prompt_input, prompt_template)
        # example_output = "(Jane Doe, cooking, breakfast)" ########
        # special_instruction = "The value for the output must ONLY contain the triple. If there is an incomplete element, just say 'None' but there needs to be three elements no matter what." ########
        # fail_safe = get_fail_safe(persona) ########
        # output = ChatGPT_safe_generate_response(prompt, example_output, special_instruction, 3, fail_safe,
        #                                         __chat_func_validate, __chat_func_clean_up, True)
        # if output != False:
        #   return output, [output, prompt, gpt_param, prompt_input, fail_safe]
        # ChatGPT Plugin ===========================================================

        gpt_param = {"max_new_tokens": 30,
                     "temperature": 0.1, "top_p": 1}
        prompt_template = "templates_v1/generate_event_triple_v1.txt"
        prompt_input = create_prompt_input(action_description, persona)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        fail_safe = get_fail_safe(persona)  ########
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)
        output = (persona.name, output[0], output[1])

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    #CLEAR !!
    @staticmethod
    def run_prompt_act_obj_desc(act_game_object, act_desp, persona, verbose=False):
        def create_prompt_input(act_game_object, act_desp, persona):
            prompt_input = [act_game_object,
                            persona.name,
                            act_desp,
                            act_game_object,
                            act_game_object]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            cr = gpt_response.strip()
            if cr[-1] == ".": cr = cr[:-1]
            return cr

        def __func_validate(gpt_response, prompt=""):
            try:
                gpt_response = __func_clean_up(gpt_response, prompt="")
            except:
                return False
            return True

        def get_fail_safe(act_game_object):
            fs = f"{act_game_object} is idle"
            return fs

        # ChatGPT Plugin ===========================================================
        def __chat_func_clean_up(gpt_response, prompt=""):  ############
            cr = gpt_response.strip()
            if cr[-1] == ".": cr = cr[:-1]
            return cr

        def __chat_func_validate(gpt_response, prompt=""):  ############
            try:
                gpt_response = __func_clean_up(gpt_response, prompt="")
            except:
                return False
            return True

        print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 6")  ########
        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/generate_obj_event_v1.txt"  ########
        prompt_input = create_prompt_input(act_game_object, act_desp, persona)  ########
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        example_output = "being fixed"  ########
        special_instruction = "The output should ONLY contain the phrase that should go in <fill in>."  ########
        fail_safe = get_fail_safe(act_game_object)  ########
        output = PromptStructure.generate_response(prompt, gpt_param,5,
                                                   fail_safe,__func_validate,__func_clean_up)
        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)
        if output != False:
            return output, [output, prompt, gpt_param, prompt_input, fail_safe]


        def create_prompt_input(init_persona, target_persona, retrieved, test_input=None):
            last_chat = init_persona.a_mem.get_last_chat(target_persona.name)
            last_chatted_time = ""
            last_chat_about = ""

            if last_chat:
                last_chatted_time = last_chat.created.strftime("%B %d, %Y, %H:%M:%S")
                last_chat_about = last_chat.description

            #retrieve description 합치기
            context = ""
            for c_node in retrieved["observation"]:
                # was만 끼워넣기?
                curr_desc = c_node.description.split(" ")
                # TODO : is를 was로 제대로 바꾸는지 확인
                curr_desc[2:3] = ["was"]
                curr_desc = " ".join(curr_desc)
                context += f"{curr_desc}. "
            context += "\n"
            for c_node in retrieved["thoughts"]:
                context += f"{c_node.description}. "

            curr_time = init_persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S %p")\
            # act_description은 full_daily_schedule임!
            init_persona_act_desc = init_persona.scratch.act_description
            init_persona_act_desc = remove_bracket(init_persona_act_desc)

    #CLEAR !!
    @staticmethod
    def run_gpt_prompt_act_obj_event_triple(act_game_object, act_obj_desc, persona, verbose=False):
        def create_prompt_input(act_game_object, act_obj_desc):
            prompt_input = [act_game_object,
                            act_obj_desc,
                            act_game_object]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            cr = gpt_response.strip()
            cr = [i.strip() for i in cr.split(")")[0].split(",")]
            return cr

        def __func_validate(gpt_response, prompt=""):
            try:
                gpt_response = __func_clean_up(gpt_response, prompt="")
                if len(gpt_response) != 2:
                    return False
            except:
                return False
            return True

        def get_fail_safe(act_game_object):
            fs = (act_game_object, "is", "idle")
            return fs

        gpt_param = {"max_new_tokens": 30,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/generate_event_triple_v1.txt"
        prompt_input = create_prompt_input(act_game_object, act_obj_desc)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        fail_safe = get_fail_safe(act_game_object)
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)
        output = (act_game_object, output[0], output[1])

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # Before Debug
    @staticmethod
    def run_prompt_new_decomp_schedule(persona,
                                           main_act_dur,
                                           truncated_act_dur,
                                           start_time_hour,
                                           end_time_hour,
                                           inserted_act,
                                           inserted_act_dur,
                                           test_input=None,
                                           verbose=False):
        def create_prompt_input(persona,
                                main_act_dur,
                                truncated_act_dur,
                                start_time_hour,
                                end_time_hour,
                                inserted_act,
                                inserted_act_dur,
                                test_input=None):
            persona_name = persona.name
            start_hour_str = start_time_hour.strftime("%H:%M %p")
            end_hour_str = end_time_hour.strftime("%H:%M %p")

            original_plan = ""
            for_time = start_time_hour
            for i in main_act_dur:
                original_plan += f'{for_time.strftime("%H:%M")} ~ {(for_time + datetime.timedelta(minutes=int(i[1]))).strftime("%H:%M")} -- ' + \
                                 i[0]
                original_plan += "\n"
                for_time += datetime.timedelta(minutes=int(i[1]))

            new_plan_init = ""
            for_time = start_time_hour
            for count, i in enumerate(truncated_act_dur):
                new_plan_init += f'{for_time.strftime("%H:%M")} ~ {(for_time + datetime.timedelta(minutes=int(i[1]))).strftime("%H:%M")} -- ' + \
                                 i[0]
                new_plan_init += "\n"
                if count < len(truncated_act_dur) - 1:
                    for_time += datetime.timedelta(minutes=int(i[1]))

            new_plan_init += (for_time + datetime.timedelta(minutes=int(i[1]))).strftime("%H:%M") + " ~"

            prompt_input = [persona_name,
                            start_hour_str,
                            end_hour_str,
                            original_plan,
                            persona_name,
                            inserted_act,
                            inserted_act_dur,
                            persona_name,
                            start_hour_str,
                            end_hour_str,
                            end_hour_str,
                            new_plan_init]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            new_schedule = prompt + " " + gpt_response.strip()
            new_schedule = new_schedule.split("The revised schedule:")[-1].strip()
            new_schedule = new_schedule.split("\n")

            ret_temp = []
            for i in new_schedule:
                ret_temp += [i.split(" -- ")]

            ret = []
            for time_str, action in ret_temp:
                start_time = time_str.split(" ~ ")[0].strip()
                end_time = time_str.split(" ~ ")[1].strip()
                delta = datetime.datetime.strptime(end_time, "%H:%M") - datetime.datetime.strptime(start_time, "%H:%M")
                delta_min = int(delta.total_seconds() / 60)
                if delta_min < 0: delta_min = 0
                ret += [[action, delta_min]]

            return ret

        def __func_validate(gpt_response, prompt=""):
            try:
                gpt_response = __func_clean_up(gpt_response, prompt)
                dur_sum = 0
                for act, dur in gpt_response:
                    dur_sum += dur
                    if str(type(act)) != "<class 'str'>":
                        return False
                    if str(type(dur)) != "<class 'int'>":
                        return False
                x = prompt.split("\n")[0].split("originally planned schedule from")[-1].strip()[:-1]
                x = [datetime.datetime.strptime(i.strip(), "%H:%M %p") for i in x.split(" to ")]
                delta_min = int((x[1] - x[0]).total_seconds() / 60)

                if int(dur_sum) != int(delta_min):
                    return False

            except:
                return False
            return True

        def get_fail_safe(main_act_dur, truncated_act_dur):
            dur_sum = 0
            for act, dur in main_act_dur: dur_sum += dur

            ret = truncated_act_dur[:]
            ret += main_act_dur[len(ret) - 1:]

            # If there are access, we need to trim...
            ret_dur_sum = 0
            count = 0
            over = None
            for act, dur in ret:
                ret_dur_sum += dur
                if ret_dur_sum == dur_sum:
                    break
                if ret_dur_sum > dur_sum:
                    over = ret_dur_sum - dur_sum
                    break
                count += 1

            if over:
                ret = ret[:count + 1]
                ret[-1][1] -= over

            return ret

        gpt_param = {"max_new_token": 1000,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/new_decomp_schedule_v1.txt"
        prompt_input = create_prompt_input(persona,
                                           main_act_dur,
                                           truncated_act_dur,
                                           start_time_hour,
                                           end_time_hour,
                                           inserted_act,
                                           inserted_act_dur,
                                           test_input)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        fail_safe = get_fail_safe(main_act_dur, truncated_act_dur)
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)

        # print ("* * * * output")
        # print (output)
        # print ('* * * * fail_safe')
        # print (fail_safe)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # Before Debug
    @staticmethod
    def run_prompt_decide_to_talk(persona, target_persona, retrieved, test_input=None,
                                      verbose=False):
        def create_prompt_input(init_persona, target_persona, retrieved,
                                test_input=None):
            last_chat = init_persona.a_mem.get_last_chat(target_persona.name)
            last_chatted_time = ""
            last_chat_about = ""
            if last_chat:
                last_chatted_time = last_chat.created.strftime("%B %d, %Y, %H:%M:%S")
                last_chat_about = last_chat.description

            context = ""
            for c_node in retrieved["events"]:
                curr_desc = c_node.description.split(" ")
                curr_desc[2:3] = ["was"]
                curr_desc = " ".join(curr_desc)
                context += f"{curr_desc}. "
            context += "\n"
            for c_node in retrieved["thoughts"]:
                context += f"{c_node.description}. "

            curr_time = init_persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S %p")
            init_act_desc = init_persona.scratch.act_description
            if "(" in init_act_desc:
                init_act_desc = init_act_desc.split("(")[-1][:-1]

            if len(init_persona.scratch.planned_path) == 0 and "waiting" not in init_act_desc:
                init_p_desc = f"{init_persona.name} is already {init_act_desc}"
            elif "waiting" in init_act_desc:
                init_p_desc = f"{init_persona.name} is {init_act_desc}"
            else:
                init_p_desc = f"{init_persona.name} is on the way to {init_act_desc}"

            target_act_desc = target_persona.scratch.act_description
            if "(" in target_act_desc:
                target_act_desc = target_act_desc.split("(")[-1][:-1]

            if len(target_persona.scratch.planned_path) == 0 and "waiting" not in init_act_desc:
                target_p_desc = f"{target_persona.name} is already {target_act_desc}"
            elif "waiting" in init_act_desc:
                target_p_desc = f"{init_persona.name} is {init_act_desc}"
            else:
                target_p_desc = f"{target_persona.name} is on the way to {target_act_desc}"

            prompt_input = []
            prompt_input += [context]

            prompt_input += [curr_time]

            prompt_input += [init_persona.name]
            prompt_input += [target_persona.name]
            prompt_input += [last_chatted_time]
            prompt_input += [last_chat_about]

            prompt_input += [init_p_desc]
            prompt_input += [target_p_desc]
            prompt_input += [init_persona.name]
            prompt_input += [target_persona.name]
            return prompt_input

        def __func_validate(gpt_response, prompt=""):
            try:
                if gpt_response.split("Answer in yes or no:")[-1].strip().lower() in ["yes", "no"]:
                    return True
                return False
            except:
                return False

        def __func_clean_up(gpt_response, prompt=""):
            return gpt_response.split("Answer in yes or no:")[-1].strip().lower()

        def get_fail_safe():
            fs = "yes"
            return fs

        gpt_param = {"max_new_tokens": 20,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/decide_to_talk_v2.txt"
        prompt_input = create_prompt_input(persona, target_persona, retrieved,
                                           test_input)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)

        fail_safe = get_fail_safe()
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    @staticmethod
    def run_prompt_decide_to_react(persona, target_persona, retrieved, test_input=None,
                                       verbose=False):
        def create_prompt_input(init_persona, target_persona, retrieved,
                                test_input=None):

            context = ""
            for c_node in retrieved["events"]:
                curr_desc = c_node.description.split(" ")
                curr_desc[2:3] = ["was"]
                curr_desc = " ".join(curr_desc)
                context += f"{curr_desc}. "
            context += "\n"
            for c_node in retrieved["thoughts"]:
                context += f"{c_node.description}. "

            curr_time = init_persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S %p")
            init_act_desc = init_persona.scratch.act_description
            if "(" in init_act_desc:
                init_act_desc = init_act_desc.split("(")[-1][:-1]
            if len(init_persona.scratch.planned_path) == 0:
                loc = ""
                if ":" in init_persona.scratch.act_address:
                    loc = init_persona.scratch.act_address.split(":")[-1] + " in " + \
                          init_persona.scratch.act_address.split(":")[-2]
                init_p_desc = f"{init_persona.name} is already {init_act_desc} at {loc}"
            else:
                loc = ""
                if ":" in init_persona.scratch.act_address:
                    loc = init_persona.scratch.act_address.split(":")[-1] + " in " + \
                          init_persona.scratch.act_address.split(":")[-2]
                init_p_desc = f"{init_persona.name} is on the way to {init_act_desc} at {loc}"

            target_act_desc = target_persona.scratch.act_description
            if "(" in target_act_desc:
                target_act_desc = target_act_desc.split("(")[-1][:-1]
            if len(target_persona.scratch.planned_path) == 0:
                loc = ""
                if ":" in target_persona.scratch.act_address:
                    loc = target_persona.scratch.act_address.split(":")[-1] + " in " + \
                          target_persona.scratch.act_address.split(":")[-2]
                target_p_desc = f"{target_persona.name} is already {target_act_desc} at {loc}"
            else:
                loc = ""
                if ":" in target_persona.scratch.act_address:
                    loc = target_persona.scratch.act_address.split(":")[-1] + " in " + \
                          target_persona.scratch.act_address.split(":")[-2]
                target_p_desc = f"{target_persona.name} is on the way to {target_act_desc} at {loc}"

            prompt_input = []
            prompt_input += [context]
            prompt_input += [curr_time]
            prompt_input += [init_p_desc]
            prompt_input += [target_p_desc]

            prompt_input += [init_persona.name]
            prompt_input += [init_act_desc]
            prompt_input += [target_persona.name]
            prompt_input += [target_act_desc]

            prompt_input += [init_act_desc]
            return prompt_input

        def __func_validate(gpt_response, prompt=""):
            try:
                if gpt_response.split("Answer: Option")[-1].strip().lower() in ["3", "2", "1"]:
                    return True
                return False
            except:
                return False

        def __func_clean_up(gpt_response, prompt=""):
            return gpt_response.split("Answer: Option")[-1].strip().lower()

        def get_fail_safe():
            fs = "3"
            return fs

        gpt_param = {"max_new_tokens": 20,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/decide_to_react_v1.txt"
        prompt_input = create_prompt_input(persona, target_persona, retrieved,
                                           test_input)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)

        fail_safe = get_fail_safe()
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # def run_gpt_prompt_create_conversation : 사용 안함

    @staticmethod
    def run_prompt_summarize_conversation(persona, conversation, test_input=None, verbose=False):
        def create_prompt_input(conversation, test_input=None):
            convo_str = ""
            for row in conversation:
                convo_str += f'{row[0]}: "{row[1]}"\n'

            prompt_input = [convo_str]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            ret = "conversing about " + gpt_response.strip()
            return ret

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return "conversing with a housemate about morning greetings"

        # ChatGPT Plugin ===========================================================
        def __chat_func_clean_up(gpt_response, prompt=""):  ############
            ret = "conversing about " + gpt_response.strip()
            return ret

        def __chat_func_validate(gpt_response, prompt=""):  ############
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 11")  ########
        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/summarize_conversation_v1.txt"  ########
        prompt_input = create_prompt_input(conversation, test_input)  ########
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        example_output = "conversing about what to eat for lunch"  ########
        special_instruction = "The output must continue the sentence above by filling in the <fill in> tag. Don't start with 'this is a conversation about...' Just finish the sentence but do not miss any important details (including who are chatting)."  ########
        fail_safe = get_fail_safe()  ########
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                                __chat_func_validate, __chat_func_clean_up)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        if output != False:
            return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # run_gpt_prompt_extract_keywords : 사용안함
    # run_gpt_prompt_keyword_to_thoughts : 사용안함
    # run_gpt_prompt_convo_to_thoughts : 사용안람

    # CLEAR !!
    @staticmethod
    def run_prompt_event_poignancy(persona, event_description, test_input=None, verbose=False):
        def create_prompt_input(persona, event_description, test_input=None):
            prompt_input = [persona.scratch.name,
                            persona.scratch.get_str_iss(),
                            persona.scratch.name,
                            event_description]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            gpt_response = int(gpt_response.strip())
            return gpt_response

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return 4

        # ChatGPT Plugin ===========================================================
        def __chat_func_clean_up(gpt_response, prompt=""):  ############
            gpt_response = int(gpt_response)
            return gpt_response

        def __chat_func_validate(gpt_response, prompt=""):  ############
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 7")  ########
        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/poignancy_event_v1.txt"  ########
        prompt_input = create_prompt_input(persona, event_description)  ########
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        example_output = "5"  ########
        special_instruction = "The output should ONLY contain ONE integer value on the scale of 1 to 10."  ########
        fail_safe = get_fail_safe()  ########
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                                __chat_func_validate, __chat_func_clean_up)
        if output != False:
            return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # run_gpt_prompt_thought_poignancy : 사용안함

    # CLEAR !!
    @staticmethod
    def run_prompt_chat_poignancy(persona, event_description, test_input=None, verbose=False):
        def create_prompt_input(persona, event_description, test_input=None):
            prompt_input = [persona.scratch.name,
                            persona.scratch.get_str_iss(),
                            persona.scratch.name,
                            event_description]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            gpt_response = int(gpt_response.strip())
            return gpt_response

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return 4

        # ChatGPT Plugin ===========================================================
        def __chat_func_clean_up(gpt_response, prompt=""):  ############
            gpt_response = int(gpt_response)
            return gpt_response

        def __chat_func_validate(gpt_response, prompt=""):  ############
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 9")  ########
        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/poignancy_chat_v1.txt"  ########
        prompt_input = create_prompt_input(persona, event_description)  ########
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        example_output = "5"  ########
        special_instruction = "The output should ONLY contain ONE integer value on the scale of 1 to 10."  ########
        fail_safe = get_fail_safe()  ########
        output = PromptStructure.generate_response(prompt, gpt_param, 3, fail_safe,
                                                __chat_func_validate, __chat_func_clean_up)
        if debug or verbose:
          print_run_prompts(prompt_template, persona, gpt_param,
                            prompt_input, prompt, output)

        if output != False:
            return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # Before Debug
    @staticmethod
    def run_prompt_focal_pt(persona, statements, n, test_input=None, verbose=False):
        def create_prompt_input(persona, statements, n, test_input=None):
            prompt_input = [statements, str(n)]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            gpt_response = "1) " + gpt_response.strip()
            ret = []
            for i in gpt_response.split("\n"):
                ret += [i.split(") ")[-1]]
            return ret

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe(n):
            return ["Who am I"] * n

        # ChatGPT Plugin ===========================================================
        def __chat_func_clean_up(gpt_response, prompt=""):  ############
            ret = ast.literal_eval(gpt_response)
            return ret

        def __chat_func_validate(gpt_response, prompt=""):  ############
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 12")  ########
        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/generate_focal_pt_v1.txt"  ########
        prompt_input = create_prompt_input(persona, statements, n)  ########
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        example_output = '["What should Jane do for lunch", "Does Jane like strawberry", "Who is Jane"]'  ########
        special_instruction = "Output must be a list of str."  ########
        fail_safe = get_fail_safe(n)  ########
        output = PromptStructure.generate_response(prompt, gpt_param, 3, fail_safe,
                                                __chat_func_validate, __chat_func_clean_up)

        if debug or verbose:
          print_run_prompts(prompt_template, persona, gpt_param,
                            prompt_input, prompt, output)

        if output != False:
            return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # Before Debug
    @staticmethod
    def run_prompt_insight_and_guidance(persona, statements, n, test_input=None, verbose=False):
        def create_prompt_input(persona, statements, n, test_input=None):
            prompt_input = [statements, str(n)]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            gpt_response = "1. " + gpt_response.strip()
            ret = dict()
            for i in gpt_response.split("\n"):
                row = i.split(". ")[-1]
                thought = row.split("(because of ")[0].strip()
                evi_raw = row.split("(because of ")[1].split(")")[0].strip()
                evi_raw = re.findall(r'\d+', evi_raw)
                evi_raw = [int(i.strip()) for i in evi_raw]
                ret[thought] = evi_raw
            return ret

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe(n):
            return ["I am hungry"] * n

        gpt_param = {"max_new_tokens": 150,
                     "temperature": 0.5,
                     "top_p": 1}
        prompt_template = "persona/prompt_template/v2/insight_and_evidence_v1.txt"
        prompt_input = create_prompt_input(persona, statements, n)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)

        fail_safe = get_fail_safe(n)
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]


    # Before Debug
    @staticmethod
    def run_prompt_agent_chat_summarize_ideas(persona, target_persona, statements, curr_context, test_input=None,
                                                  verbose=False):
        def create_prompt_input(persona, target_persona, statements, curr_context, test_input=None):
            prompt_input = [persona.scratch.get_str_curr_date_str(), curr_context, persona.scratch.currently,
                            statements, persona.scratch.name, target_persona.scratch.name]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            return gpt_response.split('"')[0].strip()

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return "..."

        # ChatGPT Plugin ===========================================================
        def __chat_func_clean_up(gpt_response, prompt=""):  ############
            return gpt_response.split('"')[0].strip()

        def __chat_func_validate(gpt_response, prompt=""):  ############
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 17")  ########
        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/summarize_chat_ideas_v1.txt"  ########
        prompt_input = create_prompt_input(persona, target_persona, statements, curr_context)  ########
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        example_output = 'Jane Doe is working on a project'  ########
        special_instruction = 'The output should be a string that responds to the question.'  ########
        fail_safe = get_fail_safe()  ########
        output = PromptStructure.generate_response(prompt, gpt_param, 3, fail_safe,
                                                __chat_func_validate, __chat_func_clean_up)

        if debug or verbose:
          print_run_prompts(prompt_template, persona, gpt_param,
                            prompt_input, prompt, output)

        if output != False:
            return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # Before Debug
    @staticmethod
    def run_prompt_agent_chat_summarize_relationship(persona, target_persona, statements, test_input=None,
                                                         verbose=False):
        def create_prompt_input(persona, target_persona, statements, test_input=None):
            prompt_input = [statements, persona.scratch.name, target_persona.scratch.name]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            return gpt_response.split('"')[0].strip()

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return "..."

        # ChatGPT Plugin ===========================================================
        def __chat_func_clean_up(gpt_response, prompt=""):  ############
            return gpt_response.split('"')[0].strip()

        def __chat_func_validate(gpt_response, prompt=""):  ############
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 18")  ########
        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/summarize_chat_relationship_v2.txt"  ########
        prompt_input = create_prompt_input(persona, target_persona, statements)  ########
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        example_output = 'Jane Doe is working on a project'  ########
        special_instruction = 'The output should be a string that responds to the question.'  ########
        fail_safe = get_fail_safe()  ########
        output = PromptStructure.generate_response(prompt, gpt_param, 3, fail_safe,
                                                __chat_func_validate, __chat_func_clean_up, True)
        if debug or verbose:
          print_run_prompts(prompt_template, persona, gpt_param,
                            prompt_input, prompt, output)

        if output != False:
            return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # Before Debug
    @staticmethod
    def run_prompt_agent_chat(maze, persona, target_persona,
                                  curr_context,
                                  init_summ_idea,
                                  target_summ_idea, test_input=None, verbose=False):
        def create_prompt_input(persona, target_persona, curr_context, init_summ_idea, target_summ_idea,
                                test_input=None):
            prev_convo_insert = "\n"
            if persona.a_mem.seq_chat:
                for i in persona.a_mem.seq_chat:
                    if i.object == target_persona.scratch.name:
                        v1 = int((persona.scratch.curr_time - i.created).total_seconds() / 60)
                        prev_convo_insert += f'{str(v1)} minutes ago, {persona.scratch.name} and {target_persona.scratch.name} were already {i.description} This context takes place after that conversation.'
                        break
            if prev_convo_insert == "\n":
                prev_convo_insert = ""
            if persona.a_mem.seq_chat:
                if int((persona.scratch.curr_time - persona.a_mem.seq_chat[-1].created).total_seconds() / 60) > 480:
                    prev_convo_insert = ""
            print(prev_convo_insert)

            curr_sector = f"{maze.access_tile(persona.scratch.curr_tile)['sector']}"
            curr_arena = f"{maze.access_tile(persona.scratch.curr_tile)['arena']}"
            curr_location = f"{curr_arena} in {curr_sector}"

            prompt_input = [persona.scratch.currently,
                            target_persona.scratch.currently,
                            prev_convo_insert,
                            curr_context,
                            curr_location,

                            persona.scratch.name,
                            init_summ_idea,
                            persona.scratch.name,
                            target_persona.scratch.name,

                            target_persona.scratch.name,
                            target_summ_idea,
                            target_persona.scratch.name,
                            persona.scratch.name,

                            persona.scratch.name]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            print(gpt_response)

            gpt_response = (prompt + gpt_response).split("Here is their conversation.")[-1].strip()
            content = re.findall('"([^"]*)"', gpt_response)

            speaker_order = []
            for i in gpt_response.split("\n"):
                name = i.split(":")[0].strip()
                if name:
                    speaker_order += [name]

            ret = []
            for count, speaker in enumerate(speaker_order):
                ret += [[speaker, content[count]]]

            return ret

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return "..."

        # ChatGPT Plugin ===========================================================
        def __chat_func_clean_up(gpt_response, prompt=""):  ############
            # ret = ast.literal_eval(gpt_response)

            print("a;dnfdap98fh4p9enf HEREE!!!")
            for row in gpt_response:
                print(row)

            return gpt_response

        def __chat_func_validate(gpt_response, prompt=""):  ############
            return True

        # print ("HERE JULY 23 -- ----- ") ########
        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/agent_chat_v1.txt"  ########
        prompt_input = create_prompt_input(persona, target_persona, curr_context, init_summ_idea,
                                           target_summ_idea)  ########
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        example_output = '[["Jane Doe", "Hi!"], ["John Doe", "Hello there!"] ... ]'  ########
        special_instruction = 'The output should be a list of list where the inner lists are in the form of ["<Name>", "<Utterance>"].'  ########
        fail_safe = get_fail_safe()  ########
        output = PromptStructure.generate_response(prompt, gpt_param, 3, fail_safe,
                                                __chat_func_validate, __chat_func_clean_up)
        # print ("HERE END JULY 23 -- ----- ") ########
        if output != False:
            return output, [output, prompt, gpt_param, prompt_input, fail_safe]


    # Before Debug
    @staticmethod
    def run_prompt_summarize_ideas(persona, statements, question, test_input=None, verbose=False):
        def create_prompt_input(persona, statements, question, test_input=None):
            prompt_input = [statements, persona.scratch.name, question]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            return gpt_response.split('"')[0].strip()

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return "..."

        # ChatGPT Plugin ===========================================================
        def __chat_func_clean_up(gpt_response, prompt=""):  ############
            return gpt_response.split('"')[0].strip()

        def __chat_func_validate(gpt_response, prompt=""):  ############
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 16")  ########
        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/summarize_ideas_v1.txt"  ########
        prompt_input = create_prompt_input(persona, statements, question)  ########
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        example_output = 'Jane Doe is working on a project'  ########
        special_instruction = 'The output should be a string that responds to the question.'  ########
        fail_safe = get_fail_safe()  ########
        output = PromptStructure.generate_response(prompt, gpt_param, 3, fail_safe,
                                                __chat_func_validate, __chat_func_clean_up)
        if output != False:
            return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # Before Debug
    @staticmethod
    def run_prompt_generate_next_convo_line(persona, interlocutor_desc, prev_convo, retrieved_summary,
                                                test_input=None, verbose=False):
        def create_prompt_input(persona, interlocutor_desc, prev_convo, retrieved_summary, test_input=None):
            prompt_input = [persona.scratch.name,
                            persona.scratch.get_str_iss(),
                            persona.scratch.name,
                            interlocutor_desc,
                            prev_convo,
                            persona.scratch.name,
                            retrieved_summary,
                            persona.scratch.name, ]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            return gpt_response.split('"')[0].strip()

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return "..."

        # # ChatGPT Plugin ===========================================================
        # def __chat_func_clean_up(gpt_response, prompt=""): ############
        #   return gpt_response.split('"')[0].strip()

        # def __chat_func_validate(gpt_response, prompt=""): ############
        #   try:
        #     __func_clean_up(gpt_response, prompt)
        #     return True
        #   except:
        #     return False

        # print ("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 15") ########
        # gpt_param = {"engine": "text-davinci-002", "max_tokens": 15,
        #              "temperature": 0, "top_p": 1, "stream": False,
        #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
        # prompt_template = "persona/prompt_template/v3_ChatGPT/generate_next_convo_line_v1.txt" ########
        # prompt_input = create_prompt_input(persona, interlocutor_desc, prev_convo, retrieved_summary)  ########
        # prompt = generate_prompt(prompt_input, prompt_template)
        # example_output = 'Hello' ########
        # special_instruction = 'The output should be a string that responds to the question. Again, only use the context included in the "Note" to generate the response' ########
        # fail_safe = get_fail_safe() ########
        # output = ChatGPT_safe_generate_response(prompt, example_output, special_instruction, 3, fail_safe,
        #                                         __chat_func_validate, __chat_func_clean_up, True)
        # if output != False:
        #   return output, [output, prompt, gpt_param, prompt_input, fail_safe]
        # # ChatGPT Plugin ===========================================================

        gpt_param = {"max_new_tokens": 250,
                     "temperature": 1,
                     "top_p": 1}
        prompt_template = "templates_v1/generate_next_convo_line_v1.txt"
        prompt_input = create_prompt_input(persona, interlocutor_desc, prev_convo, retrieved_summary)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)

        fail_safe = get_fail_safe()
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # Before Debug
    @staticmethod
    def run_prompt_generate_whisper_inner_thought(persona, whisper, test_input=None, verbose=False):
        def create_prompt_input(persona, whisper, test_input=None):
            prompt_input = [persona.scratch.name, whisper]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            return gpt_response.split('"')[0].strip()

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return "..."

        gpt_param = {"max_new_tokens": 50,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/whisper_inner_thought_v1.txt"
        prompt_input = create_prompt_input(persona, whisper)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)

        fail_safe = get_fail_safe()
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # Before Debug
    @staticmethod
    def run_prompt_planning_thought_on_convo(persona, all_utt, test_input=None, verbose=False):
        def create_prompt_input(persona, all_utt, test_input=None):
            prompt_input = [all_utt, persona.scratch.name, persona.scratch.name, persona.scratch.name]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            return gpt_response.split('"')[0].strip()

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return "..."

        gpt_param = {"max_new_tokens": 50,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/planning_thought_on_convo_v1.txt"
        prompt_input = create_prompt_input(persona, all_utt)
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)

        fail_safe = get_fail_safe()
        output = PromptStructure.generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

        return output, [output, prompt, gpt_param, prompt_input, fail_safe]


    @staticmethod
    def run_prompt_memo_on_convo(persona, all_utt, test_input=None, verbose=False):
        def create_prompt_input(persona, all_utt, test_input=None):
            prompt_input = [all_utt, persona.scratch.name, persona.scratch.name, persona.scratch.name]
            return prompt_input

        def __func_clean_up(gpt_response, prompt=""):
            return gpt_response.split('"')[0].strip()

        def __func_validate(gpt_response, prompt=""):
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        def get_fail_safe():
            return "..."

        # ChatGPT Plugin ===========================================================
        def __chat_func_clean_up(gpt_response, prompt=""):  ############
            return gpt_response.strip()

        def __chat_func_validate(gpt_response, prompt=""):  ############
            try:
                __func_clean_up(gpt_response, prompt)
                return True
            except:
                return False

        print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 15")  ########
        gpt_param = {"max_new_tokens": 15,
                     "temperature": 0.1,
                     "top_p": 1}
        prompt_template = "templates_v1/memo_on_convo_v1.txt"  ########
        prompt_input = create_prompt_input(persona, all_utt)  ########
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        example_output = 'Jane Doe was interesting to talk to.'  ########
        special_instruction = 'The output should ONLY contain a string that summarizes anything interesting that the agent may have noticed'  ########
        fail_safe = get_fail_safe()  ########
        output = PromptStructure.generate_response(prompt, gpt_param, 3, fail_safe,
                                                __chat_func_validate, __chat_func_clean_up)
        if output != False:
            return output, [output, prompt, gpt_param, prompt_input, fail_safe]
        # ChatGPT Plugin ===========================================================
        #
        # gpt_param = {"engine": "text-davinci-003", "max_tokens": 50,
        #              "temperature": 0, "top_p": 1, "stream": False,
        #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
        # prompt_template = "persona/prompt_template/v2/memo_on_convo_v1.txt"
        # prompt_input = create_prompt_input(persona, all_utt)
        # prompt = generate_prompt(prompt_input, prompt_template)
        #
        # fail_safe = get_fail_safe()
        # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
        #                                 __func_validate, __func_clean_up)
        #
        # if debug or verbose:
        #     print_run_prompts(prompt_template, persona, gpt_param,
        #                       prompt_input, prompt, output)
        #
        # return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    # 일단 보류
    # @staticmethod
    # def run_gpt_generate_safety_score(persona, comment, test_input=None, verbose=False):
    #     def create_prompt_input(comment, test_input=None):
    #         prompt_input = [comment]
    #         return prompt_input
    #
    #     def __chat_func_clean_up(gpt_response, prompt=""):
    #         gpt_response = json.loads(gpt_response)
    #         return gpt_response["output"]
    #
    #     def __chat_func_validate(gpt_response, prompt=""):
    #         try:
    #             fields = ["output"]
    #             response = json.loads(gpt_response)
    #             for field in fields:
    #                 if field not in response:
    #                     return False
    #             return True
    #         except:
    #             return False
    #
    #     def get_fail_safe():
    #         return None
    #
    #     print("11")
    #     prompt_template = "persona/prompt_template/safety/anthromorphosization_v1.txt"
    #     prompt_input = create_prompt_input(comment)
    #     print("22")
    #     prompt = generate_prompt(prompt_input, prompt_template)
    #     print(prompt)
    #     fail_safe = get_fail_safe()
    #     output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
    #                                                 __chat_func_validate, __chat_func_clean_up, verbose)
    #     print(output)
    #
    #     gpt_param = {"engine": "text-davinci-003", "max_tokens": 50,
    #                  "temperature": 0, "top_p": 1, "stream": False,
    #                  "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    #     return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    @staticmethod
    def extract_first_json_dict(data_str):
        # Find the first occurrence of a JSON object within the string
        start_idx = data_str.find('{')
        end_idx = data_str.find('}', start_idx) + 1

        # Check if both start and end indices were found
        if start_idx == -1 or end_idx == 0:
            return None

        # Extract the first JSON dictionary
        json_str = data_str[start_idx:end_idx]

        try:
            # Attempt to parse the JSON data
            json_dict = json.loads(json_str)
            return json_dict
        except json.JSONDecodeError:
            # If parsing fails, return None
            return None

    # Before Debug
    @staticmethod
    def run_generate_iterative_chat_utt(maze, init_persona, target_persona, retrieved, curr_context, curr_chat,
                                            test_input=None, verbose=False):
        def create_prompt_input(maze, init_persona, target_persona, retrieved, curr_context, curr_chat,
                                test_input=None):
            persona = init_persona
            prev_convo_insert = "\n"
            if persona.a_mem.seq_chat:
                for i in persona.a_mem.seq_chat:
                    if i.object == target_persona.scratch.name:
                        v1 = int((persona.scratch.curr_time - i.created).total_seconds() / 60)
                        prev_convo_insert += f'{str(v1)} minutes ago, {persona.scratch.name} and {target_persona.scratch.name} were already {i.description} This context takes place after that conversation.'
                        break
            if prev_convo_insert == "\n":
                prev_convo_insert = ""
            if persona.a_mem.seq_chat:
                if int((persona.scratch.curr_time - persona.a_mem.seq_chat[-1].created).total_seconds() / 60) > 480:
                    prev_convo_insert = ""
            print(prev_convo_insert)

            curr_sector = f"{maze.access_tile(persona.scratch.curr_tile)['sector']}"
            curr_arena = f"{maze.access_tile(persona.scratch.curr_tile)['arena']}"
            curr_location = f"{curr_arena} in {curr_sector}"

            retrieved_str = ""
            for key, vals in retrieved.items():
                for v in vals:
                    retrieved_str += f"- {v.description}\n"

            convo_str = ""
            for i in curr_chat:
                convo_str += ": ".join(i) + "\n"
            if convo_str == "":
                convo_str = "[The conversation has not started yet -- start it!]"

            init_iss = f"Here is Here is a brief description of {init_persona.scratch.name}.\n{init_persona.scratch.get_str_iss()}"
            prompt_input = [init_iss, init_persona.scratch.name, retrieved_str, prev_convo_insert,
                            curr_location, curr_context, init_persona.scratch.name, target_persona.scratch.name,
                            convo_str, init_persona.scratch.name, target_persona.scratch.name,
                            init_persona.scratch.name, init_persona.scratch.name,
                            init_persona.scratch.name
                            ]
            return prompt_input

        def __chat_func_clean_up(gpt_response, prompt=""):
            gpt_response = LLMManager.extract_first_json_dict(gpt_response)

            cleaned_dict = dict()
            cleaned = []
            for key, val in gpt_response.items():
                cleaned += [val]
            cleaned_dict["utterance"] = cleaned[0]
            cleaned_dict["end"] = True
            if "f" in str(cleaned[1]) or "F" in str(cleaned[1]):
                cleaned_dict["end"] = False

            return cleaned_dict

        def __chat_func_validate(gpt_response, prompt=""):
            print("ugh...")
            try:
                # print ("debug 1")
                # print (gpt_response)
                # print ("debug 2")

                print(LLMManager.extract_first_json_dict(gpt_response))
                # print ("debug 3")

                return True
            except:
                return False

        def get_fail_safe():
            cleaned_dict = dict()
            cleaned_dict["utterance"] = "..."
            cleaned_dict["end"] = False
            return cleaned_dict

        print("11")
        prompt_template = "templates_v1/iterative_convo_v1.txt"
        prompt_input = create_prompt_input(maze, init_persona, target_persona, retrieved, curr_context, curr_chat)
        print("22")
        prompt = PromptStructure.generate_prompt(prompt_input, prompt_template)
        print(prompt)
        fail_safe = get_fail_safe()
        gpt_param = {"max_new_tokens": 50,
                     "temperature": 0.1,
                     "top_p": 1}

        output = PromptStructure.generate_response(prompt, gpt_param, 3, fail_safe,
                                                    __chat_func_validate, __chat_func_clean_up)
        print(output)


        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

if __name__ == "__main__":
    verbose = True
    import sys
    print(sys.path)
    from persona.persona import Persona
    persona_name = "Isabella Rodriguez"
    persona_folder = f"../../environment/persona/{persona_name}"

    PromptStructure.load_llama_7B_chat_hf(model_path)
    Isabella = Persona(persona_name, persona_folder)

    # test1
    # wake_up_hour = LLMManager.run_prompt_wake_up_hour(Isabella)
    # print(wake_up_hour)

    # test2
    # daily_plan = LLMManager.run_prompt_daily_plan(Isabella, wake_up_hour)
    # Isabella.scratch.daily_req = daily_plan
    # print(daily_plan)

    #test3
    # hour_str = ["00:00 AM", "01:00 AM", "02:00 AM", "03:00 AM", "04:00 AM",
    #             "05:00 AM", "06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM",
    #             "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM",
    #             "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM",
    #             "08:00 PM", "09:00 PM", "10:00 PM", "11:00 PM"]
    # n_m1_activity = []
    # diversity_repeat_count = 3
    # for i in range(diversity_repeat_count):
    #     n_m1_activity_set = set(n_m1_activity)
    #     if len(n_m1_activity_set) < 5:
    #         n_m1_activity = []
    #         for count, curr_hour_str in enumerate(hour_str):
    #             if wake_up_hour > 0:
    #                 n_m1_activity += ["sleeping"]
    #                 wake_up_hour -= 1
    #             else:
    #                 n_m1_activity += [LLMManager.run_prompt_generate_hourly_schedule(Dolores, curr_hour_str, n_m1_activity, hour_str)]
    #
    # print(n_m1_activity)

    # test run_prompt_action_sector
    # action_sector = LLMManager.run_prompt_action_sector("opening Hobbs Cafe (unlocking the cafe door)", Isabella)
    # print(action_sector)

    # test run_prompt_action_arena
    # action_world = Isabella.scratch.curr_address['world']
    # action_arena = LLMManager.run_prompt_action_arena("opening Hobbs Cafe (unlocking the cafe door)", Isabella, action_world, "Hobbs Cafe")
    # print(action_sector)

    # test run_prompt_action_game_object
    # action_address = "the Ville:Giorgio Rossi's apartment:bathroom"
    # action_game_object = LLMManager.run_prompt_action_game_object("opening Hobbs Cafe (unlocking the cafe door)", Isabella, action_address)
    # print(action_game_object)

    # test run_prompt_event_triple
    # event_triple = LLMManager.run_prompt_event_triple("opening Hobbs Cafe (unlocking the cafe door)", Isabella)
    # print(event_triple)

    # test run_prompt_act_obj_desc
    # obj_desc = LLMManager.run_prompt_act_obj_desc("cafe","opening Hobbs Cafe (unlocking the cafe door)", Isabella)
    # print(obj_desc)

    # test run_gpt_prompt_act_obj_event_triple
    # act_obj_desc = LLMManager.run_gpt_prompt_act_obj_event_triple("cafe","opening Hobbs Cafe (unlocking the cafe door)", Isabella)
    # print(act_obj_desc)

    # test run_prompt_event_poignancy
    poignancy = LLMManager.run_prompt_event_poignancy(Isabella, "Isabella Rodriguez is organizing the cafe menu")
    print(poignancy)

    # test run_prompt_event_poignancy
    poignancy = LLMManager.run_prompt_chat_poignancy(Isabella, "Isabella Rodriguez is organizing the cafe menu")
    print(poignancy)