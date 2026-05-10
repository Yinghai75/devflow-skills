---
name: df-codebase-map
description: "维护仓库 codebase map（OVERVIEW + 模块卡片）；由 df-plan/df-execute/df-fix/df-accept 自动调用，通常不需要手动执行。"
metadata:
  short-description: "维护 codebase map"
---

# df-codebase-map

维护 `devflow/shared/codebase_map/` 下的仓库全景索引和模块卡片。正本只在该目录。

## 结构

```
devflow/shared/codebase_map/
├── OVERVIEW.md          ← 永远加载（≤30行）：目录 atlas + 依赖图 + 卡片索引
└── modules/
    ├── material-server.md
    ├── erp-executor.md
    ├── edge-plugin.md
    ├── dify-workflows.md
    ├── deploy.md
    ├── scripts-gates.md
    └── brand-rules.md
```

- `OVERVIEW.md`：仓库全景，df-* skills 每次都读。内容：目录 atlas（每个顶层目录一行）、模块依赖图（文本箭头）、模块卡片索引（卡片名 + 覆盖路径前缀）。
- `modules/*.md`：每张卡片 ≤30 行，固定 3 节：关键文件、边界与风险、惯例与测试。
- golden set 不放入 map，只存指针。
- codebase map 不是系统真相源；与 `docs/design/system_framework_truth.md` 冲突时以后者为准。

## 触发方与操作类型

| 调用方 | 操作 | 说明 |
|--------|------|------|
| `df-plan` | **只读** OVERVIEW + 命中模块卡片；**补建**缺失卡片 | plan 不碰代码，不刷新 |
| `df-execute` | checklist 项完成后 **增量刷新** 修改命中的卡片 | 写代码的环节负责刷新 |
| `df-fix` | git checkpoint 后 **增量刷新** 修改命中的卡片 | 写代码最多的环节 |
| `df-accept` | **最终 stale gate**，检查命中卡片是否已刷新 | 兜底检查 |
| 用户手动 | **全量重建** 或 **指定卡片刷新** | 极少使用 |

## 只读消费（df-plan / df-fix 分流）

1. 读 `OVERVIEW.md`。
2. 从当前任务的 `paths`/`surfaces` 推导命中哪些模块卡片（按 OVERVIEW 的卡片索引匹配路径前缀）。
3. 只读命中的卡片，不读其他。
4. 如果某路径前缀无对应卡片 → 补建新卡片（按 5 节模板扫描该路径）。
5. 在调用方文档记录 `map_modules_read: [material-server, edge-plugin]`。

## 增量刷新（df-execute / df-fix）

每次 git checkpoint 后：

1. 从 `git diff --name-only HEAD~1 HEAD`（或 stash diff）获取本轮修改文件。
2. 按 OVERVIEW 的卡片索引匹配修改路径 → 确定命中哪些卡片。
3. 对命中的卡片：重新扫描该模块目录，更新卡片的 5 节内容。
4. 如果修改涉及新增顶层目录或新增模块 → 同时更新 OVERVIEW 的目录 atlas 和卡片索引。
5. 未命中任何卡片的修改 → 不做（下次 plan 补建）。

## 最终 stale gate（df-accept）

1. 汇总整个 feature 的所有修改路径。
2. 检查命中的卡片是否已被 execute/fix 刷新过（对比卡片最后修改时间与 feature 最后 checkpoint 时间）。
3. 已刷新 → 通过。未刷新 → 刷新或写 waiver。
4. 检查 OVERVIEW 是否需要更新（新增了目录/模块）。

## 全量重建（用户手动或首次使用）

`$df-codebase-map --full` 或首次 `$df-plan` 发现无 OVERVIEW 时：

1. 扫描仓库顶层目录和主要代码目录。
2. 生成 `OVERVIEW.md`。
3. 为每个主要模块生成卡片。
4. 提交。

## 行数硬限

| 文件 | 上限 | 超限处理 |
|------|------|---------|
| `OVERVIEW.md` | **30 行** | 每个模块只允许表格一行（路径前缀 + 用途 + 卡片）；依赖图不超过 6 行 |
| 每张模块卡片 | **30 行** | 关键文件最多 7 个；边界与风险最多 7 条；惯例与测试最多 4 条 |

生成或刷新后如果超限，必须先砍到限额内再提交。砍的优先级：泛泛之谈 > 显而易见的风险 > 非核心文件 > 次要惯例。

## 卡片模板（3 节，不允许增加节）

```markdown
# <模块名>

## 关键文件
- `<文件>`（大小）— 一句话说明
（最多 6 项，只列核心入口和高风险文件）

## 边界与风险
- 谁调用谁、受保护接口、改了会炸的地方
（最多 6 条，合并边界和风险，不分开写）

## 惯例与测试
- 命名约定、模式、测试路径、门禁
（最多 3 条，只写这个模块独有的，不写通用知识）
```

## 精炼规则

- 卡片只写**代码事实**（文件做什么、谁调用谁、改了跑什么测试），不写**设计决策**（状态归属、职责边界、禁止模式）。设计决策属于 `system_framework_truth.md`，卡片只写指针。
- 不写 LLM 本来就知道的（如"巨文件改动容易冲突"、"日志使用 logging"）。
- 不复述 `system_framework_truth.md`、`gate_registry.yaml` 或 golden set 的内容，只引用路径。
- 不全文读取所有卡片（除非全量重建）。
- 每条 bullet 必须包含具体文件名、接口名或命令；纯描述性文字不算有效 bullet。
