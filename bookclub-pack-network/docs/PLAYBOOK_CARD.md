收到，那我把它**“收口成一张可复用的 Playbook 卡片”**（你可以直接贴进 `docs/PLAYBOOK_CARD.md` 或你的 OS 知识库里）。这张卡的目标是：**你以后做任何 multi-agent 产线，都能用同一套骨架稳定交付**。

---

# Playbook Card v1 — Stable Multi-Agent Production Loop

（输入契约 → 调度 → 产出 → 核验 → 失败回路 → 导出）

## 0) 一句话原则

**LLM 负责生成候选；规则/工具负责裁判；Publisher 负责装配与最终签名。**

---

## 1) Input Contract（输入契约：把自然语言变成“可跑接口”）

**Owner：`bc-intake`**

* [ ] 输出只包含三段：`inputs / missing_questions / assumptions`
* [ ] `inputs.cycle_days` ∈ [1..21]
* [ ] `inputs.conversion.enabled` 明确 true/false（避免后续分叉不确定）
* [ ] `book_source_mode` 明确：provided / recommend（哪怕 recommend 暂时降级，也要明确策略）

> 解锁的能力：后面所有 agent 都“吃同一种输入结构”，不会靠猜。

---

## 2) Orchestration（调度：把大任务拆成可控子任务）

**Owner：Network + Publisher**

* [ ] delegate 顺序固定（推荐）

  1. Intake → 2) BookBrief → 3) Content → 4) Ops → 5) Conversion（可选）→ 6) Publisher
* [ ] 每个 worker **只**在 `task.delegate` 时工作，完成后 `task.complete`
* [ ] 每个 worker 只产出自己模块的“局部结构”，不越界写别人的字段

> 解锁的能力：减少“一个模型一口气写完”导致的漂移与失控。

---

## 3) Production (Workers)（分工产出：每个 agent 只对一段结构负责）

### A) `bc-bookbrief`（决策门）

* [ ] 输出 `book_brief.selected_book`（title/author）
* [ ] 输出 `summary`（可短，但必须有）
* [ ] 输出 `fit_check`：why_fit≥2、risks≥1、recommendation 枚举（go/no-go/conditional）

### B) `bc-content`（Participant 内容产线）

* [ ] 产出 `content_pack.daily_plan`：长度 = N（N=cycle_days）
* [ ] 每项必须含：day/theme/key_points/text_post/discussion_prompts/homework/reflection

### C) `bc-ops`（Organizer 运营产线）

* [ ] 产出 `ops_pack`：pre_launch/opening/daily_ops/closing
* [ ] `daily_ops` 长度 = N；每项必须含 day/announcement/homework_reminder/moderation_notes

### D) `bc-conversion`（可选：转化产线）

* [ ] 如果 enabled=false：输出最小占位（不编造产品信息）
* [ ] 如果 enabled=true：`hook_map` 至少覆盖 day=1、day=ceil(N/2)、day=N（最好每天）

> 解锁的能力：每段产物都可独立复用/替换（换模型、换提示词、换策略）。

---

## 4) Validation（核验：把锯齿智能关进“规则围栏”）

**Owner：`bc-publisher`（强制执行）**

### Level-1：Schema Check（硬校验）

* [ ] 最终输出必须符合 `bookclub_pack_v1.schema.json`

### Level-2：Runtime Invariants（硬校验）

* [ ] `content_pack.daily_plan` 长度 == N
* [ ] `ops_pack.daily_ops` 长度 == N
* [ ] day 必须从 1..N **连续且无重复**
* [ ] conversion.enabled=true 时：`hook_map` 覆盖关键日（1 / mid / N）

### Level-3：Quality Scan（软校验，可抽样）

* [ ] 空字段/空段落扫描（例如 text_post 过短/为空）
* [ ] “作者/书籍背景编造”风险扫描（当输入没提供时禁止强编）
* [ ] 风格一致性：tone 是否一致、是否符合 is_online / format

> 解锁的能力：系统“稳定交付”，并且你能准确知道失败原因在哪一层。

---

## 5) Failure Loop（失败回路：失败不是崩溃，而是可控重试）

**Owner：Publisher（策略固定，便于调试）**

* [ ] **失败分类**

  * Schema fail → 结构不合规
  * Runtime fail → 天数/连续性/覆盖率不合规
  * Quality fail → 软质量不足
* [ ] **重试策略**

  * Schema/Runtime fail：只重试“责任 agent”，并锁定 `inputs` 与 `book_brief` 不变
  * Quality fail：优先“补齐”而不是“全量重写”（减少随机性）
* [ ] **重试上限**：每类最多 2 次；否则进入“降级交付”（给最小可用版本 + 提示缺口）

> 解锁的能力：可调试、可回归、可持续迭代。

---

## 6) Export（导出：让交付物对人类友好）

**Owner：Publisher**

* [ ] 输出 `pack_v1.json`（机器可用）
* [ ] 导出 `organizer_pack.md` + `participant_pack.md`（人类可用）
* [ ] 在导出头部写清：cycle_days、selected_book、tone、是否含 conversion

> 解锁的能力：评委/用户 10 秒看懂；你也能快速 Demo。

---

# 最小“核验预算”建议（你问的“每一步都要核验吗？”的落地版）

* **必核验**：Publisher 的 Schema + Runtime（两道硬门）
* **抽核验**：Quality scan（按天抽 3 天：1 / mid / N）
* **不核验**：纯润色类（标题优化、同义改写）

---

如果你下一步想更工程化：我可以把 **Level-2 Runtime Invariants** 写成一份“10 条以内的 Publisher 校验清单”（完全贴合你的 schema 字段名），以及一个“失败→重试哪个 agent”的路由表，让你 network 跑起来像真正的产线。
