# drug_food_agent.py
"""
Drug–Food Interaction Coach · 药物–饮食互动教练 Agent (单 Agent 版本 v0.1)

说明：
- 本 Agent 仅用于演示与教育目的，不提供医疗诊断或治疗建议。
- 不会调整药量、不建议停药/换药，所有用药决策必须由医生/药师做出。
- 目前仅针对「左旋多巴」和「华法林」做了比较细的示例逻辑，
  其他药物只做非常粗略、宽松的提醒。
"""

from typing import Dict, Any

from openagents.agents.worker_agent import (
    WorkerAgent,
    EventContext,
    ChannelMessageContext,
)


def make_empty_session(drug_name: str = "") -> Dict[str, Any]:
    """初始化一个会话画像（session state）。"""
    return {
        "step": 0,                 # 当前问诊阶段
        "main_drug": drug_name,    # 重点药物（左旋多巴 / 华法林）
        "drug_list": [],           # 处方药大类/名称
        "supplements": [],         # 补充剂/保健品
        "dosing_pattern": "",      # 用药时间模式
        "diet_pattern_rough": "",  # 粗略饮食习惯
        "drinks_pattern": "",      # 饮料习惯（咖啡/茶/果汁/酒精）
        "safety_flags": [],        # 高风险标记（暂留）
        "user_concerns": [],       # 用户特别关注点
    }


