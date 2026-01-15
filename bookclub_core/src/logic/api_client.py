# src/logic/api_client.py
import os
import google.generativeai as genai # 适配 OpenAgents 要求的旧包
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    def __init__(self):
        # 仿照你新版代码的逻辑，确保 API_KEY 注入
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            # 关键：强制使用 'rest'，这会让旧包像新包一样稳定，避开 gRPC 坑
            genai.configure(api_key=self.api_key, transport='rest')
        
    def generate_response(self, user_input, cache_id=None):
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro-002")
        
        try:
            if cache_id:
                # 挂载夏萌老师 PDF 缓存的核心逻辑
                from google.generativeai import caching
                content_cache = caching.CachedContent.get(cache_id)
                model = genai.GenerativeModel.from_cached_content(cached_content=content_cache)
            else:
                model = genai.GenerativeModel(model_name)

            resp = model.generate_content(user_input)
            return resp.text
        except Exception as e:
            return f"Gemini API Error: {str(e)}"

api_client = APIClient()