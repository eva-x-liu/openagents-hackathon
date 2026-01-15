import pandas as pd
import os
from typing import Dict, Any

class FoodNutritionLookup:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.data: Dict[str, Dict[str, Any]] = {}
        self._load_data()

    def _load_data(self):
        """针对实际表头优化的加载逻辑"""
        if not os.path.exists(self.excel_path):
            print(f"⚠️ 错误: 找不到文件 {self.excel_path}")
            return

        try:
            # 1. 读取 Excel
            # 如果你的 Excel 开头有几行是标题或说明，请修改 header=0 为对应的行数
            df = pd.read_excel(self.excel_path, header=0)
            
            # 2. 清洗列名：去除所有空格（解决“名 称”、“蛋 白 质”等由于排版产生的空格）
            df.columns = [str(c).replace(" ", "").strip() for c in df.columns]
            
            # 3. 明确指定第二列（索引为1）作为食物名称键
            # 根据截图，第一列是“序号”，第二列是“名称”
            food_column_name = df.columns[1] 
            
            # 4. 数据清洗：去除食物名称本身可能存在的空格
            df[food_column_name] = df[food_column_name].astype(str).str.replace(" ", "").str.strip()
            
            # 5. 转换为字典格式
            # 使用第二列作为索引，其余列作为属性
            self.data = df.set_index(food_column_name).to_dict(orient='index')
            
            print(f"✅ 成功加载成分表！定位列: [{food_column_name}]，总计 {len(self.data)} 条食物数据。")
            
        except Exception as e:
            print(f"❌ 加载 Excel 失败: {e}")

    def query(self, food_name: str) -> str:
        """Agent 调用接口，增加名称预处理"""
        # 预处理搜索词：去除用户输入可能带有的空格
        clean_query = str(food_name).replace(" ", "").strip()
        
        if clean_query in self.data:
            details = self.data[clean_query]
            # 这里的输出会包含：能量、蛋白质、脂肪、碳水等截图中的所有字段
            return f"【{clean_query}】详细营养成分：{details}"
        
        # 模糊匹配
        matches = [k for k in self.data.keys() if clean_query in k]
        if matches:
            res = self.data[matches[0]]
            return f"未找到精确匹配，最接近的是【{matches[0]}】：{res}"
        
        return f"抱歉，本地成分表中未找到关于‘{food_name}’的数据。"

# 实例化
nutrition_tool = FoodNutritionLookup("data/nutrition.xlsx")