class DrugFoodCoachAgent(WorkerAgent):
    """单 Agent 版本：药物–饮食互动教练."""

    default_agent_id = "drug-food-coach"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 以 "source_id:channel" 作为 key 维护一个简单的会话状态
        self.sessions: Dict[str, Dict[str, Any]] = {}

    # ---------- 工具方法 ----------

    def _session_key(self, source_id: str, channel: str) -> str:
        return f"{source_id}:{channel}"

    def _get_session(self, source_id: str, channel: str) -> Dict[str, Any]:
        key = self._session_key(source_id, channel)
        if key not in self.sessions:
            self.sessions[key] = make_empty_session()
        return self.sessions[key]

    def _reset_session(self, source_id: str, channel: str) -> None:
        key = self._session_key(source_id, channel)
        self.sessions[key] = make_empty_session()

    # ---------- 生命周期回调 ----------

    async def on_startup(self):
        """连接 Network 后，在 general 频道打一个总招呼。"""
        ws = self.workspace()
        await ws.channel("general").post(
            "👋 嗨，我是 **药物–饮食互动教练 Agent**。\n\n"
            "我不负责改药，只帮你从**饮食/饮料角度**，看看正在吃的药有没有典型注意点。\n"
            "目前重点支持：**左旋多巴、华法林** 两个示例。\n\n"
            "你可以直接说：\n"
            "• `我在吃左旋多巴`\n"
            "• `我在吃华法林`\n"
            "我会一步一步问你情况，再给你一张“药物–饮食互动卡”。\n\n"
            "随时可以发送 `重来` 或 `reset` 从头开始。"
        )

    async def on_direct(self, context: EventContext):
        """私聊时简单说明自己在做什么，并引导去频道体验。"""
        ws = self.workspace()
        await ws.agent(context.source_id).send(
            "这里是药物–饮食互动教练 Agent 的私聊通道。\n\n"
            "目前主要功能是在频道里演示，你可以在某个频道中发送：\n"
            "`我在吃左旋多巴` 或 `我在吃华法林`，我会一步一步帮你梳理饮食注意点。"
        )

    async def on_channel_post(self, context: ChannelMessageContext):
        """核心对话逻辑：多轮问诊 + 风险卡输出。"""
        ws = self.workspace()
        payload = context.incoming_event.payload
        text = payload.get("content", {}).get("text", "").strip()
        text_lower = text.lower()
        source_id = context.source_id
        channel = context.channel

        # 重置指令
        if text in ("重来", "reset", "重新开始"):
            self._reset_session(source_id, channel)
            await ws.channel(channel).reply(
                context.incoming_event.id,
                "好的，我们从头开始。\n\n"
                "你可以先告诉我：\n"
                "• `我在吃左旋多巴`\n"
                "• `我在吃华法林`\n"
                "目前我对这两个药的饮食注意点准备得比较完整。"
            )
            return

        session = self._get_session(source_id, channel)

        # 如果还没有 main_drug，尝试从用户输入中识别
        if session["step"] == 0 and not session["main_drug"]:
            detected = None
            if "左旋多巴" in text:
                detected = "左旋多巴"
            elif "华法林" in text:
                detected = "华法林"

            if not detected:
                await ws.channel(channel).reply(
                    context.incoming_event.id,
                    "目前我对以下药物的饮食注意点准备得比较完整：\n"
                    "• 左旋多巴\n"
                    "• 华法林\n\n"
                    "你可以先说：`我在吃左旋多巴` 或 `我在吃华法林`。\n"
                    "如果是其他药物，我也可以给非常粗略、宽松的饮食提醒，但不会给细节。"
                )
                return

            # 识别到重点药物，初始化画像
            session.update(make_empty_session(detected))
            session["drug_list"].append(detected)
            session["step"] = 1

            # 开场说明 & 边界
            if detected == "左旋多巴":
                intro = (
                    "你提到的是 **左旋多巴**，常用于治疗帕金森相关的运动症状。\n\n"
                    "接下来我会：\n"
                    "1）先了解你现在大概在吃哪些药和补充剂；\n"
                    "2）再了解用药时间和吃饭/喝东西的节奏；\n"
                    "3）最后给你一张“左旋多巴–饮食/饮料互动卡”。\n\n"
                    "我不会改药，只从**饮食和生活方式**角度给建议，重要调整请一定和医生/药师确认。"
                )
            else:  # 华法林
                intro = (
                    "你提到的是 **华法林**，是一类抗凝药，用来预防或治疗血栓。\n\n"
                    "接下来我会：\n"
                    "1）先了解你现在大概在吃哪些药和补充剂；\n"
                    "2）再了解用药时间和吃饭/喝东西的节奏；\n"
                    "3）最后给你一张“华法林–饮食/饮料互动卡”。\n\n"
                    "我不会改药，只从**饮食和生活方式**角度给建议，重要调整请一定和医生/药师确认。"
                )

            q = (
                "\n\n我们先从处方药开始：\n"
                "👉 你现在**长期在吃的处方药**，大概有哪些？\n"
                "可以说商品名（比如 XX 片），也可以用“降压药、降糖药、他汀、抗凝药”这种描述。\n"
                "能想起几个说几个就好，后面想起来还可以补充。"
            )

            await ws.channel(channel).reply(
                context.incoming_event.id,
                intro + q,
            )
            return

        # 已经有 main_drug，按 step 走多轮流程
        step = session["step"]
        main_drug = session["main_drug"]

        # STEP 1：收集其他处方药
        if step == 1:
            if text:
                session["drug_list"].append(text)
            session["step"] = 2

            msg = (
                "好的，我先粗略记下你提到的处方药情况：\n"
                f"- 重点药物：{main_drug}\n"
                f"- 你描述的其他药物/大类：{text or '（未额外提供）'}\n\n"
                "下一步，我想了解一下**补充剂/保健品**这块：\n"
                "👉 你现在有没有比较固定在吃的：\n"
                "- 钙片 / 维D\n"
                "- 多种维生素\n"
                "- 鱼油 / 辅酶 Q10\n"
                "- 中成药 / 草本保健品\n"
                "- 其他保健品\n\n"
                "记不住名字没关系，可以先说类型，比如“钙+维D、多维、某某牌子的护肝保健品”等。"
            )
            await ws.channel(channel).reply(context.incoming_event.id, msg)
            return

        # STEP 2：收集补剂/保健品
        if step == 2:
            if text:
                session["supplements"].append(text)
            session["step"] = 3

            msg = (
                "收到，我先帮你记录：\n"
                f"- 处方药（你目前提到）：{'; '.join(session['drug_list'])}\n"
                f"- 补充剂/保健品：{text or '（未提供具体补充剂信息）'}\n\n"
                "接下来我想了解一下 **吃药和吃饭、喝东西的时间关系**，不需要很精确的时间点：\n"
                "👉 你可以大致说一下：\n"
                f"1）**{main_drug}** 一般是在一天的什么时间吃？是和饭前/饭后绑定，还是固定在某个时间？\n"
                "2）其他药大概是饭前 / 饭后 / 睡前？\n"
                "3）平时有没有比较固定爱喝的东西，比如：\n"
                "   - 咖啡、茶、功能饮料\n"
                "   - 果汁（尤其是西柚/葡萄柚汁）\n"
                "   - 酒精饮品（啤酒、红酒、白酒等）"
            )
            await ws.channel(channel).reply(context.incoming_event.id, msg)
            return

        # STEP 3：收集用药时间 + 饮料习惯
        if step == 3:
            session["dosing_pattern"] = text
            # 简单分拆：把饮料习惯粗放放进一个字段
            session["drinks_pattern"] = text
            session["step"] = 4

            summary = (
                "好的，我先按你的描述，做一个简短的“当前画像”小结：\n"
                f"- 处方药：{'; '.join(session['drug_list'])}\n"
                f"- 补充剂/保健品：{'; '.join(session['supplements']) or '未特别提及'}\n"
                f"- 用药 & 饮料习惯：{text or '（你刚才这轮没有具体描述）'}\n\n"
                "下面我会先给你一张 **“药物–饮食/饮料互动卡（总览版）”**，\n"
                "让你知道在目前你告诉我的基础上，饮食/饮料的重点注意大概在哪些块。\n"
            )

            if main_drug == "左旋多巴":
                card = build_card_for_levodopa(session)
            elif main_drug == "华法林":
                card = build_card_for_warfarin(session)
            else:
                card = build_card_for_generic(session)

            tail = (
                "\n如果你之后愿意更具体一点，比如告诉我：\n"
                "- 每天几乎必吃/必喝的某一两样东西，\n"
                "我可以在这张总览卡的基础上，针对那一两样再说细一点的“怎么错开/怎么调整”。\n\n"
                "⚠️ 再重复一次：我这边所有建议，都是从营养/生活方式角度出发，\n"
                "不能代替你的医生/药师的判断。任何重要调整，请一定先和他们确认。"
            )

            await ws.channel(channel).reply(
                context.incoming_event.id,
                summary + "\n" + card + tail,
            )
            # 保持 step=4，不再自动问问题，等待用户是否提具体食物/饮料
            return

        # STEP >= 4：用户可能提更具体的食物/饮料，这里简单给一个补充回答
        if step >= 4:
            # 这里先做一个非常简单的补充：根据 main_drug + 用户提到的关键词给点提示
            extra_reply = build_followup_for_specific_food(main_drug, text)
            await ws.channel(channel).reply(
                context.incoming_event.id,
                extra_reply
            )
            return


