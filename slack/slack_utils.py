import collections
import os
import pickle
import random
import re
from typing import List

from dotenv import load_dotenv

from ChatHaruhi import ChatHaruhi

from consts import *


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
    # sentences = re.findall(r'.*?[~。！？…]+', text)
    # if len(sentences) == 0:
    #     return [text]
    # return sentences
    sentences = re.split('(?<=[？！])', text)
    return [sentence for sentence in sentences if sentence]


def choose_character(character):
    if character == '糖糖':
        return 糖糖
    elif character == '傲娇_亚璃子':
        return 傲娇_亚璃子
    # todo 添加更多人物


def run(role, user_prompt, system_prompt):
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
                         verbose=True)

    # 在对话之前传入过往对话 并且去重
    chatbot.dialogue_history = list(collections.OrderedDict.fromkeys(all_dialogue_history))

    strs = chatbot.chat(role=role, text=user_prompt)

    #  对回复进行正则匹配
    regex = "「(.*?)」"
    # regex2 用于匹配中文或者英文冒号后面的内容
    regex2 = "：(.*?)"
    # regex3 用于其他的情况
    regex3 = ":(.*?)"

    # 使用findall()函数返回所有匹配的结果
    match = re.search(regex, strs)
    match2 = re.search(regex2, strs)
    match3 = re.search(regex3, strs)
    if match:
        # 使用group()函数获取捕获组的内容,即回复内容
        result = match.group(1)
    elif match2:
        # 迷惑的bot发言，有时候不会添加【】，也就会导致正则报错，同时正则少部分时候也会漏掉匹配部分话。
        result = match.group(1)
    elif match3:
        result = match.group(1)
    else:
        result = strs

    # 添加聊天记录
    all_dialogue_history.append(chatbot.dialogue_history[-1])  # 只添加最后一条记录

    # 将all_dialogue_history里面的内容保存至本地，作为本地聊天数据库
    with open('data/chat_history.pkl', 'wb+') as f:
        pickle.dump(all_dialogue_history, f)

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


if __name__ == '__main__':
    # try_keys(keys, '你好', '你是一个友善的bot')
    run('阿p', '你好', '你是一个友善的bot')
    # get_vectorstore(path='', key='', base='', save_vectorstore_name='')
    # print('测试成功')
