
import random
import string
import datetime
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

        gpt_param = {"engine": "text-davinci-003", "max_tokens": 30,
                     "temperature": 0, "top_p": 1, "stream": False,
                     "frequency_penalty": 0, "presence_penalty": 0, "stop": ["\n"]}
        prompt_template = "persona/prompt_template/v2/generate_event_triple_v1.txt"
        prompt_input = create_prompt_input(act_game_object, act_obj_desc)
        prompt = generate_prompt(prompt_input, prompt_template)
        fail_safe = get_fail_safe(act_game_object)
        output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
                                        __func_validate, __func_clean_up)
        output = (act_game_object, output[0], output[1])

        if debug or verbose:
            print_run_prompts(prompt_template, persona, gpt_param,
                              prompt_input, prompt, output)

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
    obj_desc = LLMManager.run_prompt_act_obj_desc("cafe","opening Hobbs Cafe (unlocking the cafe door)", Isabella)
    print(obj_desc)