# ---------- 构建“互动卡”内容的辅助函数 ----------

def build_card_for_levodopa(session: Dict[str, Any]) -> str:
    """左旋多巴的饮食/饮料互动卡（总览版）。"""
    dosing = session.get("dosing_pattern", "")
    drinks = session.get("drinks_pattern", "")

    text = []
    text.append("🧾 **左旋多巴 – 饮食/饮料互动卡（总览版）**\n")

    text.append("**一、药物信息简述**")
    text.append(
        "左旋多巴常用于治疗帕金森相关的运动症状。\n"
        "它需要被吸收到血液，再进入大脑发挥作用。"
    )

    text.append("**二、总体风险大致在几块：**")
    text.append(
        "- 和 **蛋白质/高蛋白餐** 的关系\n"
        "- 和 **正常三餐节奏** 的关系\n"
        "- 和 **咖啡、茶、果汁（特别是柚子类）、酒精** 的关系\n"
    )

    text.append("**1️⃣ 和蛋白质/高蛋白餐的关系**")
    text.append(
        "部分氨基酸和左旋多巴在肠道吸收、进入大脑时会“抢通道”，\n"
        "如果在非常高蛋白的一餐旁边（大量肉类、蛋、蛋白粉奶昔）服用左旋多巴，\n"
        "有可能让药效出现波动，或者效果略打折。"
    )
    text.append(
        "👉 建议可以这样折中：\n"
        "- 尽量在**相对空腹或轻食**时服用左旋多巴；\n"
        "- 把一天里蛋白最集中的那顿饭，安排在离服药稍远一点的时间；\n"
        "- 避免每次服药都刚好叠在当天蛋白最高的一餐上。"
    )

    text.append("**2️⃣ 和日常三餐节奏的关系**")
    text.append(
        "现实生活中不一定总能做到完全空腹，所以更实用的原则是：\n"
        "- 如果已经习惯“饭后立刻吃药”，不必一下子全部推翻；\n"
        "- 但可以尝试：让靠近左旋多巴的那一餐，\n"
        "  不要是你当天最夸张的一顿高蛋白大餐。"
    )
    if dosing:
        text.append(f"你刚才对用药时间的描述是：{dosing}")

    text.append("**3️⃣ 和咖啡、茶、果汁（尤其柚子类）、酒精的关系**")
    text.append(
        "- 就左旋多巴本身而言，主要关注点仍然是“和高蛋白餐的关系”；\n"
        "- 咖啡/茶：更多是对神经系统兴奋、睡眠的影响，尤其要注意晚间用药时不要叠加太多咖啡因；\n"
        "- 酒精：大量饮酒会影响神经系统和跌倒风险，也常常和其他药物叠加风险，\n"
        "  所以整体建议是：**少量、偶尔，而不是每天大量喝**。"
    )
    if "柚" in drinks or "葡萄柚" in drinks or "西柚" in drinks:
        text.append(
            "- 你提到了柚子/葡萄柚汁：这类饮品对部分他汀、心血管药的影响更值得注意，\n"
            "  建议你把“当前用的具体他汀 + 柚子类果汁”的问题，带去问医生/药师确认。"
        )

    text.append("**4️⃣ 一条总生活方式原则**")
    text.append(
        "对左旋多巴来说，吃饭和用药的搭配可以记两个关键词：\n"
        "- **“错峰”**：尽量把特别高蛋白的那一餐错开到离服药远一点的时间；\n"
        "- **“稳定”**：不要一阵子极高蛋白，一阵子又几乎不吃蛋白，让药效的环境忽高忽低。"
    )

    text.append(
        "⚠️ 如果你还有其他没有提到的药物（尤其是抗抑郁、抗精神类药、镇静药等），\n"
        "或者有肝肾功能问题、跌倒风险偏高，这些都需要由医生综合判断。\n"
        "我这边的建议只能当作一般性参考，不适合当作唯一依据。"
    )

    return "\n".join(text)


