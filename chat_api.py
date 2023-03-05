import openai
import os

# 对prompts进行切片，保留最后几项以控制总字符串长度


def slice_prompts(prompts):
    # 初始化变量，记录 prompts 列表中的消息内容的总长度、子列表的起始索引
    total_length = 0
    start_index = -1

    # 使用 reversed 函数对 prompts 列表进行反向迭代，从最后一条消息开始遍历
    for message in reversed(prompts):
        # 把当前消息的内容的长度累加到 total_length 变量上
        total_length += len(message["content"])
        # 如果 total_length 变量大于 3000，就跳出循环
        if total_length > 2000:
            break
        start_index -= 1
    # 返回 prompts 倒数start_index-1位
    return prompts[start_index:]

# 定义一个装饰器，用来处理prompts


def handle_prompts(func):
    def wrapper(self, prompt):
        # 将用户输入作为消息字典添加到self.prompts列表中
        self.prompts.append({
            "role": "user",
            "content": prompt
        })

        # 调用原始方法获取回复内容
        content = func(self, prompt)

        # 将回复内容作为消息字典添加到self.prompts列表中
        self.prompts.append({
            "role": "assistant",
            "content": content
        })

        # 对prompts进行切片，控制字符长度
        self.prompts = slice_prompts(self.prompts)

        return content

    return wrapper

# 定义一个session类，有相对固定的system_massag、temperature，调用时接受一个prompt，调用后会拼接记录prompts（见handle_prompts）


class SessionChat:
    def __init__(self):
        # 设置openai的api密钥，从环境变量中获取
        openai.api_key = os.environ['OPENAI_API_KEY']

        # 初始化一些参数
        self.system_massage = {
            "role": "system",
            "content": "You are a helpful assistant."
        }
        self.prompts = []
        self.temperature = 0.5

    @handle_prompts
    def __call__(self, prompt):
        # 调用openai的ChatCompletion接口，传入self.prompts作为消息列表
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=[
                                                    self.system_massage] + self.prompts,
                                                temperature=self.temperature)

        # 获取返回结果中的回复内容
        content = response['choices'][0]['message']['content']

        return content

    def change_system_content(self, content):
        # 修改role为system的消息字典
        self.system_massage["content"] = content

    def clean_prompts(self):
        # 清空self.prompts列表
        self.prompts = []

# 定义一个Chat类，每次调用接收全量prompts，可自定义system_message、temperature传入


class Chat:
    def __init__(self):
        openai.api_key = os.environ['OPENAI_API_KEY']

    def __call__(self, prompts, temperature=0, system_message=None, few_shot_prompting=None):
        # 如果有 few_shot_prompting 参数，就把它到 prompts 列表前面
        if few_shot_prompting:
            prompts = few_shot_prompting + prompts

        # 如果有 system_message 参数，就把它作为第一个消息添加到 prompts 列表中
        if system_message:
            prompts = [{'role': 'system', 'content': system_message}] + prompts

        # 对prompts进行切片，控制字符长度
        prompts = slice_prompts(prompts)

        # 使用 openai 的 ChatCompletion 方法
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompts,
            temperature=temperature
        )
        # 从响应中获取第一个选择的消息的内容，并返回
        content = response['choices'][0]['message']['content']
        return content


if __name__ == '__main__':
    # python 打开这个文件时，可以在命令行和chatgpt对话
    chat = SessionChat()

    while True:
        prompt = input("You: ")
        print("AI: " + chat(prompt))
