import collections
import os
import pickle
import random
import re
import time
from typing import List, Any

from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult

from ChatHaruhi import ChatHaruhi

from consts import *
from slack_bolt import App


def is_dm(message) -> bool:
    # Check if the message is a DM by looking at the channel ID
    # chinese :  通过查看频道ID来检查消息是否为DM
    if message['channel'].startswith('D'):
        return True
    return False


def get_random_thinking_message():
    """
    正在输入中
    """
    return random.choice(thinking_thoughts_chinese)


def send_slack_message_and_return_message_id(app, channel, message: str):
    response = app.client.chat_postMessage(
        channel=channel,
        text=message)
    if response["ok"]:
        message_id = response["message"]["ts"]
        return message_id
    else:
        return "Failed to send message."


def divede_sentences(text: str) -> List[str]:
    """
    将bot的回复进行分割成多段落
    """
    sentences = re.split('(?<=[？！])', text)
    return [sentence for sentence in sentences if sentence]


def choose_character(character):
    if character == '糖糖':
        return 糖糖
    elif character == '傲娇_亚璃子':
        return 傲娇_亚璃子
    elif character == '与里':
        return
    # todo 添加更多人物


def run(role, user_prompt, system_prompt, callback):
    # 读取key
    load_dotenv()
    os.environ.get("OPENAI_API_KEY")

    # 读取本地历史对话（如果有）
    if os.path.exists('data/chat_history.pkl'):
        with open('data/chat_history.pkl', 'rb') as f:
            all_dialogue_history = pickle.load(f)
            print(f' 本地聊天记忆库：{all_dialogue_history}\n')
    else:
        all_dialogue_history = []

    db_folder = os.environ["CHARACTER_DB"]

    # system_prompt = 'file/character/system_prompt.txt'
    system_prompt = system_prompt

    chatbot = ChatHaruhi(system_prompt=system_prompt,
                         llm='openai',
                         story_db=db_folder,
                         verbose=True,
                         callback=callback
                         )

    # 在对话之前传入过往对话 并且去重
    chatbot.dialogue_history = list(collections.OrderedDict.fromkeys(all_dialogue_history))

    # 进行回复
    chatbot.chat(role=role, text=user_prompt)

    # 添加聊天记录
    all_dialogue_history.append(chatbot.dialogue_history[-1])  # 只添加最后一条记录

    # 将all_dialogue_history里面的内容保存至本地，作为本地聊天数据库
    with open('data/chat_history.pkl', 'wb+') as f:
        pickle.dump(all_dialogue_history, f)


# 去除回复中的特定符号
def remove_special_characters(text):
    if '「' or '」' in text:
        a = text.replace('「', '')
        text = a.replace('」', '')
        if ':' in text:
            result = text.split(':')[1]
        elif '：' in text:
            result = text.split('：')[1]
        else:
            result = text
    else:
        result = text
    return result


# todo 自动更换key似乎无法正常使用，换回调用env文件中设定的key值
def try_keys(keys, user_query, prompt):
    for api_key in keys:
        try:
            response = run('阿p', user_query, prompt)
            return response
        except:
            print(f"key: {api_key} 已失效，正在尝试下一个 key...")
            os.environ["OPENAI_API_KEY"] = api_key

    print("所有的 key 都失效了。")
    return None


CHAT_UPDATE_INTERVAL_SEC = 1
load_dotenv()
bot_token = os.environ["SLACK_BOT_TOKEN"]
app = App(token=bot_token)


class SlackStreamingCallbackHandler(BaseCallbackHandler):
    """
    Slack 流式输出
    """
    last_send_time = time.time()
    message = ""

    def __init__(self, channel, ts):
        self.channel = channel
        self.ts = ts
        self.interval = CHAT_UPDATE_INTERVAL_SEC
        # 投稿を更新した累計回数カウンタ
        self.update_count = 0

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.message += token
        self.message = remove_special_characters(self.message)
        now = time.time()
        if now - self.last_send_time > self.interval:
            app.client.chat_update(
                channel=self.channel, ts=self.ts, text=f"{self.message}\n\nTyping ⚙️..."
            )
            self.last_send_time = now
            self.update_count += 1

            # update_countが現在の更新間隔X10より多くなるたびに更新間隔を2倍にする
            if self.update_count / 10 > self.interval:
                self.interval = self.interval * 2

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        message_blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": self.message}},
        ]
        app.client.chat_update(
            channel=self.channel,
            ts=self.ts,
            text=self.message,
            blocks=message_blocks,
        )


if __name__ == '__main__':
    # try_keys(keys, '你好', '你是一个友善的bot')
    run('阿p', '你好', '你是一个友善的bot')
    # get_vectorstore(path='', key='', base='', save_vectorstore_name='')
    # print('测试成功')
