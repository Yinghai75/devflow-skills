---
title: "精简 DevFlow skills 并收敛上下文读取策略"
lane: "high-risk"
status: planned
created_at: "2026-05-16 15:29:46 CST"
map_modules_read:
  - devflow/shared/codebase_map/OVERVIEW.md
  - devflow/shared/codebase_map/modules/skill-entrypoints.md
  - devflow/shared/codebase_map/modules/runtime-helper.md
  - devflow/shared/codebase_map/modules/docs-and-release.md
---

# 计划

## 目标

在保留单个 `SKILL.md` 可独立执行关键规则的前提下，吸收 `opusreviews/df_skills_slim_plan.md` 中合理的三项后续建议：

- `handoff.md` / `issues.yaml` 分段读取，减少跨会话恢复和 UAT/fix 入口的上下文消耗。
- skill 文件精简，但以不削弱硬闸、职责边界和唯一事实源为优先，行数目标是软约束。
- `issues.yaml` closed stub 前置压缩，从 `$df-uat` 扩展到 `$df-fix` 入口，避免 agent 先全量读取长历史。

## 非目标

- 不追求所有 skill 强行压到 80 行；超过目标但保留必要业务判断时允许写明理由。
- 不把 `df-plan` / `df-review-loop` 的专有复杂逻辑整段外移成只剩一行引用。
- 不改变 DevFlow 阶段语义、`execution_authorized` 硬闸、`Capability Coverage Matrix` 唯一事实源或 review-loop scope 规则。
- 不在本计划阶段创建 `shared-protocols/`、改 `SKILL.md` 或运行实现门禁；这些只作为 `$df-execute` checklist。
- 不归档或改写前一个已验证 feature：`20260513-1124-补齐-devflow-runtime-发布依赖与-issue-压缩工具` 仍保持待 `$df-accept` 状态。

## 方案

### Opus 建议取舍

- 接受 #3：新增上下文读取策略。`handoff.md` 长于 100 行时默认只读最新断点和当前 issue/checklist 相关段落；`issues.yaml` 入口先看 active stub/open issue，不先吞长 closed 历史。
- 部分接受 #4：引入共享协议文档用于维护重复规则，但 `SKILL.md` 必须保留关键摘要、硬阻断条件和相对路径引用。不能假设 agent 会自动跟随外部引用。
- 接受 #5：`compact-issues` 前置到 `$df-fix` 和 `$df-uat` 入口。触发条件扩展为 `issues.yaml` 超过 80 行、任一 issue 超过 50 行、或存在 3 个及以上 closed issue。

### 设计约束

- 共享协议路径暂定为仓库根目录 `shared-protocols/`。若执行期发现安装方式不会复制该目录，必须同步 README 安装步骤，或改为不依赖外部协议文件。
- 每个被精简的 `SKILL.md` 仍需保留可独立执行的关键规则：入口硬闸、不得自动执行/修复的条件、stop-loss、scope 外处理、证据落盘和状态更新。
- `df-execute` / `df-fix` 是主要去重目标：子代理分派、checkpoint/codebase-map hygiene、最终回复格式可抽出公共协议并保留摘要。
- `df-plan` / `df-review-loop` 主要做内联精简：删除重复解释、合并冗余句子，不迁移核心判断。
- `df-uat` / `df-fix` 的 issue 压缩规则必须仍指向现有 helper：`uv run python ~/.codex/local/devflow/devflow_cli.py --repo <repo> compact-issues`。

### 预期提交分组

1. `docs(skills): add shared protocol docs and install references`
2. `docs(skills): slim execute and fix instructions`
3. `docs(skills): add scoped context reading and compact precheck`
4. `docs(review-plan): trim plan and review-loop wording`
5. `test(devflow): add skill reference and compact precheck guards`，仅当执行期需要新增测试或 runtime 防线。

## 写入边界与代码地图

- map_modules_read:
  - `devflow/shared/codebase_map/OVERVIEW.md`
  - `devflow/shared/codebase_map/modules/skill-entrypoints.md`
  - `devflow/shared/codebase_map/modules/runtime-helper.md`
  - `devflow/shared/codebase_map/modules/docs-and-release.md`
- 可写路径：
  - `df-plan/SKILL.md`
  - `df-execute/SKILL.md`
  - `df-fix/SKILL.md`
  - `df-uat/SKILL.md`
  - `df-review-loop/SKILL.md`
  - `df-accept/SKILL.md`，仅在 accept 审计需要理解 shared protocol 或 closed stub 时最小修改。
  - `README.md`
  - `README.en.md`
  - `shared-protocols/`，仅在安装可达性方案明确后创建。
  - `runtime/tests/`，仅用于新增引用完整性或 compact precheck 回归测试。
  - `devflow/shared/codebase_map/`，用于同步模块卡片。
