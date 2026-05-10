---
name: df-constraint-audit
description: "扫描 DevFlow 产物和代码，检查门禁行为、状态码语义、接口契约等约束描述是否存在多处重复或互相矛盾；用户提到 $df-constraint-audit、约束矛盾、唯一事实源审计时使用。"
metadata:
  short-description: "审计 DevFlow 约束矛盾"
---

# df-constraint-audit

只读审计当前 feature 的约束描述是否偏离唯一事实源。默认在计划/讨论语境下运行；除非用户明确确认修正，否则只输出报告和建议，不改文件。

## 输入

1. 读取 `devflow/active/.current` 指向的 feature。
2. 读取该 feature 的 `checklist.yaml`、`issues.yaml`、`handoff.md`、`uat.md`、`validation.md`，缺失文件记为缺失，不临时创建。
3. 涉及主链、官网子链、`nas-agent`、`erp-executor`、容器职责边界或状态机时，先使用 `framework-truth-guard` 读取系统框架正本。

## 审计范围

提取以下描述性文本，而不是纯文件路径引用：

- 门禁脚本行为、通过条件、失败条件。
- 状态码、错误码、pending/failed/success 等状态语义。
- 接口契约、字段来源、调用方/被调用方职责。
- 同一用户可见失败面的关闭条件或 regression guard。

## 流程

1. 对每条描述定位唯一事实源：代码、门禁脚本、契约文档或 `docs/design` 正本文档。
2. 找不到事实源的标为“孤立描述”。
3. 对照描述与事实源：
   - 一致：标 `PASS`。
   - 不一致：标 `FAIL`，列出冲突点和两个版本。
   - 多处描述同一行为：标 `DUPLICATE`，建议改为引用事实源。
4. 报告按 `FAIL` → `DUPLICATE` → `PASS` 排序。
5. 对每个 `FAIL` 和 `DUPLICATE`，建议保留的唯一事实源和应改成引用的文件路径。

## 输出

- 先给结论：是否存在阻断级约束矛盾。
- 列出每个问题的文件路径、字段/段落、事实源、建议处理方式。
- 未经用户确认，不得修改 `checklist.yaml`、`issues.yaml`、`handoff.md`、`uat.md`、`validation.md` 或代码。
