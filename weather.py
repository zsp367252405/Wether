import os
import sys
import requests

# 配置
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK")

DOUBAO_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL = "doubao-seed-2-0-pro-260215"  # 确认模型ID是否正确


def require_env(name: str) -> str:
    val = os.getenv(name)
    if not val or not val.strip():
        raise RuntimeError(f"Missing environment variable: {name}. Please set it in GitHub Secrets.")
    return val.strip()


def get_weather() -> str:
    api_key = require_env("DOUBAO_API_KEY")

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
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    try:
        resp = requests.post(DOUBAO_URL, headers=headers, json=data, timeout=30)
    except requests.RequestException as e:
        raise RuntimeError(f"Request to DOUBAO failed: {e}") from e

    # 非 2xx 直接失败，并打印返回体便于排查
    if not resp.ok:
        raise RuntimeError(f"DOUBAO HTTP {resp.status_code}: {resp.text}")

    # 解析 JSON
    try:
        resp_json = resp.json()
    except ValueError:
        raise RuntimeError(f"DOUBAO returned non-JSON: {resp.text}")

    # Ark 返回里有 error 也视为失败
    if isinstance(resp_json, dict) and resp_json.get("error"):
        raise RuntimeError(f"DOUBAO error: {resp_json['error']}")

    # 正常取内容
    try:
        return resp_json["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError(f"Unexpected DOUBAO response format: {resp_json}")


def send_feishu(content: str) -> None:
    webhook = require_env("FEISHU_WEBHOOK")

    msg = {
        "msg_type": "text",
        "content": {
            "text": f"🌤 厦门同安 每日天气预报（8:00-20:00）\n\n{content}"
        },
    }

    try:
        resp = requests.post(webhook, json=msg, timeout=30)
    except requests.RequestException as e:
        raise RuntimeError(f"Request to FEISHU webhook failed: {e}") from e

    if not resp.ok:
        raise RuntimeError(f"FEISHU webhook HTTP {resp.status_code}: {resp.text}")


def main():
    weather = get_weather()
    send_feishu(weather)
    print("✅ 发送成功")
    print(weather)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 运行失败: {e}", file=sys.stderr)
        sys.exit(1)
