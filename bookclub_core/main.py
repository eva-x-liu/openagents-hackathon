"""
⚠️ LEGACY CODE - 单体架构（已废弃）

此文件是旧版单 Agent 实现，已被 multi-agent 架构取代。
新架构见：src/agents/base_agent.py + agents/*.yaml

保留此文件仅供参考和快速测试。
不要在生产环境使用（依赖的 cache_manager 在赠金账户上无法工作）。
"""

import json
import os
from google.genai import types
from src.logic.cache_manager import cache_mgr  # ⚠️ 赠金账户不可用
from src.tools.excel_handler import nutrition_tool
from src.logic.api_client import api_client

# 颜色配置 (保持你喜欢的审美)
YOU_COLOR = "\u001b[94m"
ASSISTANT_COLOR = "\u001b[93m"
RESET_COLOR = "\u001b[0m"

def extract_tool_calls(text: str):
    """从文本中解析出 tool: query_food({"food_name": "xxx"})"""
    if "tool: query_food" in text:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            json_str = text[start:end]
            args = json.loads(json_str)
            return args.get("food_name")
        except:
            return None
    return None

def run_orchestrator():
    print(f"{ASSISTANT_COLOR}[系统初始化] 正在准备夏萌老师的知识库...{RESET_COLOR}")
    
    # 1. 激活缓存 (守住 $4.00 预算的核心)
    # 确保 data/ 目录下有你的 PDF 文件
    try:
        CACHE_ID = cache_mgr.create_or_get_cache(
            file_path="data/you_are_what_you_eat.pdf", 
            cache_name="shuxia-book-cache"
        )
    except Exception as e:
        print(f"❌ 缓存加载失败，将使用全额 Token 模式: {e}")
        CACHE_ID = None

    history = []
    print(f"{ASSISTANT_COLOR}[系统就绪] 夏萌老师已上线。您可以开始咨询需求了。{RESET_COLOR}")

    while True:
        try:
            user_input = input(f"\n{YOU_COLOR}You:{RESET_COLOR} ")
            if user_input.lower() in ['exit', 'quit']: break
        except EOFError: break

        # 内部 ReAct 循环
        current_input = user_input
        while True:
            # 2. 调用 API (带上缓存 ID)
            response_text = api_client.generate_response(
                user_input=current_input, 
                history=history, 
                cache_id=CACHE_ID
            )

            # 3. 检查是否需要调用工具 (Excel 查表)
            food_to_query = extract_tool_calls(response_text)
            
            if food_to_query:
                print(f"🔍 [工具调用] 正在本地查表: {food_to_query}")
                # 0 Token 消耗的本地查询
                tool_result = nutrition_tool.query(food_to_query)
                
                # 将工具结果作为新的“输入”喂给 AI，并记录到历史
                history.append(types.Content(role="user", parts=[types.Part(text=f"用户输入: {current_input}")]))
                history.append(types.Content(role="model", parts=[types.Part(text=response_text)]))
                
                # 更新 current_input 为工具执行结果，触发下一轮推理
                current_input = f"本地工具返回数据：{tool_result}。请基于此数据继续回答。"
                continue 
            else:
                # 4. 最终回答输出
                print(f"\n{ASSISTANT_COLOR}夏萌老师:{RESET_COLOR}\n{response_text}")
                
                # --- 核心插入位置：自动化报表触发 ---
                if "inputs:" in response_text:
                    try:
                        # 简单的 JSON 提取逻辑：寻找 inputs: 之后的内容
                        json_raw = response_text.split("inputs:")[1].strip()
                        
                        # 兼容处理：防止 AI 把 JSON 包裹在 ```json 代码块中
                        if "```" in json_raw:
                            json_raw = json_raw.split("```")[1]
                            if json_raw.startswith("json"):
                                json_raw = json_raw[4:]
                            json_raw = json_raw.strip()

                        extracted_json = json.loads(json_raw)
                        
                        # 调用我们之前写的脚本
                        from scripts.output_formatter import BookClubReport
                        reporter = BookClubReport(extracted_json)
                        reporter.save_report()
                        print(f"✅ [系统提示] 需求已补齐，夏萌老师已为您生成策划案：output/plan_v1.md")
                        
                    except Exception as e:
                        print(f"⚠️ [系统提示] 尝试生成策划案时出错，可能是 JSON 格式不规范: {e}")
                # --- 结束插入 ---

                # 存入对话历史
                history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))
                history.append(types.Content(role="model", parts=[types.Part(text=response_text)]))
                break

if __name__ == "__main__":
    run_orchestrator()