import os
import pickle

from dotenv import load_dotenv
from slack_bolt import App, Say
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack.slack_utils import is_dm, choose_character
from slack.slack_functions import slack_respond_with_agent

load_dotenv()
bot_token = os.environ["SLACK_BOT_TOKEN"]
app_token = os.environ["SLACK_APP_TOKEN"]
character = os.environ["CHARACTER"]

app = App(token=bot_token)

prompt = choose_character(character)


# 处理收到的 DM 消息
@app.event("message")
def handle_message_events(event, ack, say):
    if (is_dm(event)):
        slack_respond_with_agent(ack=ack, app=app, event=event, prompt=prompt, say=say)
    return


# 群聊
@app.event("app_mention")
def handle_mention(event, ack, say):
    slack_respond_with_agent(ack=ack, app=app, event=event, prompt=prompt, say=say)


#  重置当前记忆
@app.command("/reset")
def clear_chat_history(say, ack):
    with open('data/chat_history.pkl', 'wb') as f:
        pickle.dump([], f)
    ack()
    say("`已重置对话`")
    print('已重置对话')


# todo 添加人格切换
@app.command("/change")
def change_character(say, body, ack):
    ack()
    change_character = body["text"]
    # todo 未来通过更改env文件中的CHARACTER值来实现人格切换
    say(f'已切换为{change_character}')
    pass


def run_slack_app():
    SocketModeHandler(app, app_token).start()
