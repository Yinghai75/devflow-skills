# 验证计划

## 基础验证

- V-001：skill 关键规则保留检查。
  - 检查对象：`df-plan/SKILL.md`、`df-execute/SKILL.md`、`df-fix/SKILL.md`、`df-uat/SKILL.md`、`df-review-loop/SKILL.md`。
  - PASS：入口硬闸、执行授权、scope_decision、stop-loss、compact-issues 阈值、checkpoint、Capability Coverage Matrix 和 review 5 轮硬上限仍能从对应 `SKILL.md` 的正文或关键摘要读到。
  - FAIL：核心硬闸只剩外部链接、必须读 shared protocol 才知道是否能执行或关闭 issue。
- V-002：shared protocol 引用完整性检查。
  - PASS：所有 `SKILL.md` 中出现的 `shared-protocols/*.md` 相对引用在源仓存在；若 README 安装方式复制到 `~/.codex/skills`，安装步骤也覆盖 `shared-protocols/`。
  - FAIL：`SKILL.md` 引用不存在文件，或 README 仍只复制 `df-*` 导致复制安装后引用断裂。
- V-003：上下文读取策略检查。
  - PASS：`df-execute` / `df-fix` / `df-uat` 写明长 `handoff.md`、open issue、closed stub、`history_ref` 的读取顺序；不再无条件要求首次全量读取超过 100 行的 handoff。
  - FAIL：入口流程仍要求先全量读取长 handoff 或长 closed issue 历史。
- V-004：compact-issues 前置条件检查。
  - PASS：`df-fix` 和 `df-uat` 在读取或登记 issue 前写明触发条件：`issues.yaml` 超过 80 行、任一 issue 超过 50 行、或 3 个及以上 closed issue；命令指向 `uv run python ~/.codex/local/devflow/devflow_cli.py --repo <repo> compact-issues`。
  - FAIL：只在关闭且复测通过后才 compact，或前置规则会压缩 open / fixed_pending_retest / needs_retest issue。
- V-005：runtime compact helper 回归。
  - 注册门禁引用：`devflow/shared/gate_registry.yaml:3-8` 的 `devflow-runtime-unit`。
  - PASS：执行 `uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo /Users/yinghai/SynologyDrive/codex/devflow run-gate devflow-runtime-unit` 成功；若本 feature 修改 source runtime 或新增 fixture，还需运行 source 侧对应 unittest。
  - FAIL：gate 失败，或 compact 后历史不可追溯、id 不唯一、active issue 被误压。
- V-006：文档与安装说明同步。
  - PASS：`README.md` 与 `README.en.md` 的 skill 数量、安装步骤、runtime/helper 说明和 shared protocol 说明一致。
  - FAIL：中英文 README 对 skill 数量、复制目录或本机 helper 要求描述不一致。
- V-007：基础提交检查。
  - 注册门禁引用：`devflow/shared/gate_registry.yaml:9-14` 的 `git-diff-check`。
  - PASS：执行 `uv run python /Users/yinghai/.codex/local/devflow/devflow_cli.py --repo /Users/yinghai/SynologyDrive/codex/devflow run-gate git-diff-check` 成功，或直接 `git diff --check` 成功并写明未走 run-gate 的理由。
  - FAIL：存在空白错误、冲突标记或不可提交 diff。

## Capability Coverage Matrix 核验

- 矩阵来源：`plan.md#capability-coverage-matrix`。
- 用户动作链：触发 `$df-plan`、`$df-execute`、`$df-fix`、`$df-uat`、`$df-review-loop`、README 安装和 issue 压缩入口。
- 下游成功判据：精简后的 skill 仍可独立判断能否执行、能否修复、能否继续 UAT、能否关闭 issue；长上下文读取和 compact 入口明确。
- 失败信号：skill 只剩外部引用、安装后引用断裂、closed issue 未压缩、open/retest issue 被压缩、README/codebase map 漂移。
- 不可替代证据：关键规则保留清单、引用完整性结果、compact helper gate、README 中英文同步 diff、codebase map 更新记录。
- 本文件只记录每个矩阵行对应的 validation 项；不得另建额外验证或关闭矩阵。

## Blast Radius Guard

### Impact Map

- `df-execute` / `df-fix`：子代理、checkpoint、review-loop、状态更新和最终回复规则。
- `df-uat` / `df-fix`：`issues.yaml` 入口压缩和历史追溯。
- `df-plan`：计划态硬闸、Capability Coverage Matrix 生成规则。
- `df-review-loop`：coverage review mode、scope_decision、5 轮硬上限。
- README / README.en：公开安装和 skill 总览。
- codebase map：skill-entrypoints、runtime-helper、docs-and-release 模块卡片。

### Protected Surfaces

- 单 skill 自包含关键规则，不依赖未发布的本地上下文。
- `execution_authorized: false` 和 `$df-execute` 明确授权边界。
- `review-findings.yaml` 与 `issues.yaml` 分工。
- `compact-issues` 历史文件、`history_ref` 和 UAT id 唯一性。
- README 安装路径与真实发布内容一致。

### Gate Selection

- `devflow-runtime-unit`：`devflow/shared/gate_registry.yaml:3-8`。
- `git-diff-check`：`devflow/shared/gate_registry.yaml:9-14`。
- 目标环境为 `local`，不涉及 Dify/容器/线上对象，发布闭环不适用。
- 本 feature 是 skill 文档治理与 runtime helper 入口规则调整，不需要 `dev-full-e2e`。若执行期改动 runtime helper 行为，则必须补 source unittest 并同步本机 runtime 后再跑注册门禁。

### Golden Set Delta

- 本 feature 不新增业务 golden sample。
- 若新增 compact fixture，归入 `runtime/tests/`，不放入 `devflow/shared/golden_sets/`。

### TDD/RED Evidence

- RED-001：当前 README 手动安装步骤只复制 `df-*` 与 `runtime/`；如果 `SKILL.md` 新增 `../shared-protocols/` 依赖而不改 README，复制安装会缺文件。
- RED-002：当前 `df-fix` compact 前置只在关闭且复测通过后描述，入口处没有 3+ closed issue 前置压缩规则。
- RED-003：当前 `df-execute` / `df-fix` 重复维护子代理分派与 checkpoint 规则，行数和重复度高。

### Waiver

- 不强制所有 skill 低于 80 行。若执行后仍超过 95 行，必须在 `handoff.md` 写明保留原因；超过 130 行且无理由视为未完成本 feature。
