import os

from slack.slack_utils import get_random_thinking_message, send_slack_message_and_return_message_id, divede_sentences, \
    run


def slack_respond_with_agent(event, ack, app, prompt, say):
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
    user_query = event["text"]

    print("user: ", user_query)
    # 调用函数
    # response = try_keys(keys, user_query, prompt)

    user_name = os.environ["USER_NAME"]

    # 似乎直接return的内容是一段完整的对话
    response = run(user_name, user_query, prompt)

    # todo 到底要不要添加这个功能呢？
    # 把AI的回复内容重新处理成多端对话之后再发送

    # # 调用分割bot回复的函数
    # sentences = divede_sentences(response)
    # # 将所有回复拼接成一个字符串
    # combined_response = '\n'.join(sentences)

    # Replace acknowledgement message with actual response chinese: 循环用实际响应替换确认消息
    ack()
    say(response)

    # app.client.chat_update(
    #     channel=channel,
    #     text=response,
    #     ts=ack_message_id,
    # )
