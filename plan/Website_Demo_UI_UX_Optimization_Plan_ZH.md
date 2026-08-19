---
title: "DCFA Local Website Demo UI/UX 分阶段优化计划"
language: "zh-CN"
version: "1.0"
status: "Proposed"
last_updated: "2026-08-19"
affected_surface: "TabCF Analyst local presentation only"
affected_evidence_tracks: "None; no new Track T, H, or A evidence"
---

# DCFA Local Website Demo UI/UX 分阶段优化计划

## 0. 目标与成功标准

本计划把当前 local website demo 从“研究工程审计界面”优化为“普通访客可以快速理解、同时仍可审计的产品演示”。核心不是隐藏研究限制，而是将用户表达、方法说明和机器审计信息分层。

整体成功标准：

1. 普通访客在 10 秒内理解产品解决的问题、可用输入和主要限制；
2. 默认结果区不出现未经映射的内部枚举、`snake_case`、warning code、trace/bundle/specification ID、SDK/API 字段或后端错误上下文；
3. 页面显示的数字、文字、表格和图仍全部来自同一个 validated result bundle，不重新计算或手工复制 headline value；
4. 完整未舍入数值、证据 ID、警告代码、状态事件和运行身份继续保存在可独立验证的 artifact 中；
5. outside-support、弱 IV、外部服务失败和证据验证失败仍 fail closed，不得为了展示效果降级、静默重试或回退到 sklearn；
6. 桌面与 390 px 手机视口均无横向溢出，主要操作和主要结果可被键盘及屏幕阅读器理解；
7. P0、P1、P2 分别通过自己的验收门后才进入下一阶段，不用后续视觉工作掩盖前一阶段的信息泄露或错误语义。

## 1. 范围和不可破坏边界

### 1.1 本计划涉及

- `src/dcfa_website_demo/` 的访客展示、状态、错误、上传和交互文案；
- `src/dcfa/reporting.py` 之上的 website-specific 展示图或等价展示投影；
- website demo 的浏览器、集成和展示投影测试；
- local demo 的单实例运行识别与版本可见性；
- 后续个人网站嵌入前的展示准备度。

### 1.2 本计划不涉及

- 不修改 TabCF 数值核心、estimand、诊断阈值、support gate 或 evidence ledger；
- 不扩大 v1 的 Y/X/Z、连续处理、标量 IV、无 `W` 范围；
- 不引入 Hillstrom、通用因果方法路由或自动 IV 发现；
- 不改变 Gemini 一次结构化编译、无数据行/实际干预值传输的边界；
- 不改变 managed TabPFN 的外部传输确认、版本 profile、无 fallback 和 `development_only` 身份；
- 不把本计划或 UI smoke 描述成 Track T 统计证据、Track A agent 优势证据或公开发布授权；
- 不因为 UI 需要而覆盖、删除或弱化既有 artifact。

### 1.3 展示层原则

- **一个事实源，两个投影。** 访客投影与机器审计投影来自同一 validated result bundle；前者翻译语义和控制精度，后者保留完整机器身份。
- **折叠不是安全边界。** 不应发给普通浏览器的内部字段，不能只靠 closed accordion 隐藏。
- **用户文案不是枚举格式化。** 不使用简单的下划线替换推导产品文案；建立显式、穷举、可测试的 presentation mapping。
- **展示舍入不改变证据。** UI 可显示适当位数，artifact 必须保留未舍入值并继续通过独立验证。
- **警告保留含义，不暴露实现。** 访客看到清晰风险说明；机器 code 留在 artifact 或明确授权的开发者视图。

## 2. 目标信息架构

默认页面按以下顺序组织：

1. 一句话价值主张和首屏主操作；
2. Guided example / Local CSV 两种输入；
3. 人类可读的四阶段进度；
4. 直接回答问题的主结果；
5. 数据支持、经验诊断和适用范围；
6. 展示版图表和等价文字摘要；
7. 方法和隐私说明；
8. 仅在明确开发模式下提供的机器审计入口。

推荐的访客结果顺序为：

> Plain-language answer → support badge → important warnings → chart → methodology/details

不再默认使用：

> raw value → claim code → evidence ID → support enum → warning code → raw trace JSON

## 3. P0：信息边界与可信展示

### 3.1 阶段目标

先消除默认访客页面中的内部输出泄露和新旧运行实例混淆。在 P0 完成前，不投入大规模视觉重构。