def build_card_for_warfarin(session: Dict[str, Any]) -> str:
    """华法林的饮食/饮料互动卡（总览版）。"""
    dosing = session.get("dosing_pattern", "")
    drinks = session.get("drinks_pattern", "")

    text = []
    text.append("🧾 **华法林 – 饮食/饮料互动卡（总览版）**\n")

    text.append("**一、药物信息简述**")
    text.append(
        "华法林是一类抗凝药，用来预防或治疗血栓。\n"
        "它的效果和血液中某些凝血因子，以及**维生素 K 摄入的稳定性**关系比较大。"
    )

    text.append("**二、总体风险大致在几块：**")
    text.append(
        "- 和 **深绿色叶菜/富含维生素 K 食物** 的关系\n"
        "- 和 **维生素补充剂、草本保健品** 的关系\n"
        "- 和 **酒精、果汁（尤其柚子类）、咖啡/茶** 的关系\n"
    )

    text.append("**1️⃣ 和深绿色叶菜、维生素 K 食物的关系**")
    text.append(
        "菠菜、羽衣甘蓝、芥蓝、韭菜、香菜、部分深绿叶类蔬菜，维生素 K 会比较多一些。\n"
        "对华法林来说，重点不是“这些菜绝对不能吃”，而是：\n"
        "👉 **“尽量保持摄入的习惯稳定”，避免一阵子猛吃，一阵子又完全不吃。**"
    )
    text.append(
        "日常可以这样理解：\n"
        "- 如果你平时每天都吃一点绿叶菜，医生在这个前提下调整好了华法林剂量，\n"
        "  那就不要突然把所有绿叶菜统统停掉；\n"
        "- 如果你过去很少吃深绿叶菜，也不要突然开始每天大量补。\n"
        "- 一旦你打算做大的饮食改变（比如减肥、素食、特别强化某些菜），\n"
        "  一定要提前和医生说，让他们考虑是否需要重新评估用药。"
    )

    text.append("**2️⃣ 和维生素补充剂、草本保健品的关系**")
    text.append(
        "你如果有在吃多种维生素、草本保健品、某些“护肝护血管”的产品：\n"
        "- 有些多维产品会含一定量的维生素 K；\n"
        "- 草本/保健品可能通过肝脏代谢间接影响华法林效果。\n"
        "关键点同样是：**在医生知情的前提下保持“配方和剂量的稳定”**。"
    )

    text.append("**3️⃣ 和果汁（尤其柚子类）、酒精、咖啡/茶的关系**")
    text.append(
        "- 葡萄柚/西柚汁对部分药物（例如某些他汀、心血管用药）的代谢酶影响比较典型；\n"
        "- 对华法林来说，更需要注意的是**酒精摄入和整体肝功能状态**：\n"
        "  较大量、长期饮酒会改变肝脏代谢，从而影响华法林效果和出血风险；\n"
        "- 咖啡/茶主要影响神经系统、心率和睡眠，通常不是华法林最核心的饮食矛盾，\n"
        "  但大量咖啡因叠加其他心血管用药，也需要医生综合评估。"
    )
    if any(k in drinks for k in ["葡萄柚", "西柚", "柚子"]):
        text.append(
            "你提到了柚子/葡萄柚汁：\n"
            "- 它们对**他汀/部分心血管药物**的相互作用更值得注意；\n"
            "- 建议你把“当前用的具体他汀 + 柚子类果汁”的问题，带去问医生/药师确认。"
        )
    if any(k in drinks for k in ["酒", "红酒", "白酒", "啤酒"]):
        text.append(
            "你也提到了酒精：\n"
            "- 对正在用华法林的人来说，**频繁大量饮酒**会明显增加风险；\n"
            "- 即使是少量、偶尔，也建议在医生了解你真实饮酒习惯的前提下，再共同评估。"
        )

    text.append("**4️⃣ 一条总生活方式原则**")
    text.append(
        "对华法林这类药，饮食/饮料的关键可以记两个词：\n"
        "- **“稳定”**：让你的饮食结构、用药时间、补剂选择尽量平稳、可预期，而不是忽左忽右；\n"
        "- **“先问一声”**：在你打算做大幅度饮食变化、增加新保健品、改变喝酒习惯之前，\n"
        "  尽量先和医生/药师确认。"
    )
    if dosing:
        text.append(f"你刚才对用药和吃饭/喝东西的描述是：{dosing}")

    text.append(
        "⚠️ 如果你还有其他没有提到的药物（特别是抗凝类、抗排斥、抗肿瘤药等），\n"
        "或者有肝肾功能问题、怀孕/哺乳期，这些都需要由医生来判断整体方案。\n"
        "我这边的建议只能当作一般性参考，不适合当作唯一依据。"
    )

    return "\n".join(text)


