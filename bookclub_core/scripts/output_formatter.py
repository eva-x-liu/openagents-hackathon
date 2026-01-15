import json
from datetime import datetime

class BookClubReport:
    def __init__(self, inputs: dict):
        self.inputs = inputs
        self.timestamp = datetime.now().strftime("%Y-%m-%d")

    def format_as_markdown(self) -> str:
        """将 JSON 数据转化为夏萌老师风格的 Markdown 策划案"""
        
        # 提取核心参数，设置默认值以防万一
        cycle = self.inputs.get("cycle_days", 3)
        tone = self.inputs.get("tone", "温情专业")
        format_type = self.inputs.get("format", "线上/线下混合")
        
        # 构建 Markdown 内容
        md = f"""# 📚 《你是你吃出来的》读书会·深度研习策划案

> **主理人风格：** 夏萌老师 (临床营养师)
> **策划日期：** {self.timestamp}
> **项目周期：** {cycle} 天深度营
> **交付形式：** {format_type}

---

## 🩺 一、 策划初衷 (夏萌老师寄语)
“健康的身体是吃出来的，也是修出来的。在这 {cycle} 天里，我将带你重新认识食物，重塑你与身体的关系。”

## 📋 二、 核心参数对齐 (PackV1.inputs)
| 维度 | 设定内容 | 备注 |
| :--- | :--- | :--- |
| **读书模式** | {format_type} | 结合理论学习与实操 |
| **内容基调** | {tone} | 兼具临床权威与人文关怀 |
| **销转策略** | {"已开启" if self.inputs.get("conversion", {}).get("enabled") else "纯公益/不开启"} | 侧重价值交付 |

## 📅 三、 课程大纲 (初步构思)
"""
        # 动态生成天数逻辑 (简单的逻辑推导)
        for i in range(1, cycle + 1):
            md += f"### 第 {i} 天：{'理论基础' if i==1 else '深度实践' if i<cycle else '总结与蜕变'}\n"
            md += "- **阅读重点：** [待 Agent 根据缓存 PDF 自动填充]\n"
            md += "- **餐桌建议：** [待调用本地食物成分表生成]\n\n"

        md += """
---

## 🛠️ 四、 后续行动清单
1. [ ] **内容生成**：调用内容设计师 Agent 完成每日讲书稿。
2. [ ] **素材准备**：根据本地 Excel 导出每日推荐食谱清单。
3. [ ] **社群预热**：基于转换策略 Agent 生成首发文案。

---
*本策划案由 BookClub_Core 系统自动生成，版权所有：夏萌读书会项目组*
"""
        return md

    def save_report(self, filename: str = "output/plan_v1.md"):
        content = self.format_as_markdown()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✨ 策划案已导出至: {filename}")

# 测试代码
if __name__ == "__main__":
    test_inputs = {
        "cycle_days": 7,
        "format": "hybrid",
        "tone": "professional",
        "conversion": {"enabled": False}
    }
    reporter = BookClubReport(test_inputs)
    reporter.save_report()