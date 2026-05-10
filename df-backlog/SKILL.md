---
name: df-backlog
description: "把临时想到的新 feature、增强项或后置事项登记到 DevFlow roadmap/backlog；不创建 active feature，不生成计划，不登记 UAT issue。用户提到 $df-backlog、df-backlog、插入 roadmap、记录新 feature、backlog 时使用。"
metadata:
  short-description: "记录 DevFlow backlog"
---

# df-backlog

把“现在想到、但不应打断当前 feature”的事项记录到仓库级 backlog。所有沟通与产物使用简体中文，时间按北京时间。

## 边界

- 只维护 `devflow/roadmap.md`，必要时同步当前 active feature 的 `handoff.md`。
- 不创建 `devflow/active/` 目录。
- 不生成 `plan.md`、`checklist.yaml`、`validation.md`。
- 不写入当前 feature 的 `issues.yaml`，除非用户明确说这是当前 UAT 缺陷；那应改用 `$df-uat`。
- 不直接实现新 feature；启动时用 `$df-plan`。

## 流程

1. 读取当前仓库的 `devflow/roadmap.md`。
2. 如存在当前 active feature，读取其 `handoff.md`，判断新事项是否应作为“下一项候选”提示。
3. 从用户描述中提取：
   - 标题。
   - 背景/动机。
   - 建议优先级。
   - 首版范围。
   - 非目标。
   - 待规划问题。
   - 建议启动时机。
4. 将事项写入 `devflow/roadmap.md` 的 `Feature Backlog`，保持现有排序和编号风格；若插入到当前下一项之前，应顺延后续编号。
5. 如该事项与当前 active feature 的验收后动作有关，在 `handoff.md` 增加简短指针。
6. 回复记录位置、建议启动方式和未决问题；不要长篇规划。

## 参数习惯

- `--after-current`：明确放在当前 active feature 验收后。
- `--priority high|medium|low`：登记建议优先级。
- `--promote`：把已有 backlog 项提升为下一项候选，只调整 roadmap 排序和状态说明。

## 写法

- 标题使用用户能识别的业务名，不使用内部临时代号。
- 首版范围写成可规划的最小闭环。
- 待规划问题只列真正会影响实现方案的问题。
- 如果用户描述不足，但能合理记录，先记录并把不确定点放进“待规划问题”；不要为了登记 backlog 反复追问。
