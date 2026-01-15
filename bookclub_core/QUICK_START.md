# ⚡ 快速开始指南

> **3 分钟跑通 BookClub AI Agent Demo**

---

## 📋 前置要求

- ✅ Python 3.9+
- ✅ OpenAgents 已安装（`pip install openagents`）
- ✅ Google API Key（Gemini）
- ✅ 10GB 磁盘空间（PDF + 输出文件）

---

## 🚀 快速启动（3步）

### Step 1：配置环境（1分钟）

```bash
cd bookclub_core

# 创建 .env 文件
cat > .env << 'EOF'
GOOGLE_API_KEY=your_api_key_here
OA_WORKSPACE_SECRET=bookclub-secret-2026
EOF

# 替换为你的真实 API Key
nano .env  # 或者用任何编辑器
```

---

### Step 2：启动系统（1分钟）

```bash
./multi_start.sh
```

**预期输出**：
```
✅ 所有进程已清理完毕，缓存已清除。
🔍 [状态检查] 正在验证...
✅ [Agent] bc-intake  - 角色: INTAKE
✅ [Agent] bc-content - 角色: CONTENT  
✅ [Agent] bc-ops     - 角色: OPS
✅ [PDF]   已上传: files/xxx
✅ [营养]  营养速查表已加载（3737 字符）
✅ [规则]  膳食规则已加载（7486 字符）

🎉 系统启动成功！
```

---

### Step 3：打开 Studio（1分钟）

```bash
# 浏览器访问
open http://localhost:8700/studio

# 或手动访问
http://localhost:8700/studio
```

进入：**Channels** → **#general**

---

## 🎯 测试场景（3选1）

### 场景 1：3天快速测试（推荐）⭐

在 #general 频道发送：

```
@bc-intake

我是注册营养师Eva，想做一个 3 天的读书会
书籍：《你是你吃出来的》
特长：神经营养学
产品：复合B族维生素
目标人群：IT程序员（熬夜、用眼过度、压力大）
```

**预计耗时**：5-8 分钟  
**输出文件**：18 个  
**总字数**：~30,000 字

---

### 场景 2：7天完整测试

```
@bc-intake

我是注册营养师Eva，想做一个 7 天的读书会
（其他信息同场景1）
```

**预计耗时**：10-15 分钟  
**输出文件**：36 个  
**总字数**：~60,000 字

---

### 场景 3：自定义测试

```
@bc-intake

我是 [你的身份]，想做一个 [X] 天的读书会
书籍：《你是你吃出来的》
特长：[你的专业特长]
产品：[你的产品名称]
目标人群：[目标人群描述]
```

---

## 📖 使用流程

### Step 1：Intake Agent（需求收集）

发送上述消息后，Intake Agent 会输出：

```
═══════════════════════════════════
📋 读书会策划需求单
═══════════════════════════════════

【书籍信息】
- 书名：《你是你吃出来的》
- 作者：夏萌
...

✅ 信息收集完成，可传递给 @bc-content
═══════════════════════════════════
```

---

### Step 2：Content Agent（生成逐字稿）

1. **点击 Intake 输出右上角的 💬 引用按钮**
2. 输入框会自动显示引用内容
3. 在引用内容下方输入：

```
@bc-content

请生成完整的讲书逐字稿
```

4. **观察实时进度**：

```
📋 【大纲已生成】
Day 1：xxx
Day 2：xxx
Day 3：xxx

⏳ 正在生成 Day 1/3...
✅ Day 1/3 完成！（约 6800 字）

⏳ 正在生成 Day 2/3...
✅ Day 2/3 完成！（约 7200 字）

⏳ 正在生成 Day 3/3...
✅ Day 3/3 完成！（约 7500 字）
```

---

### Step 3：Ops Agent（生成运营物料）

1. **再次点击 💬 引用按钮**（引用 Content 输出）
2. 输入：

```
@bc-ops

请生成完整的执行物料包
```

3. **预期输出**：
   - Part 3：时间轴与 SOP
   - Part 4：21 条招募文案
   - Part 5：交付期文案
   - Part 6：资源清单
   - Part 7：销讲资源包

---

## 📁 查看输出文件

```bash
cd output

# 查看最新生成的文件
ls -lt | head -20

# 打开 Day 1 逐字稿
open content_*_day1.md

# 打开完整合并版
open content_*.md

# 打开 Word 版本
open content_*.docx
```

---

## 🔍 验证质量

### 检查点 1：字数统计

```bash
# 统计 Day 1 字数
wc -w output/content_*_day1.md

# 应该在 3000-4000 之间
```

### 检查点 2：结构完整性

```bash
# 查看大纲
grep "^#" output/content_*_day1.md

# 应该包含：
# # Day 1: xxx
# ## 2.1 书中精华
# ## 2.2 延展知识
# ## 2.3 解决方案
# ## 🌱 产品种草
```

### 检查点 3：PDF 引用