- 禁止修改区域：
  - 前一个 active feature 的正式产物，除非只是读取或用户另行授权归档。
  - `runtime/devflow_issues.py` / `runtime/devflow_cli.py` 的压缩行为，除非 RED 证明 helper 不能支持入口前置压缩。
  - `~/.codex/local/devflow/` 本机副本，除非 `$df-execute` 后确实修改 runtime 正本并完成同步验证。
- 受保护接口：
  - `execution_authorized: false` 的计划态硬闸。
  - `Capability Coverage Matrix` 作为唯一覆盖事实源。
  - `review-findings.yaml` 作为 review finding 正本，不能把 review finding 写入 `issues.yaml`。
  - `compact-issues` 的历史可追溯、active stub、下一个 UAT id 唯一性。

## Checklist

- 见 `checklist.yaml`。

## Capability Coverage Matrix

> 单一能力覆盖矩阵。`df-execute` coverage verification、`df-review-loop` coverage review、`df-fix` issue closure、`df-accept` 归档审计都只核验本表，不另建额外验证或关闭矩阵。

| 用户可见能力 | 用户动作链 | 下游成功判据 | 失败信号 | 实现项 | validation | UAT 项 | 不可替代证据 | waiver/残余风险 |
|---|---|---|---|---|---|---|---|---|
| Agent 读取瘦身后的 skill 仍能独立执行关键 DevFlow 规则 | 用户触发 `$df-execute`、`$df-fix`、`$df-plan` 或 `$df-review-loop`，agent 只读对应 `SKILL.md` 和必要引用 | 入口硬闸、scope、stop-loss、checkpoint、review/validation/UAT 边界仍能从 skill 内关键摘要得出 | `SKILL.md` 只剩外部引用；关键阻断条件必须读另一个文件才知道；Plan Mode 自动文案被误当执行授权 | DF-002、DF-003、DF-006 | validation.md:V-001、V-002、V-006 | uat.md:UAT-001 | 精简前后行数记录、关键规则保留清单、引用可达性检查 | 残余风险：agent 可能不主动打开引用文件；以 skill 内保留硬闸摘要缓解 |
| Agent 恢复长 `handoff.md` / 长 `issues.yaml` 时先 scoped read 或压缩 | 用户触发 `$df-execute`、`$df-fix` 或 `$df-uat`，当前 feature 有长 handoff 或多 closed issue | skill 明确要求只读最新断点、相关段落和 active issue；触发阈值时先运行 compact helper | 指令仍要求全量读取长 handoff；closed issue 多时未先 compact；重复新建历史 issue | DF-004、DF-005 | validation.md:V-003、V-004、V-005 | uat.md:UAT-002 | `df-execute`/`df-fix`/`df-uat` 中的入口规则、compact helper 单测或门禁证据 | 无 |
| shared protocol 不破坏公开安装和单 skill 可用性 | 用户按 README 安装或本机 symlink 使用 DevFlow skills | 若 `SKILL.md` 引用 `shared-protocols/`，README 安装步骤覆盖该目录；本机和复制安装形态都能解析相对引用 | README 仍只复制 `df-*`；安装后引用文件不存在；skill 描述依赖未发布本地上下文 | DF-002、DF-008 | validation.md:V-002、V-006 | uat.md:UAT-003 | 引用完整性测试或手工 `test -f` 证据、README/README.en 同步 diff | 若最终决定不建外部协议，记录 waiver 并以内联精简替代 |
| issue 压缩入口前置不改变历史可追溯性 | 用户登记新 UAT issue 或进入 `$df-fix <issue-id>` | closed issue 被压缩为 stub 后仍保留 `history_ref`、最新证据、复测状态和下一个 UAT id 唯一性 | 压缩删除正式记录；open/fixed_pending_retest 被误压；closed 复测未完成却隐藏 | DF-005 | validation.md:V-004、V-005 | uat.md:UAT-002 | `devflow-runtime-unit` gate 或新增 compact fixture 测试 PASS | 无 |
| 文档总览与 codebase map 反映新规则 | 用户看 README、README.en 或 codebase map 判断 skill 组成和安装方式 | skill 数量、安装步骤、shared protocol 说明、runtime helper 边界和模块卡片一致 | README 暗示未安装文件可用；README.en 漏同步；codebase map 仍写旧边界 | DF-008、DF-009 | validation.md:V-006、V-007 | uat.md:UAT-003 | README 中英文 diff、codebase map 更新记录、`git diff --check` PASS | 无 |

## 验证计划

- 见 `validation.md`。

## 执行前确认

- 本计划已将 opus 的 open question 转成执行期硬闸：外部 shared protocol 不可假设自动可读。
- 本 feature 状态应停在 `planned`，`execution_authorized: false`。只有用户后续显式 `$df-execute` 或明确“执行”才允许改 skill 正文。
