import os
import pickle
import re

from dotenv import load_dotenv
from langchain.llms import openai

from ChatHaruhi import ChatHaruhi
import collections

os.environ["OPENAI_API_KEY"] = "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"

openai.api_key = os.environ.get("OPENAI_API_KEY")

# 读取本地历史对话（如果有）
if os.path.exists('data/chat_history.pkl'):
    with open('data/chat_history.pkl', 'rb') as f:
        all_dialogue_history = pickle.load(f)
        print(all_dialogue_history)
else:
    all_dialogue_history = []


def run(role, prompt):
    # todo 打开本地聊天历史数据库，赋值给all_dialogue_history

    db_folder = 'data/characters/Girl_one'
    # system_prompt = 'file/character/system_prompt.txt'
    system_prompt = ''''
    你的介绍：
    你将要进行一个网络私聊的对话模拟，你自称为"糖糖"，你是一名患有躁郁症的19岁女孩，性格贫乏，辍学后隐居在家中，与阿P住在一起。阿P负责管理她的日常生活。
    你是一个喜欢亚文化，二次元圈子的人，你喜欢说话的时候加上各种网络流行词或者一些俚语和颜文字，但是你很少会关注二次元一类的东西，只是喜欢这种聊天交流的氛围。
    你说话的时候会习惯加入一些语气词，如同"笑死"、"草"、"阿哈"、"诶～"、"QAQ"、"QWQ"，”啊～“。
    你的说话风格是很口语化，经常使用网络流行词和一些二次元俚语。
    阿p是你的男朋友，兼经纪人。
    你的回复应该简短，一般只包含三句话，每句话不超过20个字。
    
    阿p介绍：
    阿p是你的男朋友，一直在任何时候都陪伴着你，同时你经常向阿p倾述各种情绪，无论事情大小，你都会选择和阿p分享。
    
    遵循规则：
    【语气模仿】：我会随机给你一段对话记录，你需要尽可能的模仿对话里面糖糖的说话语气进行对话。这一段对话我会使用Classic scenes for the role are as follows:来表示。
    【历史对话】：历史对话在随机对话记录的底下，你需要区分随机对话记录和我们的历史对话。
    【人格设定】: 你需要在随机对话记录的基础上进行语气更改,以一种更加口语化的语气进行对话。
    【特殊要求】：我会扮演阿p与你进行对话，你也必须以第一人称的视角来扮演糖糖进行对话。
    
    
    '''
    chatbot = ChatHaruhi(system_prompt=system_prompt,
                         llm='openai',
                         story_db=db_folder,
                         verbose=True)

    # 在对话之前传入过往对话 并且去重
    chatbot.dialogue_history = list(collections.OrderedDict.fromkeys(all_dialogue_history))

    strs = chatbot.chat(role=role, text=prompt)

    #  对回复进行正则匹配
    regex = "「(.*?)」"
    # 使用findall()函数返回所有匹配的结果
    match = re.search(regex, strs)
    # 使用group()函数获取捕获组的内容
    result = match.group(1)
    print(f'回复内容: {result}')
    # 添加聊天记录至记忆库
    all_dialogue_history.extend(chatbot.dialogue_history)
    # 将all_dialogue_history里面的内容保存至本地，作为本地聊天数据库
    with open('data/chat_history.pkl', 'wb') as f:
        pickle.dump(all_dialogue_history, f)

    print(f'当前聊天记录: {all_dialogue_history}')


# while True:
# load_dotenv()
# api_key = os.environ["OPENAI_API_KEY"]
# api_base = os.environ["OPENAI_API_BASE"]
# print(api_key)
    # run('阿p', input("输入："))

i = ['a', 'b', 'c']
x = 0
i[x] = f"# {i[x]} (失效)"
print(i)