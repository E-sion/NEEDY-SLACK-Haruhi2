import os
from dotenv import load_dotenv
from slack_bolt import App
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
def handle_message_events(event, ack):
    if (is_dm(event)):
        slack_respond_with_agent(ack=ack, app=app, event=event, prompt=prompt)

    return

# todo 未来添加更多功能

# @app.event("app_mention")
# def handle_mention(event, ack):
#     slack_respond_with_agent(ack=ack, app=app, event=event, key=api_key, base=api_base,
#                              vectorstore=vectorstore)

#
# @app.command("/upload-new-doc")
# def handle_document_upload(body, say, ack):
#     ack()
#     value = body['text']
#
#     # If user didn't include a URL or URLs, then abort chinese:  如果用户没有包含URL或URL，则中止
#     if (value == "" or value is None):
#         say("Please enter a valid URL to the document!")
#         return
#
#     say("I'm uploading a new document! :arrow_up:")
#
#     # Load the URLs into vectorstore chinese:  将URL加载到vectorstore中
#     load_urls_and_overwrite_index(value)
#
#     say("I'm done uploading the document! :white_check_mark:")


def run_slack_app():
    SocketModeHandler(app, app_token).start()


