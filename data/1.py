import re
from typing import List

def divide_sentences(text: str) -> list:
    sentences = re.split('(?<=[？！])', text)
    return [sentence for sentence in sentences if sentence]

print(divide_sentences('咦？你说什么？！喜欢我？！呃...那、那个...本小姐...本小姐也...也稍微有一点点喜欢你好了...(///ω///)'))

# print('''
# 咦？
# 你说什么？！
# 喜欢我？！
# 呃...那、那个...本小姐...本小姐也...也稍微有一点点喜欢你好了...(///ω///)
# '''
# )
