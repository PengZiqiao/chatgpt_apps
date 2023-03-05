from flask import Flask, render_template, request
from chat_api import Chat
import sys


chat = Chat()

app = Flask(__name__)

# 改写jinja模板变量的标记，防止和vuejs冲突
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send', methods=['POST'])
def send():
    # 从请求中获取JSON数据
    data = request.get_json()

    # 获得回复，并返回到前端
    content = chat(
        prompts=data['prompts'],
        temperature=data['temperature'],
        system_message=data['systemMessage'],
        few_shot_prompting=data['fewShotPrompting']
    )

    return content


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=int(sys.argv[1]))
