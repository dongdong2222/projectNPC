import json

from typing import Union
from fastapi import FastAPI, Form
from fastapi import Request
from pydantic import BaseModel

from event_observer import EventObserver
from persona.prompt_template.prompt_structure import PromptStructure
from global_methods import *

app = FastAPI()
class inputData(BaseModel):
    postData: str
    persona_name : str
class BackEnd:
    def __init__(self):
        # day_type = "New day", "First day", False
        self.event_observer = EventObserver()
        PromptStructure.load_llama_7B_chat_hf("../../llama2chat7Bhf")
        PromptStructure.load_embedding_model()
        print("test init")



@app.post("/aaa/{ddd}")
async def process_post_request(ddd: str, key1: str = Form(...), key2: str = Form(...)):
    # 여기서 원하는 대로 요청을 처리하고 결과를 반환하세요.
    print(0)
    result = f"Received POST request with key1={key1} and key2={key2}"
    return {"result": result}



@app.get("/")
def read_root():
    return {"message": "start"}

### Event
@app.get("/event/observe/{persona_name}")
async def read_observe_event(persona_name: str, content: Union[str, None] = None, day_type: Union[str, bool] = False):
    if content is not None:
        json_event = json.loads(content)
        # json_event["object"] = json_event["obj"]
        # del json_event["obj"]
        response = app.state.backend.event_observer.observe(persona_name, json_event, day_type)
        print(type(response))
        print(f"response : {response}")

    return {"response": "response"}

@app.get("/event/whisper/{persona_name}")
async def read_whisper_event(persona_name: str, content: Union[str, None] = None, day_type: Union[str, bool] = False):
    pass

### Map
@app.get("/data/map/init")
def init_map():
    # TODO : map.json 가져오기
    with open("./environment/map.json") as map_json:
        mapData = json.load(map_json)
        return mapData

@app.post("/data/map/{object_info}")
def write_object(object_info: str, postData: dict):
    # TODO : object description 업데이트 후 내용 response
    pass

### Persona
@app.get("/data/personas")
def read_personas():
    return {}

@app.get("/data/personas/scratch/{persona_name}")
def read_scratch(persona_name: str, content: Union[str, None] = None):
    if content == "curr_address":
        return app.state.backend.event_observer.personas[persona_name].scracth.curr_address
        # TODO : scracht에서 데이터 받아오기
    elif content == "curr_chat":
        chat = app.state.backend.event_observer.personas[persona_name].scracth.chatting_with
        chat_dict = {}
        for item in chat:
            key = item[0]
            value = item[1]

            if key in chat_dict:
                chat_dict[key].append(value)
            else:
                chat_dict[key] = [value]
        return chat_dict
    return {"persona_name": persona_name, "content": content}

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
    print("curr_address_json:", postData["curr_address"])
    scratch = app.state.backend.event_observer.personas[persona_name].scratch
    response_dict = {}
    if ("curr_address" in postData):
        scratch.curr_address = convert_address_to_dict(postData["curr_address"])
        response_dict['curr_address'] = postData["curr_address"]
    return response_dict
@app.post("/data/personas/memory_stream/{persona_name}")
def write_memory_stream(persona_name: str, content: Union[str, None] = None):
    return {}

@app.post("/data/personas/spacial_memory/{persona_name}")
def write_spacial_memory(persona_name: str, content: Union[str, None] = None):
    return {}


@app.post("/example")
async def example_endpoint(data: str):
    print("")
    # 어떤 로직 수행

    # 간단한 JSON 응답 반환
    return {"status": "success", "message": "This is an example response"}
# -----------------------------------------
@app.on_event("startup")
async def startup_event():
    app.state.backend = BackEnd()
@app.on_event("shutdown")
async def shutdown_event():
    app.state.temp = None  # 또는 del app.state.my_object