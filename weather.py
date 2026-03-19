import requests
import os

# 配置
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK")
MODEL = "doubao-seed-2-0-pro-260215"

def get_weather():
    prompt = """
你是专业天气预报员。
请生成 厦门市同安区 大同街道 & 祥平街道 今天 08:00~20:00 逐小时天气预报。
严格按下面格式输出，不要多余文字，不要解释，只输出预报：

时间  天气  图标
使用下面固定图标，不能用其他：
晴 ☀️
多云 ⛅
阴 ☁️
晴转多云 🌤
多云转阴 🌥
小雨 🌦
中雨 🌧
大雨 🌨
雷阵雨 ⛈

只输出 08:00—20:00，逐小时一条，格式工整。
""".strip()

    headers = {
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    resp = requests.post(DOUBAO_URL, json=data, timeout=30)
    return resp.json()["choices"][0]["message"]["content"]

def send_feishu(content):
    msg = {
        "msg_type": "text",
        "content": {
            "text": f"🌤 厦门同安 每日天气预报（8:00-20:00）\n\n{content}"
        }
    }
    requests.post(FEISHU_WEBHOOK, json=msg)

if __name__ == "__main__":
    weather = get_weather()
    send_feishu(weather)
    print("✅ 发送成功")
    print(weather)
