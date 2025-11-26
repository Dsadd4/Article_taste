# utils.py
import json
import yaml
import os
from typing import List, Dict, Optional

# 从YAML文件加载API keys
def load_api_keys(config_path=None):
    """从YAML配置文件加载API keys"""
    if config_path is None:
        # 默认使用当前文件同目录下的api_key_config.yaml
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'api_key_config.yaml')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('api_keys', {})
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件未找到: {config_path}")
    except Exception as e:
        raise Exception(f"加载配置文件失败: {e}")

# 加载API keys
_api_keys = load_api_keys()
QWENKEY = _api_keys.get('qwen', '')
DEEPSEEKKEY = _api_keys.get('deepseek', '')
GPTKEY = _api_keys.get('gpt', '')

def mv_file(src_path,dst_path):
    #将src_path下的文件移动到dst_path下，如果存在同名文件，则删除
    import os
    import shutil
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    os.makedirs(dst_path)
    for file in os.listdir(src_path):
        if os.path.exists(os.path.join(dst_path, file)):
            os.remove(os.path.join(dst_path, file))
        shutil.move(os.path.join(src_path, file), os.path.join(dst_path, file))

import re

class Preprocessor:
    def improve_content(self, content: str) -> str:
        """
        去掉冗余符号，保留文本内容，以便语言模型处理。
        
        主要操作：
        1. 去掉多余空格、制表符、换行
        2. 去掉多余标点（例如连续的点、逗号、横线）
        3. 保留字母、数字、常见标点（句号、逗号、冒号、分号、括号等）
        4. 标准化空格
        """
        if not content:
            return ""

        # 1. 去掉控制符、不可见字符
        text = re.sub(r"[\x00-\x1F\x7F]", " ", content)

        # 2. 多个空格压缩成一个
        text = re.sub(r"\s+", " ", text)

        # 3. 去掉重复标点，比如 "...." -> ".", "----" -> "-"
        text = re.sub(r"([.,;:!?()\-])\1+", r"\1", text)

        # 4. 去掉首尾空格
        text = text.strip()

        return text

def chat_with_Qwen_thinkingmodel(task,prompt,model="qwen-flash"):
    from openai import OpenAI
    import os

    client = OpenAI(
        # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
        api_key=QWENKEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    messages = [
            {"role": "system", "content": f"You are a scientific expert in the task of {task}."},
            {"role": "user", "content": prompt},
        ]

    completion = client.chat.completions.create(
        model=model,  # 您可以按需更换为其它深度思考模型
        messages=messages,
        extra_body={"enable_thinking": True},
        stream=True
    ) 

    full_response = ""
    for chunk in completion:
        delta = chunk.choices[0].delta
        # full_response += "\n" + "=" * 20 + "thinking process" + "=" * 20
        if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
            
            full_response += delta.reasoning_content
       
        # full_response += "\n" + "=" * 20 + "full response" + "=" * 20
        if hasattr(delta, "content") and delta.content:
            
            full_response += delta.content
            print(delta.content, end="", flush=True)

    return full_response, ""


def chat_with_Qwen(task: str, prompt: str, model: str = "qwen-flash", history_messages: Optional[List[Dict[str, str]]] = None):

    # if model == "qwen-flash":
    #     return chat_with_Qwen_thinkingmodel(task,prompt,model)
    
    import os
    from openai import OpenAI

    client = OpenAI(
        # 贵，烧钱,
        api_key=QWENKEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
     )

    # 构建消息列表
    messages = [
        {"role": "system", "content": f"You are a expert in the task of {task}."}
    ]
    
    # 如果有历史消息，追加到消息列表中
    if history_messages:
        messages.extend(history_messages)
    
    # 添加当前用户消息
    messages.append({"role": "user", "content": prompt})

    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model=model,
        messages=messages,
        # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
        # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
        # extra_body={"enable_thinking": False},
    )
    # print(completion.model_dump_json())
    return completion.choices[0].message.content, completion.usage

def chat_with_deepseek(task: str, prompt: str, model: str = "deepseek-chat", history_messages: Optional[List[Dict[str, str]]] = None):
    from openai import OpenAI
    import re
    try:
        client = OpenAI(api_key=DEEPSEEKKEY, base_url="https://api.deepseek.com") 
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": f"You are a scientific expert in the task of {task}."}
        ]
        
        # 如果有历史消息，追加到消息列表中
        if history_messages:
            messages.extend(history_messages)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False
        )

        return response.choices[0].message.content, response.usage
    except Exception as e:
        print(f"DeepSeek API调用错误: {e}")
        return "DeepSeek API调用失败", {"total_tokens": 0}


