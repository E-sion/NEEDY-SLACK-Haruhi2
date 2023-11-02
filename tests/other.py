import collections
import os
import pickle
import re

import openai
from dotenv import load_dotenv

# from ChatHaruhi import ChatHaruhi


def run(role, user_prompt, system_prompt):
    # 读取key
    load_dotenv()
    os.environ.get("OPENAI_API_KEY")

    # 读取本地历史对话（如果有）
    if os.path.exists('../data/chat_history.pkl'):
        with open('../data/chat_history.pkl', 'rb') as f:
            all_dialogue_history = pickle.load(f)
            print(f' 本地聊天记忆库：{all_dialogue_history}\n')
    else:
        all_dialogue_history = []

    db_folder = 'data/characters/Girl_one'
    # system_prompt = 'file/character/system_prompt.txt'
    system_prompt = system_prompt

    chatbot = ChatHaruhi(system_prompt=system_prompt,
                         llm='openai',
                         story_db=db_folder,
                         verbose=True)

    # 在对话之前传入过往对话 并且去重
    chatbot.dialogue_history = list(collections.OrderedDict.fromkeys(all_dialogue_history))

    # 获取bot回复
    strs = chatbot.chat(role=role, text=user_prompt)

    #  对回复进行正则匹配
    regex = "「(.*?)」"
    # 使用findall()函数返回所有匹配的结果
    match = re.search(regex, strs)
    # 使用group()函数获取捕获组的内容,即回复内容
    result = match.group(1)

    # 添加聊天记录至记忆库
    all_dialogue_history.extend(chatbot.dialogue_history)
    # 将all_dialogue_history里面的内容保存至本地，作为本地聊天数据库
    with open('../data/chat_history.pkl', 'wb') as f:
        pickle.dump(all_dialogue_history, f)
    print(result)
    return result


def re_str(strs):
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
        print(result)
    elif match2:
        # 迷惑的bot发言，有时候不会添加【】，也就会导致正则报错，同时正则少部分时候也会漏掉匹配部分话。
        result = match.group(1)
        print(result)
    elif match3:
        result = match.group(1)
        print(result)
    else:
        result = strs
        print(result)

if __name__ == '__main__':
    # run('阿p', '你好', '你是一个友善的bot')
    re_str('糖糖：「你好」')
