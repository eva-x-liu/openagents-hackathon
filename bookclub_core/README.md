# 📚 BookClub AI Agent

> **OpenAgents Hackathon 2025**  
> 多智能体读书会全案生成系统 - 从需求收集到执行物料，10 分钟完成 2 万字策划

[![OpenAgents](https://img.shields.io/badge/OpenAgents-Multi--Agent-blue)](https://github.com/OpenAgentsInc)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-green)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🎯 项目介绍

**BookClub AI Agent** 是一个基于 OpenAgents 框架的多智能体系统，专为**知识付费创业者**设计，用于快速生成读书会全案策划。

### 核心价值

| 传统方式 | AI 方式 | 提升 |
|---------|---------|------|
| 7 天人工策划 | 10 分钟 AI 生成 | **100x** |
| 2 万字逐字稿 | 自动分天生成 | **质量稳定** |
| 21 条文案手写 | 一键输出 | **即时可用** |

---

## 🎬 Demo 演示

📺 **[观看 3 分钟演示视频](https://youtu.be/2UJ3wY9j3q4?si=HVKJx8SspFkXbH4N)**

> 视频内容：完整流程演示，从需求输入到 2 万字输出

---

## ✨ 核心功能

### 1. 三个 AI Agent 协作

```
用户需求
   ↓
[Intake Agent] 需求收集官
   ↓ 结构化需求单
[Content Agent] 学术内容官  
   ↓ 2万字讲书逐字稿（分天生成）
[Ops Agent] 整合输出官
   ↓ 完整执行物料包（21条文案+SOP）
最终交付
```

### 2. 分天生成策略

- ✅ **避免截断**：每天 3500 字，独立生成
- ✅ **支持扩展**：3/5/7/21 天任意长度
- ✅ **实时进度**：用户看到"Day 1/3 完成"
- ✅ **质量稳定**：每天专注，输出详细

### 3. 三层知识库架构

| 知识库 | 用途 | 调用优先级 |
|--------|------|----------|
| 营养速查表 | 食物营养数据 | 涉及具体克数（g/ml）时优先 |
| 书籍 PDF | 医学逻辑原理 | 涉及"为什么"时优先 |
| 膳食指南 | 定量推荐标准 | **必须核对**（约束规则） |

### 4. 多格式输出

每个输出自动生成 3 种格式：
- 📄 **Markdown**（`.md`）- 开发者查看
- 📘 **Word**（`.docx`）- 微信公众号编辑器
- 📱 **纯文本**（`_wechat.txt`）- 朋友圈复制

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/eva-x-liu/openagent.git
cd bookclub_core
```

### 2. 配置环境变量

```bash
cat > .env << 'EOF'
GOOGLE_API_KEY=your_api_key_here
OA_WORKSPACE_SECRET=bookclub-secret-2025
EOF
```

### 3. 知识库配置（重要⚠️）

本项目需要以下数据文件（**因版权原因未包含在仓库中**）：

| 文件 | 说明 | 获取方式 |
|------|------|----------|
| `data/you_are_what_you_eat.pdf` | 《你是你吃出来的》 | 购买电子版书籍 |
| `data/nutrition.xlsx` | 中国食物成分表 | 官方数据下载 |
| `data/nutrition_reference.md` | 营养速查表 | 基于食物成分表整理（自行生成） |

**配置步骤**：
1. 购买/获取上述版权文件
2. 将文件放入 `data/` 目录
3. （可选）运行脚本生成营养速查表

**仓库中已包含**：
- `data/dietary_rules.md` - 基于公开的《中国居民膳食指南2022》整理

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 启动系统

```bash
./multi_start.sh
```

### 6. 开始使用

浏览器访问：http://localhost:8700/studio

详细步骤见：[📖 快速开始指南](QUICK_START.md)

---

## 📊 Demo 成果

### 真实输出示例（3天读书会）

| Agent | 输出 | 字数 | 耗时 |
|-------|------|------|------|
| **Intake** | 结构化需求单 | ~500 字 | 10-20s |
| **Content** | 3天讲书逐字稿 | **~20,000 字** | 3-6 分钟 |
| **Ops** | 执行物料包 | **~10,000 字** | 2-3 分钟 |
| **总计** | - | **30,000+ 字** | **5-8 分钟** |

### 输出质量亮点

✅ **逐字稿格式**（可直接朗读）
> "各位程序员朋友们，大家好！欢迎大家参加我们这次的线上读书会..."

✅ **引用书中原文**（标注页码）
> "在 **PDF P22** 页，作者提到：'长期睡眠不足会导致免疫系统功能下降...'"

✅ **精确营养数据**
> "根据食物成分表，100g 鸡蛋含蛋白质 **12.7g**，脂肪 9.0g..."

✅ **符合膳食指南**
> "根据《中国居民膳食指南 2022》，每天鸡蛋摄入量不超过 **1 个**，不弃蛋黄..."

---

## 🏆 技术亮点

### 1. OpenAgents 高级特性运用

- ✅ **多 Agent 协作**：3 个 Agent 通过频道消息传递协作
- ✅ **Mod 驱动**：使用 workspace.default Mod 实现消息路由
- ✅ **自定义事件处理**：实现 `on_channel_mention` 处理 @ 消息
- ✅ **知识库集成**：PDF 文件上传 + 结构化数据注入

### 2. 创新设计

- ✅ **三层知识库架构**：明确数据调用优先级，避免混淆
- ✅ **分天生成策略**：避免长文截断，支持任意天数
- ✅ **渐进式销售策略**：Day1种草 → 中间见证 → 最后销讲

### 3. 产品化设计

- ✅ **多格式输出**：Markdown + Word + 微信纯文本
- ✅ **实时进度反馈**：用户看到"Day 1/3 完成"
- ✅ **成本控制**：Gemini 免费层 4 美元跑 10+ 次

---

## 📁 项目结构

```
bookclub_core/
├── agents/                      # Agent 配置
│   ├── intake.yaml             # 需求收集官
│   ├── content.yaml            # 学术内容官
│   └── ops.yaml                # 整合输出官
│
├── src/agents/                  # 核心代码
│   └── base_agent.py           # Agent 基类（核心逻辑）
│
├── data/                        # 知识库（需自行配置）
│   └── dietary_rules.md        # 膳食指南（已包含）
│
├── network.yaml                 # Network 配置
├── multi_start.sh               # 启动脚本
├── stop.sh                      # 停止脚本
├── requirements.txt             # Python 依赖
│
└── 📚 文档
    ├── README.md                # 本文档
    ├── QUICK_START.md           # 快速开始
    ├── HACKATHON_DEMO.md        # Demo 文档
    └── DEMO_SCRIPT_5MIN.md      # 演讲稿
```

---

## 🛠️ 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Agent 框架 | OpenAgents | 多智能体协作 |
| LLM | Gemini 2.0 Flash | 内容生成引擎 |
| 语言 | Python 3.9+ | 核心开发语言 |
| 文档生成 | python-docx | Word 输出 |

---

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [QUICK_START.md](QUICK_START.md) | 3分钟跑通 Demo |
| [HACKATHON_DEMO.md](HACKATHON_DEMO.md) | 完整 Demo 文档 |
| [DEMO_SCRIPT_5MIN.md](DEMO_SCRIPT_5MIN.md) | 演讲稿 |
| [使用指南.md](使用指南.md) | 完整用户手册 |

---

## 🔮 未来规划

- [ ] 支持更多书籍（用户上传 PDF）
- [ ] 支持更多领域（不限于营养学）
- [ ] Web UI（替代 Studio）
- [ ] SaaS 产品化

---

## 👥 团队

- **Eva** - 项目负责人（注册营养师）

---

## 🙏 致谢

- [OpenAgents](https://github.com/OpenAgentsInc) - 多智能体框架
- [Google Gemini](https://ai.google.dev/) - LLM 支持
- 《你是你吃出来的》作者夏萌 - 知识内容来源

---

## 📄 License

MIT License

---

**项目状态**：✅ Hackathon 演示就绪  
**最后更新**：2026-01-07  
**版本**：v1.0
