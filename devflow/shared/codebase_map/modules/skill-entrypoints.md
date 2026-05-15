# Skill 入口模块

## 关键文件

- `df-plan/SKILL.md`
- `df-uat/SKILL.md`
- `df-execute/SKILL.md`
- `df-review-loop/SKILL.md`
- `df-fix/SKILL.md`
- `df-accept/SKILL.md`
- `df-backlog/SKILL.md`
- `df-status/SKILL.md`
- `df-regression/SKILL.md`
- `df-codebase-map/SKILL.md`
- `df-constraint-audit/SKILL.md`

## 边界与风险

- 每个 `SKILL.md` 必须自包含，不能依赖未发布的隐性上下文。
- 改 skill 后同步 `README.md` 与 `README.en.md`。
- 技能规则写短规则，不写长解释；跨 skill 复用逻辑优先独立成 skill，而不是在多个入口重复弱规则。
- 不能把项目级 Dify、FZNAS、浏览器细节写进全局 skills。
- 最终状态回复要求按任务类型动态表达；发布/UAT 类任务保留硬状态，工具链或文档治理任务不要套用发布表头。

## 惯例与测试

- 用 `quick_validate.py <skill-dir>` 校验被修改 skill。
- 用 `git diff --check` 查空白和冲突标记。
- README 只做最小版本式更新，不整份覆盖重写。
