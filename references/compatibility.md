# 框架适配矩阵 — Vision Skill

本文件记录各 Agent 框架对本 skill 的实际适配状态。`verified` = 已在真实环境跑通端到端;`untested` = 架构兼容但尚未真实验证;`incompatible` = 已知不兼容(若有)。

## Agent 框架适配

| 框架        | Skill 目录                   | SKILL.md 自动加载 | 脚本手动可用 | 状态         | 测试人   | 测试日期 |
| ----------- | ---------------------------- | ----------------- | ------------ | ------------ | -------- | -------- |
| Claude Code | `~/.claude/skills/`          | ✅                | ✅           | ✅ verified  | (填写)   |          |
| Codex / Kun | `~/.codex/skills/`           | ✅                | ✅           | ✅ verified  | (填写)   |          |
| Cursor      | `~/.agents/skills/`          | ⚠️                | ✅           | ⚠️ untested  | 待社区   |          |
| OpenCode    | `~/.config/opencode/skills/` | ⚠️                | ✅           | ⚠️ untested  | 待社区   |          |

注:`SKILL.md 自动加载` 表示框架原生支持 Agent Skills 标准会自动语义匹配加载;`脚本手动可用` 表示即使框架不自动加载,调用方仍可手动执行 `python scripts/vision.py ...` 完成功能。

## 上游文本 LLM 组合适配

视觉模型默认 `agnes-2.5-flash`(Agnes AI,免费);备用 `Qwen/Qwen3.5-4B`(硅基流动,免费)、`GLM-4.6V-Flash`(智谱,免费)。以下为文本 LLM × 默认视觉模型的组合:

| 文本 LLM       | 视觉模型         | 上下文    | 端到端 | 状态         |
| -------------- | ---------------- | --------- | ------ | ------------ |
| GLM-5.2        | agnes-2.5-flash  | 128K      | ✅     | ✅ verified  |
| DeepSeek-V3    | agnes-2.5-flash  | 128K      | ✅     | ✅ verified  |
| Qwen2.5-72B    | agnes-2.5-flash  | 128K      | ?      | ⚠️ untested  |
| GPT-4o (text)  | agnes-2.5-flash  | 128K      | ?      | ⚠️ untested  |
| Claude 3.5     | agnes-2.5-flash  | 200K      | ?      | ⚠️ untested  |
| 8K 部署任意模型 | agnes-2.5-flash  | 8K        | ⚠️     | ⚠️ 易截断    |

## 如何补 verified

1. 在真实环境跑一遍 `python scripts/vision.py understand --image <你的测试图>`
2. 确认 stdout 输出合法 JSON 且 `success: true`
3. 跑一遍 `python scripts/vision.py query --image <同图> --question "<问题>"`
4. 把上表对应行改成 ✅ verified,并填测试人/日期,提 PR

我们不预设全绿——没测过的就是 untested。这就是这份矩阵的意义。