def build_card_for_generic(session: Dict[str, Any]) -> str:
    """默认/未知药物时的非常宽松的一般性提示。"""
    drugs = "; ".join(session.get("drug_list") or []) or "（你尚未详细提供药物名称）"
    text = []
    text.append("🧾 **药物–饮食/饮料互动卡（通用版）**\n")
    text.append("你目前提到正在使用的药物/大类：")
    text.append(f"- {drugs}\n")
    text.append(
        "由于我对这些药物的详细信息和相互作用数据掌握有限，\n"
        "暂时只能给出非常宽松的一般性饮食/生活方式提醒："
    )
    text.append(
        "- 尽量保持**规律、均衡**的饮食结构，不要忽然极端节食或暴饮暴食；\n"
        "- 酒精、能量饮料、极端高剂量的补剂（尤其是草本、来路不明的保健品）要格外谨慎；\n"
        "- 在没有医生指导的情况下，不要因为“网上说某种东西有益/有害”就突然大量增加或完全停掉。"
    )
    text.append(
        "最重要的是：\n"
        "- 把你目前所有药物、补剂和典型饮食习惯，整理成一张纸，\n"
        "  在门诊时交给熟悉你的医生/药师，他们可以结合你的病史和检查结果，\n"
        "  给出更有针对性的建议。"
    )
    text.append(
        "⚠️ 本工具的输出不能作为任何用药调整的根据，所有重要决策请以医生/药师判断为准。"
    )
    return "\n".join(text)


