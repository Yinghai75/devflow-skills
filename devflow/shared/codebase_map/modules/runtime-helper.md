# Runtime Helper 模块

## 关键文件

- `/Users/yinghai/.codex/local/devflow/devflow_cli.py`
- `/Users/yinghai/.codex/local/devflow/templates/`
- `/Users/yinghai/.codex/local/devflow/tests/test_devflow_cli.py`
- `df-regression/scripts/regression_feature.py`

## 边界与风险

- 当前公开仓库没有 runtime helper 正本，skills 仍引用本机绝对路径。
- `run_gate` 负责执行项目门禁，不能使用 shell 注入面。
- `issues.yaml` 是活跃视图，压缩必须保留历史可追溯性和下一个 UAT id 的唯一性。
- 迁移历史只能移动到 feature-local `evidence/`，不得删除正式记录。

## 惯例与测试

- Python 运行使用 `uv run python ...`。
- runtime 行为需要先写单测或 fixture 形成 RED。
- 修改 helper 后运行 `/Users/yinghai/.codex/local/devflow/tests/test_devflow_cli.py`。