```bash
# 查找 PDF 页码引用
grep "PDF P" output/content_*_day1.md

# 应该有多处引用，如：
# PDF P22
# PDF P25
# PDF P30
```

### 检查点 4：营养数据

```bash
# 查找营养数据
grep -E "\d+\.?\d*g|\d+\.?\d*mg" output/content_*_day1.md

# 应该有精确数字，如：
# 12.7g 蛋白质
# 186mg 胆固醇
```

---

## 🐛 常见问题

### Q1：启动失败，提示 "openagents command not found"

**解决**：
```bash
# 激活 Conda 环境
conda activate bookclub_env

# 或者重新安装
pip install openagents
```

---

### Q2：Agent 没有响应

**检查**：
```bash
# 查看日志
tail -20 intake.log
tail -20 content.log
tail -20 ops.log

# 查找错误信息
grep -i "error\|fail" *.log
```

**常见原因**：
- API Key 未配置或无效
- Python 缓存问题（运行 `./stop.sh` 清理）
- 网络问题（检查代理设置）

---

### Q3：生成被截断

**解决**：
1. 检查 `content.log` 是否有错误
2. 确认 `max_output_tokens` 设置（应为 8192）
3. 重试一次（有时是 API 限流）

```bash
# 重启系统
./stop.sh
./multi_start.sh
```

---

### Q4：前端看不到输出

**解决**：
```bash
# 检查 Agent 是否真的在运行
tail -5 content.log | grep "running"

# 应该显示：
# 🤖 Agent 'bc-content' is running!

# 如果没有，重启
./stop.sh
./multi_start.sh
```

---

## 📊 性能参考

### 硬件配置（测试环境）

- **CPU**：Apple M1 / Intel i5
- **内存**：8GB
- **网络**：10Mbps+

### 预期耗时

| 操作 | 耗时 | 说明 |
|------|------|------|
| 系统启动 | 30-60s | 包含 PDF 上传 |
| Intake 输出 | 10-20s | 需求收集 |
| Content Day 1 | 60-90s | 单天逐字稿 |
| Content Day 2 | 60-90s | 单天逐字稿 |
| Content Day 3 | 60-90s | 单天逐字稿 |
| Ops 输出 | 90-120s | 完整物料包 |
| **总计（3天）** | **5-8 分钟** | 端到端 |

---

## 🎥 录屏建议

如果你要录制 Demo 视频：

```bash
# 1. 开启录屏（macOS）
Cmd + Shift + 5

# 2. 选择录制区域
只录制浏览器窗口（OpenAgents Studio）

# 3. 同时录制终端（可选）
使用 OBS 或 ScreenFlow 录制多窗口

# 4. 建议录制内容
- 启动过程（加速播放）
- 输入需求（正常速度）
- 实时进度（保留原速，展示"正在生成"）
- 打开文件展示（快速滚动）
```

---

## 🛑 停止系统

```bash
# 停止所有 Agent
./stop.sh

# 如果还有残留进程
pkill -f openagents

# 清理端口
lsof -ti:8700,8600 | xargs kill -9
```

---

## 📚 进阶操作

### 自定义天数

系统自动识别输入中的"X 天"，支持：
- 3 天（推荐，快速测试）
- 5 天（中等规模）
- 7 天（完整周期）
- 21 天（大型项目）

### 复用 PDF 文件

启动后会显示：
```
💡 [提示] 可设置环境变量以复用: export PDF_FILE_REF='files/xxx'
```

复制这行，添加到 `.env` 文件，下次启动就不用重新上传了：
```bash
echo "PDF_FILE_REF='files/b566jt6mj1f8'" >> .env
```

### 监控实时日志

```bash
# 新开一个终端窗口
tail -f content.log

# 或者同时监控三个 Agent
tail -f intake.log & tail -f content.log & tail -f ops.log
```

---

## ✅ 检查清单（Demo 前）

- [ ] `.env` 文件已配置（API Key）
- [ ] 系统已启动（`./multi_start.sh`）
- [ ] 浏览器已打开（`localhost:8700/studio`）
- [ ] 测试文案已准备（复制到剪贴板）
- [ ] 关闭无关应用（保持界面整洁）
- [ ] 网络连接稳定（Gemini API）

---

## 🎯 成功标准

运行完整流程后，你应该得到：

```
output/
├── intake_xxx.md (需求单，~500字)
├── content_xxx_day1.md (~3500字)
├── content_xxx_day2.md (~3500字)
├── content_xxx_day3.md (~3500字)
├── content_xxx.md (完整版，~10000字)
├── ops_xxx.md (物料包，~10000字)
└── ...（对应的 .docx 和 _wechat.txt 文件）

总计：18 个文件，~30,000 字
```

---

**如果遇到任何问题，请查看：**
- 📖 完整文档：`使用指南.md`
- 🐛 问题排查：`启动和关闭.md`
- 💬 联系作者：Eva（注册营养师）

---

*快速开始版本：v1.0 | 更新时间：2026-01-07*
