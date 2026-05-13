# 验证计划

## 基础验证

- `uv run python runtime/tests/test_devflow_cli.py`：仓内 runtime 单测通过；失败即阻断。
- `uv run python /Users/yinghai/.codex/local/devflow/tests/test_devflow_cli.py`：本机 runtime 副本单测通过；失败即阻断。
- `uv run python /Users/yinghai/.codex/skills/.system/skill-creator/scripts/quick_validate.py <modified-skill-dir>`：每个被修改 skill 校验通过；失败即阻断。
- `git diff --check`：无空白错误和冲突标记；失败即阻断。

## 执行证据

- `uv run python runtime/tests/test_devflow_cli.py`：PASS，24 tests。
- `uv run python /Users/yinghai/.codex/local/devflow/tests/test_devflow_cli.py`：PASS，24 tests。
- `uv run --with pyyaml python /Users/yinghai/.codex/skills/.system/skill-creator/scripts/quick_validate.py df-plan`：PASS。
- `uv run --with pyyaml python /Users/yinghai/.codex/skills/.system/skill-creator/scripts/quick_validate.py df-uat`：PASS。
- `git diff --check`：PASS。
- `evidence/manifest.json`：`devflow-runtime-unit` PASS；`git-diff-check` PASS。

## Blast Radius Guard

### Impact Map

- 公开安装：README 宣称的安装方式必须能获得 runtime helper 或明确同步步骤。
- UAT issue：`issues.yaml` 分层不能丢失 issue id、状态、最新证据和历史引用。
- 门禁执行：`run-gate` 不能依赖 shell 解释命令，不能扩大命令注入面。
- Skill 合同：`df-uat` 的硬阻断必须有可执行 helper 对应。

### Protected Surfaces

- `df-plan` 计划/执行授权边界。
- `df-uat` issue 去重、重开、history_ref 和 80 行硬阻断。
- `df-execute` run-gate/evidence manifest 语义。
- README 公开安装路径和 10-skill 总览。
- 已有本机 `~/.codex/local/devflow` 使用者。

### Gate Selection

- `devflow-runtime-unit`：runtime helper 单测。
- `git-diff-check`：基础 diff 收口。
- 本 feature 不涉及 Dify、容器、线上对象；dev-full/online 发布闭环豁免。

### Golden Set Delta

- 新增 compact fixture：包含 open issue、closed issue、长 investigation、history_ref 和 evidence 历史 id。
- 新增 run-gate fixture：包含普通 argv 命令、带引号参数命令、shell 控制符拒绝样本。

### TDD/RED Evidence

- 当前公开仓库没有 `runtime/` 或等价 helper 正本；README 只安装 `df-*`。
- 当前 `df-uat/SKILL.md` 要求超过 80 行先压缩，但 runtime CLI 没有 `compact-issues` 子命令。
- 当前 `/Users/yinghai/.codex/local/devflow/devflow_cli.py` 的 `run_gate` 使用 `subprocess.run(command, shell=True, ...)`。

### Waiver

- 设计文档：本仓库无 `docs/design/` 正本，runtime packaging 不改变外部项目架构合同，豁免。
- 发布闭环：目标环境为 local，不涉及 Dify/容器/线上对象，豁免 dev-full/online 发布。
