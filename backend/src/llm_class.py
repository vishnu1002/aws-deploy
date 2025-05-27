from openai import OpenAI
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForVision2Seq, AutoProcessor
from abc import ABC, abstractmethod


class LLMBase(ABC):
    @abstractmethod
    def query(self, prompt: str) -> str:
        pass

class DeepSeek(LLMBase):
    def __init__(self, model="deepseek-ai/DeepSeek-R1-Distill-Llama-8B", api_base="http://10.10.100.122:4444/v1", api_key="c2VjdXJlc2VydmVyCg=="):
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        self.model = model 

    def query(self, prompt): 
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"


class Llama(LLMBase):
    def __init__(self, model_name="llama-3.3-70b-versatile", api_base="https://api.groq.com/openai/v1", api_key="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"):
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        self.model_name = model_name

    def query(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"


class Qwen(LLMBase):
    def __init__(self, model_name="qwen-qwq-32b", api_base="https://api.groq.com/openai/v1", api_key="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"):
        self.client = OpenAI(api_key=api_key,base_url=api_base)
        self.model_name = model_name 

    def query(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0.6
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

