"""
⚠️ 注意：此模块依赖 Gemini Cache API，需要付费账户。
赠金账户无法使用此功能。

新架构已改用直接上传文件的方式（见 src/agents/base_agent.py）。
此文件仅供参考，不应在生产环境使用。
"""

import os
import datetime
import google.generativeai as genai
from google.generativeai import caching # 统一使用这个库进行缓存管理
from dotenv import load_dotenv

load_dotenv()

# 配置全局 API KEY
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class CacheManager:
    def create_or_get_cache(self, file_path, cache_name):
        """
        核心逻辑：检查是否存在同名缓存，若无则上传并创建。
        支撑 Pack 2 的内容产出。
        """
        # 1. 逻辑检查：列出所有现有缓存并查找匹配项
        for c in caching.CachedContent.list():
            if c.display_name == cache_name:
                print(f"🔍 找到现有缓存: {c.name}")
                return c.name

        # 2. 缩进修正：以下代码必须缩进在方法内部
        print(f"📦 正在上传并创建新缓存: {file_path}...")
        
        # 使用 google-generativeai 标准语法
        uploaded_file = genai.upload_file(path=file_path)
        
        # 创建缓存
        cache = caching.CachedContent.create(
            model="models/gemini-1.5-pro-002",
            display_name=cache_name,
            contents=[uploaded_file],
            ttl="3600s" # 必须是字符串格式以满足 Pydantic 校验
        )
        
        print(f"✅ Cache 成功创建: {cache.name}")
        return cache.name

# 导出实例供 Agent 调用
cache_mgr = CacheManager()