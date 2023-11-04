
import torch
import traceback

#from utils import *
from transformers import LlamaForCausalLM, LlamaTokenizer
from sentence_transformers import SentenceTransformer

class PromptStructure:
    model = None
    tokenizer = None
    embedding_model = None

    @staticmethod
    def generate_prompt(curr_input, prompt_lib_file):
        """
        Takes in the current input (e.g. comment that you want to classifiy) and
        the path to a prompt file. The prompt file contains the raw str prompt that
        will be used, which contains the following substr: !<INPUT>! -- this
        function replaces this substr with the actual curr_input to produce the
        final promopt that will be sent to the GPT3 server.
        ARGS:
          curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                      INPUT, THIS CAN BE A LIST.)
          prompt_lib_file: the path to the promopt file.
        RETURNS:
          a str prompt that will be sent to OpenAI's GPT server.
        """
        if type(curr_input) == type("string"):
            curr_input = [curr_input]
        curr_input = [str(i) for i in curr_input]

        f = open(prompt_lib_file, "r")
        prompt = f.read()
        f.close()
        for count, i in enumerate(curr_input):
            prompt = prompt.replace(f"!<INPUT {count}>!", i)
        if "<commentblockmarker>###</commentblockmarker>" in prompt:
            prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
        return prompt.strip()
    @classmethod
    def generate_response(cls,
                          prompt,
                          llm_parameter,
                          repeat=5,
                          fail_safe_response="fail_safe_response",
                          func_validate=None,
                          func_clean_up=None,
                          verbose=False):
        if verbose:
            print(prompt)

        for i in range(repeat):
            curr_llm_response = cls.LLama_request(prompt, llm_parameter)
            if func_validate(curr_llm_response, prompt=prompt):
                return func_clean_up(curr_llm_response, prompt=prompt)
            if verbose:
                print("---- repeat count: ", i, curr_llm_response)
                print(curr_llm_response)
                print("~~~~")
        return fail_safe_response

    @classmethod
    def get_embedding(cls, text):
        text = text.replace("\n", " ")
        if not text:
            text = "this is blank"
        embeddings = cls.embedding_model.encode(text)
        return embeddings

    # ---------------------------------------------
    @classmethod
    def load_llama_7B_chat_hf(cls, path):
        cls.tokenizer = LlamaTokenizer.from_pretrained(path)
        cls.model = LlamaForCausalLM.from_pretrained(path, device_map="auto", torch_dtype=torch.float16)
        cls.tokenizer.add_special_tokens(
            {
                "pad_token" : "<PAD>",
            }
        )
        cls.model.resize_token_embeddings(cls.model.config.vocab_size + 1)
        cls.model.eval()

    @classmethod
    def load_embedding_model(cls):
        cls.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    @classmethod
    def LLama_request(cls, prompt, llm_parameter=None):
        try:
            with torch.no_grad():
                input = cls.tokenizer(prompt, padding=True, truncation=True, return_tensors="pt").to("cuda")
                if llm_parameter is None:
                    output = cls.model.generate(**input)
                else:
                    output = cls.model.generate(**input,
                                                max_new_tokens=llm_parameter["max_new_tokens"],
                                                temperature=llm_parameter["temperature"],
                                                top_p=llm_parameter["top_p"])
                #TODO : 응답만 반환하도록 바꾸기
                output_text = cls.tokenizer.decode(output[0], skip_sepcial_tokens=True)
                response_text = output_text.replace(prompt, "").replace("<s>", "").replace("</s>", "").strip()
                print(f"output text : {output_text}")
                print(f"response text : {response_text}")
                return response_text
        except:
            traceback_message = traceback.format_exc()
            print("TOKEN LIMIT EXCEEDED")
            print(traceback_message)
            return "TOKEN LIMIT EXCEEDED"

