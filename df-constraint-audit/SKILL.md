---
name: df-constraint-audit
description: "扫描当前 feature 的 DevFlow 产物，检查门禁行为描述、状态语义、接口契约是否与代码事实源矛盾或多处重复；用户提到 $df-constraint-audit、约束矛盾、唯一事实源审计时使用。"
metadata:
  short-description: "审计约束矛盾"
---

# df-constraint-audit

只读审计当前 feature 产物中的约束描述是否偏离代码事实源。只输出报告，不改文件。

## 输入

1. 读取 `devflow/active/.current` 指向的 feature。
2. 读取：`checklist.yaml`、`issues.yaml`、`handoff.md`、`uat.md`、`validation.md`、`acceptance.md`、`state.yaml`。缺失文件记为缺失。
3. 涉及主链、官网子链、容器职责边界或状态机时，先读 `docs/design/system_framework_truth.md`。

## 三类检查（按优先级）

### 1. GATE-VS-CODE：门禁行为描述 vs Python 脚本实际行为

扫描 checklist/issues/handoff/validation 中对门禁行为的**自然语言描述**（非文件路径引用），找到对应的 Python 门禁脚本，比较描述与代码是否一致。

常见矛盾模式（源自 doom loop 根因分析）：
- checklist 说"字段 X 存在则 RED"，但脚本实际不检查字段 X
- issues.yaml 说"门禁应检查 Y"，但脚本检查的是 Z
- handoff.md 说"门禁通过条件是 A"，但脚本的通过条件是 B
- 状态码语义（pending/failed/success）在多处有不同定义

**注意**：如果描述使用引用格式（脚本路径 + 行号），标 `PASS-REF`（合规引用）。如果使用自然语言重新描述脚本逻辑，即使描述内容正确也标 `DUPLICATE`（违反 21A 预防规则）。

### 2. STATUS-DRIFT：文档间状态矛盾

检查 feature 内多个文档对当前状态的表述是否一致：
- `acceptance.md` 的 accept 建议 vs `state.yaml` 的 status
- `handoff.md` 最新段落的"下一步"建议 vs `state.yaml` + `checklist.yaml` 的实际进度
- `issues.yaml` 中 issue 的 open/closed 状态 vs `uat.md` 的验证记录

### 3. DUPLICATE-DESC：同一行为的多处描述

同一个门禁行为/接口契约/状态语义在 2+ 个文件中被独立描述（而非引用同一事实源），即使当前内容一致也标记——因为下次改代码时极易漂移。

## 流程

1. 逐文件提取描述性文本（门禁行为、状态语义、接口契约、通过/失败条件）。
2. 对每条描述定位唯一事实源（Python 脚本、契约文档、`docs/design` 正本）。
3. 对照并标记：
   - `FAIL`：描述与事实源矛盾。
   - `DUPLICATE`：多处描述同一行为，或用自然语言复述了脚本逻辑。
   - `STATUS-DRIFT`：文档间状态矛盾。
   - `PASS-REF`：使用引用格式，内容与事实源一致。
   - `PASS`：无矛盾。
4. 报告按 `FAIL` → `STATUS-DRIFT` → `DUPLICATE` → `PASS-REF` → `PASS` 排序。
5. 对每个非 PASS 项，建议唯一事实源和处理方式。

## 输出

- 先给结论：是否存在阻断级约束矛盾（`FAIL` 或 `STATUS-DRIFT`）。
- 列出每个问题的文件路径、行号、事实源、建议处理方式。
- 未经用户确认，不得修改任何文件。
