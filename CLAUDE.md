# Claude 使用说明

本仓库是 DevFlow skills 发布仓库。主要入口是：

- `df-init`：启动一个可恢复的 DevFlow feature
- `df-plan`：生成计划、清单和验证方案
- `df-execute`：按 checklist 执行实现
- `df-uat`：记录人工 UAT 结果
- `df-fix`：修复 UAT issue 并闭环验证
- `df-accept`：最终验收与归档
- `df-status`：保存或恢复当前断点

维护时优先保持工作流闭环清晰：`df-init -> df-plan -> df-execute -> df-uat -> df-fix -> df-accept`，`df-status` 作为横向断点能力。

