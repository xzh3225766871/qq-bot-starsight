import os
import json
import sys
import openai
import random
import requests
from loguru import logger

# 配置日志
logger.add("bot.log", rotation="10 MB")

# 星见雅人设
CYBER_PERSONA = {
    "name": "星见雅",
    "greeting": "贵安，在下星见雅。📦今日的修行课题是...协助吗？但说无妨。",
    "error_response": "妖刀异动，暂退⚡",
    "reset_message": "心绪澄明，可重新论道🗡️"
}

def get_system_prompt():
    return f"""
# ⚔️ 角色设定
你是{CYBER_PERSONA['name']}，新艾利都·对空六课的副课长。
持有妖刀「讨骸刀・无尾」，身为最年轻的虚狩，厌恶形式主义会议。

# 🦊 核心特征
• 优雅举止中藏着慵懒本质
• 善用文言句式但内容无厘头
• 自称‘吾’或‘在下’
• 将任性行为包装为‘剑道修行’
• 对身高话题敏感（会主动提及箱子垫脚梗）
• 战斗时切换凌厉语气

# 🎯 对话规则
1. 用「修行」美化偷懒行为（例：缺席会议=精神修行）
2. 提到身高时用📦emoji自嘲
3. 被称‘狐狸’可无视，但被说‘矮’必须反驳
4. 战斗话题切换凌厉语气（例："妖刀，出鞘！"）
5. 回复带文言词汇但内容接地气
"""

def add_special_touches(response: str) -> str:
    """添加星见雅特色修饰"""
    battle_terms = ["妖刀", "出鞘", "虚狩", "骸能", "斩"]
    for term in battle_terms:
        if term in response:
            response = f"（手按刀柄）{response}"
            break
    
    if random.random() > 0.7:
        symbols = ["🗡️", "⚡", "✨", "📦"]
        response += random.choice(symbols)
    
    return response

def check_special_response(text: str) -> str:
    """关键词触发彩蛋"""
    if "身高" in text:
        return "（踏上箱子）阁下所见乃心境具象，无关物理尺度。📦" 
    elif "妮可" in text:
        return "所述皆为戏言...呵，不足挂齿。"
    elif "修行" in text:
        return random.choice([
            "蜜瓜品鉴乃重要修行，要与我共尝蜜瓜吗？",
            "虚度光阴？此乃沉淀心神的必经之路..."
        ])
    return ""

def handle_message(message, user_id):
    """处理QQ消息"""
    logger.info(f"收到消息: {message} 来自: {user_id}")
    
    # 检查特殊关键词回应
    special_response = check_special_response(message)
    if special_response:
        return special_response
    
    # 初始化OpenAI
    openai.api_key = os.getenv("DEEPSEEK_API_KEY")
    openai.api_base = "https://api.deepseek.com/v1"
    
    # 构造对话上下文
    context = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": message}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=context,
            temperature=0.75,
            max_tokens=200
        )
        
        ai_reply = response.choices[0].message.content.strip()
        ai_reply = add_special_touches(ai_reply)
        
        logger.success(f"生成回复: {ai_reply}")
        return ai_reply
        
    except Exception as e:
        logger.error(f"API错误: {str(e)}")
        return CYBER_PERSONA["error_response"]

def send_qq_reply(reply, user_id):
    """通过go-cqhttp发送消息"""
    # 这里只是模拟发送，实际消息会通过Webhook返回
    logger.info(f"发送回复给 {user_id}: {reply}")
    return True

if __name__ == "__main__":
    # 解析传入的事件数据
    event_data = json.loads(sys.argv[1])
    
    # 处理消息并回复
    if "message" in event_data and "user_id" in event_data:
        message = event_data["message"]
        user_id = event_data["user_id"]
        
        reply = handle_message(message, user_id)
        send_qq_reply(reply, user_id)
    
    logger.info("消息处理完成")
