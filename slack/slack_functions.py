from slack.slack_utils import get_random_thinking_message, send_slack_message_and_return_message_id, divede_sentences, run


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
    user_query = event["text"]

    print("用户输入", user_query)
    # 调用函数
    # response = try_keys(keys, user_query, prompt)

    # todo 添加用户自定义role值
    response = run('阿p', user_query, prompt)

    if response:
        print(f"成功获取回复：{response}")
    else:
        print("key失效，请修改consts.py文件中的key列表")

    # 调用分割bot回复的函数
    sentences = divede_sentences(response)
    # 将所有回复拼接成一个字符串
    combined_response = '\n'.join(sentences)

    # Replace acknowledgement message with actual response chinese: 循环用实际响应替换确认消息
    print("多段回复", combined_response)
    app.client.chat_update(
        channel=channel,
        text=combined_response,
        ts=ack_message_id,
    )
    # 回复延迟，让回复更真实
