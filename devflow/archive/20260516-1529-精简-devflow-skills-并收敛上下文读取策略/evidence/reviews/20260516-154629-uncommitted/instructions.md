# review instructions

- 当前 feature：`20260516-1529-精简-devflow-skills-并收敛上下文读取策略`
- 目标：提交前审查当前 uncommitted diff。
- scope：`df-plan/SKILL.md`、`df-execute/SKILL.md`、`df-fix/SKILL.md`、`df-uat/SKILL.md`、`df-review-loop/SKILL.md`、`shared-protocols/`、`README.md`、`README.en.md`、`devflow/shared/codebase_map/`、当前 feature DevFlow 产物。
- 重点检查：关键硬闸是否被削弱；shared protocol 引用是否导致安装断裂；compact-issues 前置条件是否保护 open/retest issue；README 中英文是否同步；codebase map 是否反映新边界。
- P0/P1/P2 处理：当前 scope 内 P0/P1 阻断；scope 外 P0/P1 只有能证明与本 feature 无文件、接口、状态、门禁或 UAT 动作链交叉时才记录 follow-up；无法证明独立时标记 `uncertain_scope`。P2 只在确定 bug 或测试缺口且在 scope 内时阻断。
- 不要把行数目标、风格偏好或后续重构建议当作阻断项；只报告可证明的 bug、回归风险、安全问题、安装断裂或缺失测试。
