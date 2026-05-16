# Runtime Helper 模块

## 关键文件

- `runtime/devflow_cli.py`
- `runtime/devflow_issues.py`
- `runtime/templates/`
- `runtime/tests/test_devflow_cli.py`
- `~/.codex/local/devflow/`：runtime 同步后的本机执行副本。
- `df-regression/scripts/regression_feature.py`

## 边界与风险

- 公开仓库 `runtime/` 是 helper 正本；skills 运行依赖同步后的本机副本。
- `run_gate` 负责执行项目门禁，不能使用 shell 注入面。
- `issues.yaml` 是活跃视图；压缩必须保留历史可追溯性、legacy `REVIEW-*` 历史和下一个 UAT id 唯一性。
- 迁移历史只能移动到 feature-local `evidence/`，不得删除正式记录。
- skill 入口只允许在不会压缩 open / fixed_pending_retest / needs_retest issue 的场景前置 compact；超长 active issue 应 scoped read 后继续当前 UAT / fix。

## 惯例与测试

- Python 运行使用 `uv run python ...`。
- runtime 行为需要先写单测或 fixture 形成 RED。
- 修改 helper 后运行 `uv run python runtime/tests/test_devflow_cli.py`，同步后再运行 `uv run python ~/.codex/local/devflow/tests/test_devflow_cli.py`。
