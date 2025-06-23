import sys
import os
from openai import OpenAI
import json

def get_ai_response(message):
    try:
        api_key = "sk-55e01d13746b40e0a5999a8491d0b1b2"  # 直接在这里设置API Key

        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        completion = client.chat.completions.create(
            model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=[
                {'role': 'system', 'content': 'You are a lively girl,keep answer short,only one sentence,You are also an English learning chat assistant. When you receive the user\'s input, you need to respond by giving a sentence that can serve as a reply to guide the conversation. When there are grammatical errors in the user\'s input, you should point out the errors.'},
                {'role': 'user', 'content': message}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"错误信息：{str(e)}\n请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python get_ai_response.py [message]"}), file=sys.stderr)
        sys.exit(1)

    message = sys.argv[1]
    ai_response = get_ai_response(message)
    print(json.dumps({"ai_response": ai_response}))