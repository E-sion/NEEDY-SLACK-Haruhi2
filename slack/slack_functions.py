import os
import re

from slack.slack_utils import get_random_thinking_message, send_slack_message_and_return_message_id, divede_sentences, \
    run, SlackStreamingCallbackHandler


def slack_respond_with_agent(event, ack, app, prompt):
    """
    This function takes a Slack message event and respond with a LLM-generated response
    chinese:  该函数接受Slack消息事件，并使用LLM生成的响应进行响应
    """

    channel = event["channel"]

    # Acknowledge user's message chinese:  确认用户的消息
    ack()
    ack_message_id = send_slack_message_and_return_message_id(
        app=app, channel=channel, message=get_random_thinking_message())

    # Generate an LLM response using agent chinese:  使用代理生成LLM响应
    if "@" in event["text"]:
        user_query = re.sub("<@.*>", "", event["text"])
    else:
        user_query = event["text"]
    print("user: ", user_query)

    user_name = os.environ["USER_NAME"]
    callback = SlackStreamingCallbackHandler(ts=ack_message_id, channel=channel)
    run(user_name, user_query, prompt, callback)