def chat_with_gpt(task: str, prompt: str, model: str = "gpt-4", temperature: float = 0.5, history_messages: Optional[List[Dict[str, str]]] = None):
    import requests
    import json
    url = "https://gpt-api.hkust-gz.edu.cn/v1/chat/completions"
    headers = { 
    "Content-Type": "application/json", 
    "Authorization": f"Bearer {GPTKEY}" #Please change your KEY. If your key is XXX, the Authorization is "Authorization": "Bearer XXX"
    }

    # 构建消息列表
    messages = [
        {"role": "system", "content": f"You are a scientific expert in the task of {task}."}
    ]
    
    # 如果有历史消息，追加到消息列表中
    if history_messages:
        messages.extend(history_messages)
    
    # 添加当前用户消息
    messages.append({"role": "user", "content": prompt})

    data = { 
    "model": model, # # "gpt-3.5-turbo" version in gpt-4o-mini, "gpt-4" version in gpt-4o-2024-08-06
    "messages": messages,
    "temperature": temperature
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # 检查HTTP错误
        response_data = response.json()
        
        if 'choices' not in response_data or not response_data['choices']:
            raise ValueError("API响应中没有找到choices")
            
        raw_response = response_data['choices'][0]['message']['content']
        token_consume = response_data.get('usage', {})
        
        return raw_response, token_consume
    except requests.exceptions.RequestException as e:
        print(f"API请求错误: {e}")
        return "API请求失败", {"total_tokens": 0}
    except (KeyError, ValueError) as e:
        print(f"解析API响应错误: {e}")
        return "解析响应失败", {"total_tokens": 0}
    except Exception as e:
        print(f"未知错误: {e}")
        return "未知错误", {"total_tokens": 0}




#定义一个chat_engine类用于与gpt,deepseek,openai等进行交互


class chat_engine:
    def __init__(self):
        self.response = ""
        self.token_consume = 0
        self.completion_tokens = 0
        self.prompt_tokens = 0
        self.prompt_template = None
        # group supported models by provider to keep selection logic simple
        self.support_model = {
            'deepseekseries': ["deepseek-chat", "deepseek-reasoner"],
            'gptseries': ["gpt-4", "gpt-4o", "gpt-3.5-turbo", "gpt-5"],
            'qwen': ["qwen3-max", "qwen-flash"],
        }
    
    def get_support_model(self):
        return self.support_model

    def load_prompt_template(self,prompt_template_path):
        self.prompt_template = json.load(open(prompt_template_path, 'r', encoding='utf-8'))
    
    def chat_with_LLM(self, task: str, prompt: str, model_type: str, temperature: float = 0.5, history_messages: Optional[List[Dict[str, str]]] = None):
        """
        与LLM进行对话
        
        参数:
            task: 任务描述
            prompt: 当前用户消息
            model_type: 模型类型（如 'qwen-flash', 'deepseek-chat', 'gpt-4' 等）
            temperature: 温度参数（默认0.5）
            history_messages: 历史对话消息列表，格式为 List[Dict[str, str]]，
                            每个字典包含 'role' 和 'content' 键
                            例如: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        
        返回:
            str: 模型响应内容
        """
        # breakpoint()
        if model_type in self.support_model['deepseekseries']:
            self.response, token_consume = chat_with_deepseek(task,prompt,model_type,history_messages)
            
            # 处理OpenAI Usage对象
            if hasattr(token_consume, 'total_tokens'):
                self.token_consume += int(token_consume.total_tokens)
            elif isinstance(token_consume, dict) and 'total_tokens' in token_consume:
                self.token_consume += int(token_consume['total_tokens'])
            else:
                print(f"警告: 无法获取token消耗信息，token_consume格式: {type(token_consume)}")
        elif model_type in self.support_model['gptseries']:
            # Normalize friendly aliases to actual API model identifiers.
            provider_model = model_type
            if model_type == "gpt-4o":
                provider_model = "gpt-4o-2024-08-06"
            elif model_type == "gpt-5":
                assert False, "gpt-5 is not supported currently, please use gpt-4o or gpt-4 or gpt-3.5-turbo"

            self.response, token_consume = chat_with_gpt(task,prompt,provider_model,temperature,history_messages)
            # 处理字典格式的token_consume
            # print(token_consume)
            if isinstance(token_consume, dict) and 'total_tokens' in token_consume:
                self.token_consume += int(token_consume['total_tokens'])
                self.completion_tokens += int(token_consume['completion_tokens'])
                self.prompt_tokens += int(token_consume['prompt_tokens'])
            else:
                print(f"警告: 无法获取token消耗信息，token_consume格式: {type(token_consume)}")
        elif model_type in self.support_model['qwen']:
            self.response, token_consume = chat_with_Qwen(task,prompt,model_type,history_messages)
            if isinstance(token_consume, dict) and 'total_tokens' in token_consume:
                self.token_consume += int(token_consume['total_tokens'])
                self.completion_tokens += int(token_consume['completion_tokens'])
                self.prompt_tokens += int(token_consume['prompt_tokens'])
            else:
                # print(f"警告: 无法获取token消耗信息，token_consume格式: {type(token_consume)}")
                pass

        return self.response

    def get_response(self):
        return self.response

    def get_price(self):
        print("the price is based on gpt-3.5-turbo")
        price_prompt = 0.001089404/1000
        price_completion = 0.004357618/1000
        price_total = price_prompt*self.prompt_tokens + price_completion*self.completion_tokens
        return price_total
    
    def get_token_consume(self):
        return self.token_consume, self.completion_tokens, self.prompt_tokens


def extract_function_name(message: str):
    #从message中提取函数名称,函数名称在<pipeline></pipeline>之间
    function_name = re.search(r"<pipeline>(.*?)</pipeline>", message).group(1)
    return function_name







