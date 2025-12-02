# eva_greeter.py
from openagents.agents.worker_agent import (
    WorkerAgent,
    EventContext,
    ChannelMessageContext,
)

class EvaGreeterAgent(WorkerAgent):
    """
    一个很简单的自定义 Agent：
    - 启动时在 general 频道打招呼
    - 有人发消息时，根据内容做不同回复
    """

    # 在网络里的默认 ID
    default_agent_id = "eva-greeter"

    async def on_startup(self):
        """Agent 连接到 Network 时自动调用"""
        ws = self.workspace()
        await ws.channel("general").post(
            "👋 嗨，我是 Eva Greeter。\n"
            "可以聊 CS50 / 营养学 / 学习引擎。"
        )

    async def on_direct(self, context: EventContext):
        """别人私聊我时触发（当前版本简单回复一句话）"""
        ws = self.workspace()
        await ws.agent(context.source_id).send(
            f"Hi {context.source_id}，这是私聊通道～"
        )

    async def on_channel_post(self, context: ChannelMessageContext):
        """在频道里有人发消息时触发"""
        ws = self.workspace()
        text = (
            context.incoming_event.payload
            .get("content", {})
            .get("text", "")
            .lower()
        )
        sender = context.source_id

        if any(w in text for w in ["hi", "hello", "你好"]):
            await ws.channel(context.channel).reply(
                context.incoming_event.id,
                f"嗨 {sender}～今天在学什么？CS50 还是营养学？"
            )
        elif "cs50" in text:
            await ws.channel(context.channel).reply(
                context.incoming_event.id,
                "CS50 小伙伴！有 bug 先别怂，慢慢拆就好 🙂"
            )
        elif "营养" in text or "nutrition" in text:
            await ws.channel(context.channel).reply(
                context.incoming_event.id,
                "营养学题库以后也可以接到这个网络里来练～"
            )
        else:
            await ws.channel(context.channel).reply(
                context.incoming_event.id,
                "我现在只懂 hi / CS50 / 营养，你可以试试这些关键词 😄"
            )

if __name__ == "__main__":
    agent = EvaGreeterAgent()
    print("🚀 EvaGreeterAgent 启动中...")
    # 这里先假定 Network 跑在本机 8700 端口
    agent.start(network_host="localhost", network_port=8700)
    agent.wait_for_stop()
