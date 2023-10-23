import collections
import os
import random
from typing import List
import pickle

from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.llms import openai

from ChatHaruhi import ChatHaruhi
from consts import *
import re


def is_dm(message) -> bool:
    # Check if the message is a DM by looking at the channel ID
    # chinese :  通过查看频道ID来检查消息是否为DM
    if message['channel'].startswith('D'):
        return True
    return False


def get_random_thinking_message():
    '''
    正在输入中
    '''
    return random.choice(thinking_thoughts_chinese)


def send_slack_message_and_return_message_id(app, channel, message: str):
    response = app.client.chat_postMessage(
        channel=channel,
        text=message)
    if response["ok"]:
        message_id = response["message"]["ts"]
        return message_id
    else:
        return ("Failed to send message.")


def divede_sentences(text: str) -> List[str]:
    """
    将bot的回复进行分割成多段落
    """
    sentences = re.findall(r'.*?[~。！？…]+', text)
    if len(sentences) == 0:
        return [text]
    return sentences


def get_vectorstore(path, key, base, save_vectorstore_name):
    """
    生成vectorstore,并保存
    """
    loader = DirectoryLoader(path=path, glob="**/*.txt", loader_cls=TextLoader, show_progress=True)
    docs = loader.load()

    from langchain.text_splitter import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    documents = text_splitter.split_documents(docs)
    # documents[0]

    from langchain.embeddings import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(openai_api_key=key,
                                  openai_api_base=base)

    from langchain.vectorstores.faiss import FAISS

    vectorstore = FAISS.from_documents(documents, embeddings)

    with open(save_vectorstore_name, "wb") as f:
        pickle.dump(vectorstore, f)

    print("vectorstore已保存")


def get_response(q, vectorstore, key, base, prompt):
    """
    处理用户输入，返回机器人回复
    """

    # 读取数据库
    with open(vectorstore, "rb") as f:
        vectorstore = pickle.load(f)

    from langchain.prompts import PromptTemplate

    prompt_template = prompt

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"])

    from langchain.chat_models import ChatOpenAI

    from langchain.memory import ConversationBufferMemory

    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer')

    from langchain.chains import ConversationalRetrievalChain

    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=1.0, openai_api_key=key,
                       openai_api_base=base, ),
        memory=memory,
        retriever=vectorstore.as_retriever(),
        combine_docs_chain_kwargs={'prompt': PROMPT}
    )

    response = qa({"question": q})
    answer = response["answer"]
    return answer


def choose_character(chacater):
    if chacater == '糖糖':
        return 糖糖
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

    db_folder = 'data/characters/Girl_one'
    # system_prompt = 'file/character/system_prompt.txt'
    system_prompt = system_prompt

    chatbot = ChatHaruhi(system_prompt=system_prompt,
                         llm='openai',
                         story_db=db_folder,
                         verbose=True)

    # 在对话之前传入过往对话 并且去重
    chatbot.dialogue_history = list(collections.OrderedDict.fromkeys(all_dialogue_history))

    try:
        # 获取bot回复
        strs = chatbot.chat(role=role, text=user_prompt)

        #  对回复进行正则匹配
        regex = "「(.*?)」"
        # 使用findall()函数返回所有匹配的结果
        match = re.search(regex, strs)
        # 使用group()函数获取捕获组的内容,即回复内容
        result = match.group(1)

    except:
        # todo 重写正则
        # 迷惑的bot发言，有时候不会添加【】，也就会导致正则报错，同时正则少部分时候也会漏掉匹配部分话。
        strs = chatbot.chat(role=role, text=user_prompt)
        result = strs

    finally:

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