def build_followup_for_specific_food(main_drug: str, user_text: str) -> str:
    """当用户在后续回合提到具体食物/饮料时，给一点附加说明。"""
    t = user_text

    # 非常简单、关键词驱动的补充逻辑
    if main_drug == "左旋多巴":
        if any(k in t for k in ["蛋白粉", "奶昔", "高蛋白", "肉", "牛排", "鸡胸"]):
            return (
                "你提到和左旋多巴比较靠近的高蛋白食物/饮品（比如你说的这些："
                f"`{user_text}`）。\n\n"
                "从原理上看，高蛋白餐有可能和左旋多巴在吸收/进入大脑时形成一定竞争，\n"
                "所以更安全的做法是：\n"
                "- 尝试把左旋多巴安排在离这类高蛋白摄入稍远一点的时间（比如提前 30 分钟）；\n"
                "- 或者把蛋白最集中的那一餐挪到不和用药完全重叠的时间段。\n\n"
                "具体调整幅度，建议你结合医生的意见和自己的生活节奏，一点一点微调。\n"
                "任何明显的症状变化，都需要尽快反馈给医生。"
            )
        if any(k in t for k in ["柚", "葡萄柚", "西柚", "红酒", "酒"]):
            return (
                "关于你提到的这些饮料："
                f"`{user_text}`。\n\n"
                "对左旋多巴本身来说，最核心的矛盾仍然在于“和高蛋白餐的关系”，\n"
                "但柚子类果汁、酒精往往会和**他汀/心血管药物/肝功能**一起构成整体风险。\n\n"
                "建议你把当前的用药清单 + 你的饮酒/柚子饮料习惯，用纸或电子方式整理好，\n"
                "在下一次门诊时专门请医生/药师帮你一起看一遍。"
            )

    if main_drug == "华法林":
        if any(k in t for k in ["菠菜", "青菜", "芥蓝", "羽衣甘蓝", "绿叶菜", "韭菜", "香菜"]):
            return (
                "你提到你特别在意这类深绿色叶菜："
                f"`{user_text}`。\n\n"
                "对正在使用华法林的人来说，关键不是“从此不能吃”，而是：\n"
                "👉 不要从“几乎不吃”突然跳到“每天大量吃”，也不要相反。\n\n"
                "比较稳妥的方式是：\n"
                "- 在医生知情的前提下，逐渐把一个你能接受的“每天适量蔬菜”模式稳定下来；\n"
                "- 同时配合医生安排的凝血指标监测，来判断需不需要调整剂量。\n\n"
                "简单说：**可以吃，但要稳定，在医生知道的前提下吃。**"
            )
        if any(k in t for k in ["葡萄柚", "西柚", "柚子", "酒", "红酒", "白酒", "啤酒"]):
            return (
                "你提到的："
                f"`{user_text}`，\n"
                "这类饮料在“华法林 + 他汀/心血管用药”的组合里确实值得认真对待。\n\n"
                "- 葡萄柚/西柚汁：更典型的是和某些他汀/心血管药物的代谢酶相互作用；\n"
                "- 酒精：长期/大量饮酒会显著增加出血和肝脏风险。\n\n"
                "建议你把：\n"
                "1）所有正在吃的药物名字；\n"
                "2）你真实的饮酒频率和喜欢喝的饮料；\n"
                "整理成一份小清单，在门诊时交给医生/药师，他们可以结合你的凝血指标、肝功能，\n"
                "给出更具体的“可以喝多少、怎么喝比较安全”的建议。"
            )

    # 没匹配到更细粒度，就给一个通用的补充说明
    return (
        "我听到了你提到的这些具体吃的/喝的东西："
        f"`{user_text}`。\n\n"
        "目前我这边还没有针对每一种具体食物/饮料单独建档，\n"
        "所以只能给出一个大的原则：\n"
        "- 尽量让你的饮食和用药模式保持稳定，而不是忽快忽慢、忽多忽少；\n"
        "- 在你打算做任何“大动作”（比如极端减肥、暴饮暴食、开始大量喝某种饮品、上很多保健品）之前，\n"
        "  先把你的药物清单和这些打算告诉医生/药师，让他们帮你一起评估风险。\n\n"
        "⚠️ 我的回答只能作为一般性参考，不适合作为任何用药调整的唯一依据。"
    )


if __name__ == "__main__":
    agent = DrugFoodCoachAgent()
    print("🚀 DrugFoodCoachAgent 启动中...")
    # 这里默认连接到本机 Docker 容器中的 OpenAgents Network
    agent.start(network_host="localhost", network_port=8700)
    agent.wait_for_stop()
