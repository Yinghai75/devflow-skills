# UAT 记录

## 人工验收记录

暂无。

## UAT 覆盖矩阵

> 由 `$df-plan` 根据 checklist、validation 和 Golden Set Delta 填写；不得在高风险 feature 中保持为空。

### UAT-001：公开安装说明与 runtime helper 路径一致

- 覆盖能力：用户按 README 安装后能获得或同步 DevFlow runtime helper。
- 环境：本机 local，公开仓库 checkout。
- 操作步骤：
  1. 按 README 的手动安装路径复制 skills 与 runtime helper。
  2. 执行 README 或 skill 中给出的 `df-plan` helper 命令。
- 期望结果：命令路径存在，能打印帮助或创建 feature，不出现缺文件。
- 证据口径：命令输出、路径存在性和 README 对应段落。
- 自动证据：runtime 单测与 `git diff --check`。
- 状态：待人工 UAT

### UAT-002：compact-issues 保留历史且可继续编号

- 覆盖能力：长 `issues.yaml` 可压缩为活跃视图，同时保留历史追溯。
- 环境：本机 local synthetic fixture。
- 操作步骤：
  1. 在临时 feature 中放入超过阈值的 `issues.yaml` 和 evidence 历史。
  2. 运行 `compact-issues`。
  3. 新增一个 UAT issue。
- 期望结果：活跃文件保留 open/复测相关 issue；长历史迁移到 `evidence/`；新 issue id 大于活跃和历史最大 id。
- 证据口径：fixture diff、单测输出和新增 issue id。
- 自动证据：`test_devflow_cli.py` 中 compact 相关测试。
- 状态：待人工 UAT

### UAT-003：run-gate 安全执行仍能记录 evidence

- 覆盖能力：门禁命令不用 shell 也能执行，非法 shell 控制符被拒绝。
- 环境：本机 local synthetic gate registry。
- 操作步骤：
  1. 在临时 feature 注册普通 argv 命令并运行 `run-gate`。
  2. 注册含 shell 控制符的命令并运行 `run-gate`。
- 期望结果：普通命令生成 log 和 manifest；控制符命令被拒绝且不执行副作用。
- 证据口径：`evidence/manifest.json`、log、单测断言。
- 自动证据：`test_devflow_cli.py` 中 run-gate 安全测试。
- 状态：待人工 UAT
