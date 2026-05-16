# review instructions

- 当前 feature：`20260516-1529-精简-devflow-skills-并收敛上下文读取策略`
- 目标：复审当前 uncommitted diff，重点确认上一轮 review 的 P1/P2 是否已修复。
- 上一轮 finding：
  - P1：published `skills add` 不安装根目录 `shared-protocols/`，skill 不能依赖 `../shared-protocols/*.md`。
  - P2：`df-fix` 不得在目标 open/retest issue 超过 50 行时先运行会压缩 active issue 的 `compact-issues`。
- 当前修复意图：skill 正文不再引用 `shared-protocols`；README 不再要求复制该目录；compact 前置只用于 closed/deferred 历史，open/retest 超长 issue 只 scoped read 后继续。
- scope：`df-* /SKILL.md`、README 中英文、codebase map、当前 feature DevFlow 产物。
- 仅报告可证明的 P0/P1/P2 bug、安装断裂、compact 误压、硬闸削弱或测试缺口。
