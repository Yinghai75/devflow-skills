---
name: df-codebase-map
description: "生成、刷新和检查 DevFlow 原生 codebase map；正本位于 devflow/shared/codebase_map/，只服务实现层导航，不替代 framework-truth-guard。"
metadata:
  short-description: "维护 DevFlow codebase map"
---

# df-codebase-map

维护 DevFlow 原生 codebase map。所有沟通与产物使用简体中文，时间按北京时间。

## 定位

- 正本只在 `devflow/shared/codebase_map/`。
- 只回答实现层问题：代码在哪、现有模式是什么、接口触点在哪里、哪些区域易炸、相关门禁是什么。
- 不读取、不依赖、不迁移 `.planning/codebase/*`。
- 不替代 `framework-truth-guard`；涉及主链、长尾链、官网子链、`nas-agent`、`erp-executor`、容器职责边界、状态机或跨模块编排时，先使用 `framework-truth-guard`。

冲突优先级：

`docs/design/system_framework_truth.md` > `docs/design/module_maps/*.md` > DevFlow codebase map > 局部代码观察

如果发现 map 与系统框架真相或模块地图冲突，只能记录冲突、要求补文档或阻断；不得用 map 覆盖系统边界。

## 结构

- `devflow/shared/codebase_map/manifest.yaml`
- `devflow/shared/codebase_map/units/*.md`

`manifest.yaml` 必须包含：

- `owner: devflow`
- `generated_at_bj`
- `source_commit`
- `scope_index`
- `units`
- `stale_if_changed`
- `not_source_of_truth_for_framework: true`

每个 unit 不超过 200 行，且包含：

- `## Scope`
- `## Structure`
- `## Patterns`
- `## Interfaces`
- `## Risks`
- `## Recommended Gates`

## 场景

### 检查场景

由 `df-init`、`df-plan`、`df-accept` 触发。

1. 读取 `manifest.yaml`，不要全文读取 `units/`。
2. 根据调用方给出的 `paths`、`surfaces`、`target_env` 推导 scope。
3. 判断 scope 是否有命中 unit，判断 `source_commit` 与当前 `git rev-parse HEAD` 是否一致。
4. 判断目标路径是否命中 `stale_if_changed` 或 unit 覆盖范围。
5. 返回：命中 units、缺失 scope、过期原因、是否允许 waiver。

### 按 scope 生成或刷新

调用方必须提供 `paths`、`surfaces`、`target_env`。只刷新命中的 units，不生成大而全全文 map。

生成时必须读取：

- `AGENTS.md`
- `devflow/shared/gate_registry.yaml`
- 目标 scope 下的代码、测试、配置、接口文件
- 命中系统边界时，先读取 `docs/design/system_framework_truth.md` 和相关 `docs/design/module_maps/*.md`

生成后更新：

- `manifest.yaml.generated_at_bj`
- `manifest.yaml.source_commit`
- `manifest.yaml.scope_index`
- `manifest.yaml.units`
- `manifest.yaml.stale_if_changed`
- 对应 `units/*.md`

### 全量刷新

仅用户明确要求“刷新全部 codebase map”或 map 严重缺失时使用。仍按 scope 拆 unit，禁止写一个大而全地图。

## Consumption

固定消费顺序：

`manifest.yaml → scope 命中的 units → local files`

禁止把整个 `devflow/shared/codebase_map/` 当上下文包全文读取。

## Stale 规则

- 修改路径命中某 unit 覆盖范围，该 unit 过期。
- 修改 `AGENTS.md`、`docs/design/system_framework_truth.md`、`docs/design/module_maps/*.md`，相关风险/接口 unit 过期。
- 修改 `devflow/shared/gate_registry.yaml`，含推荐门禁的相关 units 过期。
- 修改跨模块接口、Dify workflow、容器配置、插件/Broker/执行器链路，相关接口 unit 过期。

## 写入要求

- unit 的 `Recommended Gates` 只能推荐候选；最终门禁必须来自 `devflow/shared/gate_registry.yaml`。
- `manifest.yaml.scope_index` 必须能支持按 paths、surfaces、target_env 找到 unit。
- `units[].line_count` 要反映实际行数；超过 200 行必须拆分。
- 每次刷新要在调用方文档记录 `map_units_read` 或刷新/豁免结果。
