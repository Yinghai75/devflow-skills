---
title: "补齐 DevFlow runtime 发布依赖与 issue 压缩工具"
lane: "high-risk"
status: planned
created_at: "2026-05-13 11:24:23 CST"
map_modules_read: ["skill-entrypoints", "runtime-helper", "docs-and-release"]
---

# 计划

## 目标

让公开 devflow-skills 仓库的 runtime helper、模板和 skill 调用路径形成可发布、可测试的单一事实源；补齐 df-uat issue 压缩 helper，并移除 run-gate shell=True 执行风险。

## 非目标

- 不抽取共享分派矩阵或最终回复模板。
- 不调整子代理模型、角色或 `subagent_handoff.md` 策略。
- 不改变已发布 skill 的核心流程语义。
- 不把 `opusreviews/` 输入目录作为发布内容提交。

## 方案

1. 先保留当前 legacy roadmap 小修 diff，不回退；把结构性建议拆成本 feature 执行。
2. 建立 runtime 发布正本：把当前本机 `/Users/yinghai/.codex/local/devflow/` 的 CLI、templates、tests 作为待纳入公开仓库的 runtime 源；执行期确认最终落点，优先选择仓内 `runtime/`，安装说明同步到 `~/.codex/local/devflow/` 目标路径。
3. 为 `df-uat` 的硬阻断补 `compact-issues`：从活跃 `issues.yaml` 抽离长历史到 feature-local `evidence/`，活跃 issue 保留当前失败面、状态、最新证据和 `history_ref`；压缩后必须保证 YAML 可解析、历史 id 可追溯、下一个 UAT id 不冲突。
4. 硬化 `run-gate`：门禁命令仍由 `gate_registry.yaml` 注册，但 runtime 用 `shlex.split` 得到 argv 后以 `shell=False` 执行；拒绝 shell 控制符、重定向和占位命令。
5. 同步 skill 与 README：`df-uat` 写明 helper 命令，`df-execute`/`df-plan` 只保留必要 runtime 规则，README 中英文说明 runtime helper 安装/同步口径。
6. 用单测、skill 校验和 `git diff --check` 收口；本地安装副本同步作为执行期单独 checklist 项，不在计划阶段改运行代码。

## 写入边界与代码地图

- map_modules_read: ["skill-entrypoints", "runtime-helper", "docs-and-release"]
- 新代码放置规则：runtime helper 源码优先放仓内 `runtime/`；skill 只写调用合同，不内嵌长脚本。
- 禁止修改区域：不改 `asset/` 图片；不提交 `opusreviews/`；不删除正式 DevFlow 产物。
- 受保护接口：`df-plan`/`df-execute` 授权边界、`df-uat` issue id 语义、`run-gate` evidence manifest 格式、README 10-skill 总览。

## Checklist

- 见 `checklist.yaml`。

## Capability Coverage Matrix

> 单一能力覆盖矩阵。`df-execute` coverage verification、`df-review-loop` coverage review 和 `df-accept` 归档审计都只核验本表，不另建额外验证矩阵。本 feature 为 DevFlow skills/runtime 治理任务，用户已确认不做人工 UAT；UAT 列保留覆盖项并以 waiver 记录。

| 用户可见能力 | 用户动作链 | 下游成功判据 | 失败信号 | 实现项 | validation | UAT 项 | 不可替代证据 | waiver/残余风险 |
|---|---|---|---|---|---|---|---|---|
| 公开安装说明与 runtime helper 路径一致 | 维护者按 README 安装或同步 skills 与 runtime helper，再调用 skill 中的 helper 命令 | `~/.codex/local/devflow/devflow_cli.py` 路径可用；README 中英文与 skill 调用路径一致 | README 指向不存在的 helper；skill 调用本机私有路径但公开安装未覆盖 | checklist.yaml:DF-002, DF-005, DF-006 | validation.md:执行证据；`df-plan`/`df-uat` quick_validate PASS；runtime 单测 PASS | uat.md:UAT-001 | evidence/manifest.json；runtime 单测；README/README.en 与 skill diff | 用户确认 DevFlow skills/runtime 治理任务不做人工 UAT；以机器门禁和文档一致性审计替代 |
| compact-issues 保留历史且可继续编号 | 维护者在 feature 中压缩长 `issues.yaml`，后续继续登记 UAT issue | 活跃 issues 保留当前失败面；长历史进入 evidence；新 issue id 不与活跃或历史冲突 | 历史丢失、id 重复、legacy stub 被重复归档、active issue 被误跳过 | checklist.yaml:DF-004 | validation.md:compact fixture 与 40 tests PASS | uat.md:UAT-002 | runtime/tests/test_devflow_cli.py compact 相关回归；evidence/manifest.json | 用户确认 DevFlow skills/runtime 治理任务不做人工 UAT；synthetic fixture 覆盖该工具合同 |
| run-gate 安全执行仍能记录 evidence | 维护者运行 gate registry 中的门禁命令；含 shell 控制符的命令被拒绝 | 普通 argv 命令生成 log/manifest；危险 shell 控制符不执行副作用 | `shell=True` 注入面复现；manifest 缺失；危险命令被执行 | checklist.yaml:DF-003, DF-006 | validation.md:run-gate fixture 与 `devflow-runtime-unit`/`git-diff-check` PASS | uat.md:UAT-003 | runtime/tests/test_devflow_cli.py run-gate 安全测试；evidence/manifest.json | 用户确认 DevFlow skills/runtime 治理任务不做人工 UAT；安全合同由 RED 样本和单测闭环 |

## 验证计划

- 见 `validation.md`。

## 预期提交分组

- `docs(devflow): plan runtime helper packaging feature`
- `feat(runtime): package devflow cli and compact issues helper`
- `docs(skills): document runtime helper install and usage`