### 3.2 工作项

#### P0.1 建立显式 presentation model

- 为允许的 claim type、support status、warning 和 blocked error 建立显式映射；
- 映射结果至少包含：短标题、用户解释、严重级别、建议行动和是否允许显示数值；
- 未知 enum/code 必须 fail closed 为通用安全文案，并在 artifact 中保留原值；
- 主结果使用自然语言句子，不直接展示 `quantile_contrast_x_minus_comparison_x` 等内部类型；
- `supported`、`weak_support` 等改为用户能理解的支持状态；
- `Y_units` 改为 “outcome units” 或经输入明确提供的合法单位标签；
- UI 显示精度由展示规则控制，完整值继续只由 evidence record 绑定。

#### P0.2 分离访客详情与机器审计

- 默认页面不渲染完整 `Agent trace` JSON；
- 不把 prompt/config/request hash、token usage、latency、SDK/API 版本、trace/specification/bundle/event ID 或 error context 发送给普通访客 DOM；
- artifact、独立验证命令和内部调试能力保持不变；
- 如保留开发者视图，必须由明确的本地开发配置开启，并与默认访客输出分离；
- 默认访客页最多显示一个短的“Result verified”状态和必要的方法说明。

#### P0.3 清理用户可见错误

- 不直接显示 `DCFAError.to_dict()`；
- 不直接展示 `OUTSIDE_SUPPORT`、`LLM_API_FAILED`、backend stage、exception type、文件路径或版本差异；
- 建立有限的用户错误类别：输入需修正、超出数据支持、服务暂不可用、结果验证失败；
- blocked 路径必须继续不显示数值、不显示图、不生成伪 evidence；
- 完整 typed error 继续写入允许的审计边界。

#### P0.4 生成 website-specific 展示图

- 展示图必须从 validated result bundle 派生，不从已有 PNG 读取数值；
- 删除图内的 `local_development | tabpfn | development_only`、bundle ID 和 evidence ID；
- `q=0.5` 映射为 “Median”，`Intervention x` 映射为 “Treatment level”；
- 图外保留简短而清楚的 development-only 限制；
- 原始审计图如仍有验证用途，应继续作为独立 artifact，不被覆盖；
- 为图提供等价的文字摘要，不能要求访客从曲线读 headline number。

#### P0.5 消除新旧服务实例混淆

- 明确一个权威 local demo 入口和端口来源；
- 启动时检测或清楚报告端口冲突，避免旧进程继续代表当前源码；
- 页面或可见运行信息提供短版本/commit 标识，但不暴露完整内部健康负载；
- browser QA 必须核对页面版本与当前 `HEAD`，不能只确认端口返回 200。

### 3.3 P0 验收门

- strong、weak、outside-support、input error、Gemini failure、managed backend failure 的默认访客输出均不包含原始内部 enum/code/ID/trace；
- 页面源码和 DOM 中不存在默认渲染的完整 audit JSON；
- 展示图不包含下划线式运行身份、bundle/evidence ID 或开发枚举；
- weak 路径仍显示等价的弱 IV/弱支持含义；outside-support 仍无数字、图和 evidence；
- 相同 result bundle 的访客值与 evidence ledger 值一致，差别只允许是已测试的显示舍入；
- 只存在一个被验收的 local demo 实例，页面版本与 `HEAD` 对应；
- 相关单元/集成测试、artifact verification、Ruff、format 和 `git diff --check` 通过。

## 4. P1：结果优先与核心交互

### 4.1 阶段目标

让访客先理解结论和限制，再按需查看方法；同时缩短从进入页面到成功运行第一个示例的路径。

### 4.2 工作项

#### P1.1 重构主结果层级

- 主结果第一行直接回答用户问题，例如“从低处理水平到高处理水平，估计中位结果增加 4.85 个结果单位”；
- 主结果下只保留三个高价值元素：support 状态、重要警告、development-only 限制；
- 删除 answer card 与 evidence card 的重复字段；
- Evidence ID 不作为视觉主元素；如需要复制，放入开发者详情；
- 无法给出数值时，用原因和下一步替代空白 evidence card。

#### P1.2 简化 hero 和首屏路径

- 把 hero 改为“问题—能力—行动”的短结构；
- 减少首屏 badges，只保留最关键的范围说明；
- 390 px 手机首屏必须看到主 CTA 或清楚的输入起点；
- 将长 development/privacy 声明拆为一行摘要和可展开说明，但外部数据传输不得被弱化；
- “What this demo will not claim”改为面向用户的“Scope and limitations”。

