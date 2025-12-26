# Demo Input Case (Supports cycle_days 1..21)

> 用途：
> - Studio 回归测试（每次改 agent 都用同一套输入跑一遍）
> - 录 3 分钟视频（稳定复用）
> - 验证「cycle_days 可自定义」能力

---

## A. 固定演示案例（推荐：先用 3 天游程录视频）
请按以下信息向 Publisher（bc-publisher）发起一次生成请求：

### 1) 基本信息
- 主理人身份：营养师
- 目标人群：小学/初中孩子的家长
- 核心问题：孩子用眼负担大，家长希望通过“饮食与营养”做可执行的日常改善，但不知道如何系统化

### 2) 书籍来源
- 模式：provided
- 备选书（占位示例）：《护眼营养指南》
  - 作者：可空
  - 备注：如果信息不足，请在 book_brief 里标注“待补充”，不要编造

### 3) 读书会形式
- cycle_days：3
- 线上：是
- 交付形态：hybrid（群内短文 + 可直播逐字稿 + PPT 大纲）
- 风格：professional（专业但不说教）

### 4) 运营要求
- 每天早上 8 点发预告
- 每天有作业 + 复盘引导问题
- 需要：开营主持稿 + 破冰方案 + 收官脚本

### 5) 销转（本次演示开启）
- enabled：true
- 产品：叶黄素相关产品（示例占位）
- 面向人群：孩子家长
- 作用点（示例）：视疲劳管理、用眼营养支持（注意合规措辞）
- 约束：避免夸大/医疗化表述；加入“因人而异/建议咨询专业人士”等提醒

---

## B. 扩展验证（可选：把 3 改成 7/14/21）
只改一行即可验证扩展能力：

- cycle_days：7

验收点：
- content_pack.daily_plan 必须恰好 7 项，day=1..7 连续
- ops_pack.daily_ops 必须恰好 7 项，day=1..7 连续
- conversion.enabled=true 时：
  - hook_map 至少覆盖 day=1、day=4、day=7（最好覆盖每一天）

---

## C. 验收清单（每次跑完都对照）
1) book_brief：summary + author_profile + fit_check(recommendation)
2) packs 四包结构都存在：
   - recruit_pack（MVP：文案可用，poster_text 为海报文案+版式要点）
   - content_pack（按天输出）
   - ops_pack（开营+破冰+每日8点预告+作业复盘+收官）
   - conversion_pack（enabled 按输入开关）
3) pack_v1 输出结构完整（meta/inputs/book_brief/packs）
4) Publisher 运行时强校验通过（长度==cycle_days、day 连续）