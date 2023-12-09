import json

from typing import Union
from fastapi import FastAPI, Form
from fastapi import Request
from pydantic import BaseModel
import asyncio

import uvicorn
from event_observer import EventObserver
from persona.prompt_template.prompt_structure import PromptStructure
from global_methods import *
from time_manager import Timer

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
app = FastAPI()
class inputData(BaseModel):
    postData: str
    persona_name : str
class BackEnd:
    def __init__(self):
        # day_type = "New day", "First day", False
        self.event_observer = EventObserver()
        PromptStructure.load_llama_7B_chat_hf_and_LoRA("../../llama2chat7Bhf")
        PromptStructure.load_embedding_model()
        self.timer = Timer()
        print("test init")



async def main_observe_task(persona_name, json_event, day_type):
    elapsed = app.state.backend.timer.get_elapsed_time()
    app.state.backend.event_observer.personas[persona_name].scratch.curr_time += elapsed
    response = app.state.backend.event_observer.observe(persona_name, json_event, day_type)
    act_event_list = app.state.backend.event_observer.personas[persona_name].scratch.get_curr_event_and_desc()
    act_event = {'subject': act_event_list[0], 'predicate': act_event_list[1], 'obj': act_event_list[2],
                 'description': act_event_list[3]}
    response['act_event'] = act_event
    print(f"curr_time : {app.state.backend.event_observer.personas[persona_name].scratch.curr_time}")
    print(f"response : {response}")


@app.get("/")
def read_root():
    return {"message": "start"}

### Event
@app.get("/event/observe/{persona_name}")
async def read_observe_event(persona_name: str, content: Union[str, None] = None, day_type: Union[str, bool] = False):
    response = {}
    if content is not None:
        json_event = json.loads(content)
        print(f"content: {json_event}")
        # json_event["object"] = json_event["obj"]
        # del json_event["obj"]
        # asyncio.create_task(main_observe_task(persona_name, json_event, day_type))
        scratch = app.state.backend.event_observer.personas[persona_name].scratch
        elapsed = app.state.backend.timer.get_elapsed_time()
        app.state.backend.event_observer.personas[persona_name].scratch.curr_time += elapsed

        response = app.state.backend.event_observer.observe(persona_name, json_event, day_type)
        act_event_list = scratch.get_curr_event_and_desc()
        act_event = {'subject': act_event_list[0], 'predicate': act_event_list[1], 'obj': act_event_list[2],
                     'description': act_event_list[3]}
        act_obj_event_list = scratch.get_curr_obj_event_and_desc()
        act_obj_event = {'subject': act_obj_event_list[0], 'predicate': act_obj_event_list[1], 'obj': act_obj_event_list[2],
                     'description': act_obj_event_list[3]}
        response['act_address'] = scratch.act_address
        response['act_event'] = act_event
        response['act_obj_event'] = act_obj_event
        response['curr_time'] = scratch.curr_time
        response['addition_plan'] = scratch.addition_plan
        print(f"response : {response}")
    return response


@app.get("/event/whisper/{persona_name}")
async def read_whisper_event(persona_name: str, content: Union[str, None] = None, day_type: Union[str, bool] = False):
    pass

### Map
@app.get("/data/map/init")
def init_map():
    # TODO : map.json 가져오기
    with open("./environment/map.json") as map_json:
        app.state.backend.timer.start_timer()
        mapData = json.load(map_json)
        return mapData

@app.post("/data/map/{object_info}")
def write_object(object_info: str, postData: dict):
    # TODO : object description 업데이트 후 내용 response scratch.act_obj_description 넘겨야함
    pass

### Persona
@app.get("/data/personas")
def read_personas():
    return {}

@app.get("/data/personas/scratch/{persona_name}")
def read_scratch(persona_name: str, content1: Union[str, None] = None, content2: Union[str, None] = None):
    response_dict = {}
    if content1 == "curr_address":
        response_dict["curr_address"] = app.state.backend.event_observer.personas[persona_name].scracth.curr_address
        # TODO : scracht에서 데이터 받아오기
    elif content1 == "curr_chat":
        chat_with = app.state.backend.event_observer.personas[persona_name].scracth.chatting_with
        chat = app.state.backend.event_observer.personas[persona_name].scracth.chat
        chat_dict = {}
        for item in chat:
            key = item[0]
            value = item[1]

            if key in chat_dict:
                chat_dict[key].append(value)
            else:
                chat_dict[key] = [value]
        response_dict['curr_chat'] = chat_dict
    elif content1 == "act_obj_event":
        act_obj_event_list = app.state.backend.event_observer.personas[persona_name].scratch.get_curr_obj_event_and_desc()
        act_obj_event = {'subject': act_obj_event_list[0], 'predicate': act_obj_event_list[1], 'obj': act_obj_event_list[2],
                     'description': act_obj_event_list[3]}
        response_dict['act_obj_event'] = act_obj_event
    elif content1 == "act_address":
        pass
        #TODO
    return response_dict

@app.get("/data/personas/memory_stream/{persona_name}")
def read_memory_stream(persona_name: str, content: Union[str, None] = None):
    return {}

@app.get("/data/personas/spatial_memory/{persona_name}")
def read_spatial_memory(persona_name: str, content: Union[str, None] = None):
    return {}

@app.post("/data/personas/scratch/{persona_name}")
async def write_scratch(persona_name: str, postData: dict):
    # curr_address_json = json.loads(curr_address)
    print("persona_name:", persona_name)
    # print("curr_address_json:", postData["curr_address"])
    scratch = app.state.backend.event_observer.personas[persona_name].scratch
    response_dict = {}
    elapsed = app.state.backend.timer.get_elapsed_time()
    app.state.backend.event_observer.personas[persona_name].scratch.curr_time += elapsed
    if ("curr_address" in postData):
        scratch.curr_address = convert_address_to_dict(postData["curr_address"])
        response_dict['curr_address'] = postData["curr_address"]
    if ("act_address" in postData):
        response_dict['act_address'] = scratch.act_address
    if ('act_description' in postData):
        response_dict['act_description'] = scratch.act_description
    if ('act_duration' in postData):
        response_dict['act_duration'] = scratch.act_duration
    if ('addition_plan' in postData):
        response_dict['addition_plan'] = scratch.addition_plan
    if ('f_daily_schedule' in postData):
        schedule = scratch.f_daily_schedule
        temp = []
        for plan in schedule:
            temp += [plan[0]]
        response_dict['f_daily_schedule'] = temp
    response_dict['curr_time'] = scratch.curr_time
    # return {"write_scratch": "ddd"}
    return response_dict
@app.post("/data/personas/memory_stream/{persona_name}")
def write_memory_stream(persona_name: str, content: Union[str, None] = None):
    return {}

@app.post("/data/personas/spacial_memory/{persona_name}")
def write_spacial_memory(persona_name: str, content: Union[str, None] = None):
    return {}


################Player 축가가가
@app.post("/player/chat/{persona_name}")
def chat_with_persona(persona_name: str, postData: dict):
    pass

# -----------------------------------------
@app.on_event("startup")
async def startup_event():
    app.state.backend = BackEnd()
@app.on_event("shutdown")
async def shutdown_event():
    app.state.temp = None  # 또는 del app.state.my_object

# if __name__ == '__main__':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     uvicorn.run(app, host="0.0.0.0", port=5712, loop="asyncio")