#### P1.3 将内部状态机投影为用户进度

- 将多个内部 state event 映射为四个用户阶段：理解问题、检查数据、运行分析、验证结果；
- 进度状态不得伪造已经完成的步骤；
- blocked 状态显示发生在哪个用户阶段及可采取的下一步；
- 外部请求期间显示当前阶段，并防止重复提交；
- 不在进度面板显示 reason enum、tool call 数或模型内部状态。

#### P1.4 改善 Gemini 与数据传输说明

- Guided question 输入旁明确说明文本将发送给 Google Gemini，并提醒不要输入私人或敏感信息；
- CSV 路径继续要求明确确认，分别说明“问题发送给 Gemini”和“所选 Y/X/Z 行发送给 Prior Labs”；
- 把超长 checkbox 文案拆为简短确认和紧邻的传输摘要；
- 不改变当前一次请求、`store=false`、无行数据发送给 Gemini、无 silent fallback 的实现边界。

#### P1.5 提供可靠的空态、等待态和失败态

- 初始页面不重复显示两个“等待填充”的空卡；
- 执行中给出阶段反馈，不显示假进度百分比；
- 网络或凭证问题对访客显示“服务暂不可用”，对本地 operator 保留可诊断信息；
- 成功后把焦点或 live announcement 移到主结果；
- 重复点击不得创建多个意外外部请求。

### 4.3 P1 验收门

- 桌面和 390 px 手机上，访客能在首屏看到产品作用及主操作；
- strong 示例的第一视觉焦点是自然语言结果，不是内部字段或 evidence card；
- weak/outside-support 的语义、警告和无数字规则保持完整；
- Gemini/CSV 传输边界在动作发生前清晰可见；
- 执行中、成功、输入错误、服务错误和安全阻止均有互斥、稳定的 UI 状态；
- 不增加任何新的外部请求、重试或统计路径。

## 5. P2：响应式、无障碍与展示完善

### 5.1 阶段目标

完成键盘、屏幕阅读器、移动图表和上传流程的细节，使 demo 适合截图、录屏、mentor walkthrough 和后续受控嵌入。

### 5.2 工作项

#### P2.1 修正语义与键盘体验

- 标题层级按 `h1 → h2 → h3` 组织；
- 检查 Gradio tabs 是否产生重复或近乎不可见但可聚焦的按钮；
- 所有输入具有稳定的 programmatic label、说明和错误关联；
- 状态更新使用适当的 live region，blocked/success 不只依靠颜色；
- 运行结束后的焦点位置可预测；
- 完整键盘流程覆盖 guided、CSV、accordion、运行和错误恢复。

#### P2.2 优化移动图表和结果阅读

- 双栏图在窄屏改为上下排列，或优先展示回答当前问题的单一主图；
- 图例、坐标和注释在 390 px 下仍可读；
- 提供图表文字摘要和必要的数据表替代；
- 保持颜色对比，并避免只用颜色区分不同曲线或状态。

#### P2.3 改善 CSV 预检

- 提供标准示例 CSV 下载入口；
- 文件选择后在本地显示表头、行数和三列角色摘要，再进入确认；
- 角色输入尽量使用已读取表头的受控选择，减少拼写错误；
- 继续严格拒绝额外列、非连续 Y/X、非有限值和 120–256 行范围外文件；
- 预检不得把文件内容发送给 Gemini 或 Prior Labs。

#### P2.4 视觉与内容一致性

- 收紧移动端容器边距，避免 390 px 视口只剩约 294 px 主内容宽度；
- 统一按钮、badge、warning、support 和 blocked 状态的视觉语法；
- 把 `Track T`、`W drop`、`general router`、`Hillstrom` 等项目内部词汇移到方法说明；
- 默认文案面向普通访客，研究术语提供解释而不是直接暴露；
- 截图和录屏路径不依赖展开开发者详情。

#### P2.5 评估前端承载边界

- 优先对现有 Gradio 做小而可验证的改进；
- 只有当 Gradio 无法解决 DOM 泄露、键盘重复焦点或响应式图表问题时，才提出薄展示前端；
- 若需要分离前端，仍使用当前 typed backend/evidence contracts，不复制统计逻辑；
- 不在本阶段引入重型通用前端框架、设计系统或与需求无关的服务层。

### 5.3 P2 验收门

- 1280 px 与 390 px 浏览器 QA 无横向溢出、内容重复、不可见焦点或小到不可读的图表文字；
- 标题层级、表单 label、live status、键盘顺序和图表替代文本通过人工检查；
- CSV 预检在任何外部传输前完成，现有严格数据边界不变；
- guided strong/weak/outside-support 和 CSV happy/error paths 均通过浏览器回归；
- 页面适合直接截图或录屏，不需要展示开发者 trace 才能解释可信性；
- public hosting、authentication、rate limiting、retention/privacy policy 和成本归属仍作为独立发布门，不因 P2 完成而自动开放。

## 6. 建议实施顺序与依赖

| 顺序 | 交付物 | 依赖 | 是否允许外部 live call |
|---|---|---|---|
| 1 | P0 presentation mapping、错误映射和 DOM 审计边界 | 当前 typed response/schema | 否；优先使用 fake clients |
| 2 | P0 website-specific plot 和单实例/version 检查 | validated result bundle | 否 |
| 3 | P0 完整回归与 artifact parity | 1–2 | 否 |
| 4 | P1 result-first 页面和用户进度 | P0 通过 | 否 |
| 5 | P1 privacy/consent、等待和失败状态 | P0 通过 | 否 |
| 6 | P1 桌面/移动浏览器验收 | 4–5 | 否；live call 需另行明确授权 |
| 7 | P2 accessibility、移动图表和 CSV 预检 | P1 通过 | 否 |
| 8 | P2 受控展示验收与发布缺口清单 | 7 | 如确有必要，单独授权一次 bounded smoke |

每一阶段都应使用新的测试或临时运行目录；不得覆盖既有结果来制造“干净”验收。

## 7. 验证策略

### 7.1 自动检查

- 在 `tests/integration/test_website_demo.py` 或更小的专用测试模块中验证 presentation mapping、redaction、舍入一致性和各状态输出；
- 用 contract-faithful fake Gemini/TabPFN clients 覆盖 strong、weak、outside-support、输入失败和外部服务失败；
- 扫描默认 HTML/DOM/plot text，断言禁止出现的 raw code/ID 字段；
- 继续运行 artifact verification，证明展示层没有改变证据和数值核心；
- 运行现有全套 pytest、Ruff、format、dependency 和 diff 检查。

### 7.2 人工浏览器检查

- 1280 × 720：价值主张、主操作、结果层级和图表；
- 390 × 844：首屏 CTA、容器宽度、tabs、长警告、结果和图表；
- 键盘：Tab 顺序、tabs、accordion、submit、结果焦点和错误恢复；
- 屏幕阅读器语义：标题、label、status、warning 和图表摘要；
- 运行身份：页面版本与当前 `HEAD` 一致，不从旧端口/旧进程验收。

### 7.3 阶段证据

每个阶段的 handoff 至少记录：

- 改动文件；
- 运行命令和测试结果；
- 浏览器视口及检查路径；
- strong/weak/outside-support 的展示截图或结构化 QA 记录；
- artifact verification 结果；
- 未验证的外部服务、容器和公开部署边界；
- commit、push destination 和最终 Git 状态。

## 8. 实施前需明确但不阻塞 P0 的决策

1. Developer details 是仅本地配置可见，还是完全移出页面并只保留 artifact/CLI？
2. 访客是否需要复制短 evidence handle，还是只显示 “Verified result”？
3. 页面默认语言保持英文，还是在后续增加中英文切换？
4. 展示图保留 CDF + summary 双图，还是按问题类型只显示一张主图？
5. P2 后若 Gradio 仍存在不可修复的 DOM/键盘问题，是否批准薄前端分离？

这些决策不得改变数值、证据、数据传输或研究协议；如果某一选择会触及这些边界，必须先追加 architecture/protocol decision，而不是在 UI 实现中静默决定。

## 9. 完成定义

本计划只有在 P0、P1、P2 各自验收门全部通过，并且以下条件同时成立时才算完成：

- 默认访客界面不暴露内部机器输出；
- 自然语言结果、警告、图表和证据来自同一 validated bundle；
- 所有 hard gate、warning、development-only 和数据传输边界保持完整；
- 桌面、移动、键盘和屏幕阅读器路径可用；
- 当前代码、文档、测试和实际运行页面一致；
- 未把工程 smoke、managed service traceability 或 UI polish 误报为科学结果或公开发布准备完成。
