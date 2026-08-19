---
title: "DCFA Hugging Face Space 正式展示版发布计划"
language: "zh-CN"
version: "1.0"
status: "Approved; implementation deferred until UI P0/P1 acceptance"
approved_on: "2026-08-19"
implementation_dependency: "Website demo UI/UX P0 and P1 accepted"
affected_surface: "Public portfolio demo and user-owned duplicated Space"
affected_evidence_tracks: "None; no new Track T, H, or A evidence"
---

# DCFA Hugging Face Space 正式展示版发布计划

## 0. 已批准的发布决策

DCFA 的第一版正式 website tool 采用一个公开 Hugging Face Space，并明确分成两种模式：

```text
Public DCFA Space
├── Explore prepared demo
│   └── frozen prompt + prepared synthetic CSV + verified stored result
│       zero API calls, zero credentials, zero inference cost
│
└── Analyze your own data
    └── Duplicate this Space
        ├── user configures a Gemini secret
        ├── user configures a Prior Labs TabPFN secret
        └── the duplicated Space runs the existing bounded live workflow
```

公共原始 Space 不收集访客的 Gemini key 或 TabPFN token，也不使用项目所有者的服务
凭证替访客运行任意输入。希望分析自有 CSV 和 prompt 的用户，应复制 Space，并在自己控制的
Space Settings 中配置两个 secrets。Hugging Face 不应把原 Space 的 secrets 自动复制给用户。

本决策区分两种“正式”状态：

- website tool 可以是经过部署验收的正式 portfolio release；
- prepared 或 duplicated-Space 的数值结果仍保持其真实的
  `local_development / tabpfn / development_only` 证据身份；
- website 发布不得把展示可用性改写成 locked Track T、Track A agent 优势或真实世界因果证据。

## 1. 实施时点和前置条件

本计划不与当前 UI 优化并行实施。只有以下条件满足后才开始：

1. `plan/Website_Demo_UI_UX_Optimization_Plan_ZH.md` 的 P0 验收通过；
2. 同一计划的 P1 验收通过；
3. 默认访客 DOM 已不包含内部 enum、warning code、trace、bundle/specification/evidence ID、
   SDK 字段或后端错误上下文；
4. visitor-safe 文案、图表和原始 evidence bundle 的数值一致性已经测试；
5. 当前 P0/P1 改动已经完成验证、commit 和 push，工作区不存在与 Space 实施范围重叠的
   未提交改动。

P2 不阻止开始 Space 集成，但正式公开 URL 前仍必须通过与发布直接相关的移动端、键盘、
标题层级、状态提示和图表替代文本检查。

开始实现前，应在 `docs/DECISIONS.md` 追加一条 architecture decision，记录本计划已批准的
双模式边界；不得通过修改旧 decision 隐藏先前 local-only 设计。

## 2. 产品范围

### 2.1 Public prepared demo

公共模式面向招聘者、导师和普通访客。它允许访客：

- 查看固定的自然语言问题；
- 查看 prepared synthetic CSV 的表头、行数、Y/X/Z 角色和可下载副本；
- 点击一次明确标注为 replay 的按钮；
- 查看四阶段 workflow 投影、visitor-safe 数值、support 状态、warnings、图表和限制；
- 查看简短的方法与隐私说明；
- 跳转到代码、架构说明和 `Duplicate this Space`。

它不得：

- 调用 Gemini、Prior Labs 或其他外部推理服务；
- 读取任何 API key、token 或 secret；
- 重新拟合模型或重新计算 headline number；
- 把预存状态动画描述成正在发生的 live agent execution；
- 接受公共原始 Space 上的任意 prompt 或 CSV 执行；
- 暴露机器 trace、服务 metadata、内部 ID 或未映射错误。

推荐按钮文案：

> Replay the verified example

页面必须紧邻按钮说明：

> This replays a previously executed and independently verified workflow. No API call is made.

### 2.2 User-owned duplicated Space

自定义分析模式面向愿意使用自己服务账户的技术用户。公共页面只提供说明和
`Duplicate this Space` 链接；用户在复制后的私有 Space 中：

1. 接受 Google Gemini 与 Prior Labs 各自的账户、license、quota 和费用边界；
2. 在 Space Settings 中配置 Gemini secret 和 TabPFN secret；
3. 上传严格限定的 CSV；
4. 输入 bounded prompt；
5. 明确确认 prompt 发往 Google、选择的 Y/X/Z rows 发往 Prior Labs；
6. 运行现有的 one-request Gemini compiler、typed runtime、managed TabPFN 和 evidence gate。

复制后的 live mode 继续保持：

- exactly one continuous outcome Y、one continuous treatment X、one scalar IV Z；
- no baseline covariates W；
- 120–256 rows、exactly three selected numeric columns 和现有 distinct-value gates；
- Gemini 不接收数据行或实际 intervention values；
- managed TabPFN 接收明确授权的 Y/X/Z rows 和 prediction grids；
- no retry、no Gemini bypass、no sklearn fallback；
- outside-support、证据失败或 provider failure 时不显示数值；
- 每次成功运行产生新的 immutable artifact path。

### 2.3 明确不进入 v1

- 在公共共享 Space 页面收集访客的 long-lived API keys；
- 用项目所有者的 keys 为匿名访客提供任意输入分析；
- 用户账户、数据库、支付、订阅、团队 workspace 或 usage dashboard；
- general causal-method router、binary/multi-arm treatment、W support 或 Hillstrom route；
- 把 prepared result 升级为论文或 locked Track T headline；
- 同站 ephemeral BYOK、OAuth broker 或多租户 credential vault。

如果未来需要在同一公共页面直接接受访客 keys，必须新建独立安全计划，至少覆盖 TLS、
request isolation、secret zero-persistence、日志脱敏、上传 TTL、并发身份隔离和隐私政策；
不得把该能力顺带加入本计划。

## 3. Prepared demo artifact contract

### 3.1 输入必须冻结

prepared demo 使用一个公开、可再分发的 synthetic CSV，不得使用真实、licensed、private、
PII 或用户上传数据。冻结内容至少包括：

- `prepared_demo_id` 和 schema version；
- 精确 prompt；
- CSV bytes 和 SHA-256；
- Y/X/Z role mapping；
- row count、seed 和 intervention-label contract；
- Gemini website profile ID/hash；
- managed TabPFN profile ID/hash；
- 生成 result 的 DCFA source/commit identity；
- 生成日期和 external service metadata；
- result bundle、evidence record 和验证状态。

prepared CSV 和 prompt 必须在运行前冻结。不得先看结果再修改输入来获得更好看的数值或
warnings；如需改变输入，创建新的 `prepared_demo_v2` 并保留 v1。

### 3.2 公开资产和机器审计资产分离

建议发布包分为两个层次：

```text
public_showcase/
├── prepared_demo_manifest.json
├── prepared_demo.csv
├── prepared_prompt.txt
├── visitor_result.json
├── visitor_plot.png
└── verification_summary.json

full_verification_bundle/
├── specification.json
├── result_bundle.json
├── evidence_records.jsonl
├── numerical_core.json
├── backend_manifest.json
├── report_manifest.json
└── remaining independently verifiable artifacts
```

`public_showcase/` 可以随 Space 代码发布。完整验证包只有在 secret/credential/路径/服务响应
检查通过后才可作为 release asset 或公开下载；默认访客 DOM 不读取它的内部字段。

### 3.3 生成与版本规则

- 在 UI P0/P1 和 Space artifact contract 冻结后，使用一次明确授权的 live run 生成新目录；
- 不复用 source hash 已经过期的 local artifact 冒充当前 release artifact；
- 生成后运行独立 artifact verifier；
- public projection 只能从已验证 bundle 派生，不手工复制数值；
- manifest 绑定 public projection、prepared CSV、prompt 和完整 bundle 的 hashes；
- 任一输入、profile、源代码或展示投影的实质变化都创建新版本；
- 不覆盖旧 showcase 来让重新运行看起来“干净”。

### 3.4 Zero-network contract

prepared demo 的正式定义是**读取和展示已验证结果**，不是使用缓存命中掩盖外部调用。

自动测试必须证明：

- Gemini client 和 TabPFN client 不被 import 或构造；
- credential loader 不被调用；
- 外部网络被禁用或 provider client 被设置为 fail-on-call 时，demo 仍完整工作；
- 点击 replay 不创建新的 analysis artifact；
- visitor value、warnings 和 plot projection 与 frozen showcase manifest 一致；
- replay 状态使用 “Previously executed” 或等价语义，不伪装实时进度。

## 4. Hugging Face Space 架构

### 4.1 一个代码库，两种运行能力

采用 Docker Space 复用现有 FastAPI + Gradio 服务。运行模式由能力检查决定：

| Space 状态 | Prepared demo | Custom live mode |
|---|---:|---:|
| Public original，无 secrets | available | disabled; show duplication instructions |
| User duplicate，无 secrets | available | not ready; list missing secret names only |
| User duplicate，有两个 secrets | available | available after profile/readiness checks |

公共原始 Space 不配置所有者 Gemini/TabPFN secrets。即使有人绕过 UI，也不能让 custom endpoint
使用缺失 secret 或自动 fallback。

### 4.2 Secrets contract

实现时选择专用、不含值回显的环境变量名，例如：

- `DCFA_SPACE_GEMINI_API_KEY`；
- `DCFA_SPACE_TABPFN_TOKEN`。

本地 mode-600 credential-file workflow 保持可用；Space secrets 是独立 adapter，不得把环境
secret 写入仓库文件、artifact、trace、health payload 或异常上下文。

`/readyz` 需要拆分语义：

- base readiness：public showcase assets、schema/profile、visitor rendering 和只读服务可用；
- live readiness：两个 secrets、可写 ephemeral artifact location 和 live profiles 可用。

公共原始 Space 在没有 secrets 时仍必须通过 base readiness；health/readiness payload 只报告
布尔能力，不报告 secret 内容、长度、前缀或 provider error context。

### 4.3 Custom mode execution isolation

当前 managed client 使用进程级 token setter。Duplicated Space 初版仍只面向其所有者，可继续
使用单 worker、队列和 `finally` reset，但必须通过并发与异常测试证明 token 不跨请求残留。

如果未来允许同一 duplicate 被多人共享，必须先改为 request-scoped client 或一次请求一个
隔离 subprocess/container；不得依赖一个可变的全局 access token 支持多租户。

### 4.4 Storage and retention

- prepared assets 只读且随版本发布；
- custom upload 和生成 artifacts 默认使用 Space 的 ephemeral storage；
- 不默认挂载 persistent storage；
- 页面明确说明 duplicated Space owner 对 retention 和 access 负责；
- 临时上传文件和失败请求残留需要 bounded cleanup；
- 不启用 Gradio public share、monitoring、第三方 analytics 或包含请求正文的 access log。

### 4.5 Space repository metadata

实施时补齐 Hugging Face Space 所需的最小 metadata 和说明：

- Docker SDK 和受支持的端口；
- license 与第三方服务说明；
- prepared-demo / duplicate-live 两种模式；
- 如何 Duplicate Space；
- 两个 secret 的名字和获得方式，但不提供或示例化真实 secret；
- 数据分别发送给 Google 和 Prior Labs 的说明；
- `development_only`、no-W、continuous-treatment scope 和非通用工具限制；
- 冷启动、quota、provider failure 和免费硬件休眠预期。

## 5. 页面信息架构

P0/P1 完成后，Space 页面在其 visitor-safe 结构上增加以下入口：

1. Hero：一句话说明 agent 把问题编译成受限 specification，并用确定性工具生成可验证结果；
2. Primary CTA：`Replay the verified example`；
3. Prepared input：可查看 prompt、Y/X/Z mapping 和 synthetic CSV 摘要；
4. Workflow replay：四个明确标注为 previously executed 的用户阶段；
5. Result：自然语言答案、support、重要 warning、图和 development-only 说明；
6. Trust section：zero API call、prepared artifact hash、验证摘要和代码链接；
7. Secondary CTA：`Duplicate this Space to analyze your own data`；
8. Custom-mode explanation：两个 secrets、两次外部数据边界和运行限制；
9. Scope and limitations。

公共原始 Space 不显示可提交的 key/password 字段。它可以展示 custom input 的静态说明或
disabled preview，但不得让访客误以为上传会在当前公共实例中执行。

## 6. 实施阶段

### HF0：冻结 architecture decision 和 artifact schema

交付：

- 在 `docs/DECISIONS.md` 追加双模式 release decision；
- 定义 prepared demo manifest、visitor result 和 verification summary schemas；
- 选定 synthetic CSV、prompt 和版本命名；
- 定义 base/live readiness contract。

验收：schema、claims 和数据边界评审通过；不进行 live API call。

### HF1：实现 zero-API prepared replay

交付：

- frozen showcase loader；
- prepared input 展示；
- visitor-safe replay/result/plot；
- zero-network 和 no-credential tests；
- tamper/hash mismatch fail-closed tests。

验收：在删除所有 credential、禁用网络后，prepared demo 仍完整工作且没有新 artifact。

### HF2：实现 duplicate-owned live capability

交付：

- Space environment-secret adapter；
- base/live readiness 分离；
- public original custom mode disabled state；
- duplicate 配置说明；
- custom live path 与现有 typed runtime 的集成测试。

验收：missing-secret 不执行；fake provider happy/failure paths 通过；无 secret 出现在 DOM、日志
或 artifact。真实 bounded smoke 需要 duplicate owner 的单独明确授权。

### HF3：构建和部署 Space

交付：

- Docker Space configuration；
- pinned dependency installation；
- health/readiness checks；
- public Space README 和 limitation text；
- immutable release identity 显示。

验收：Hugging Face clean build 成功；公共 URL 在无 secrets 状态可用；prepared replay 零外部
调用；cold start 后恢复；旧进程/旧 revision 不会代表当前 release。

### HF4：浏览器与安全验收

至少覆盖：

- desktop 1280 px 和 mobile 390 px；
- 键盘、标题层级、focus、live status 和图表替代文本；
- prepared replay；
- missing-secret duplicate；
- configured-secret duplicate 的 fake-client workflow；
- direct URL、iframe 和 new-tab fallback；
- page source/DOM credential 和内部字段扫描；
- no outbound request assertion for prepared mode；
- provider failure、outside-support 和 evidence mismatch 的 no-number behavior。

### HF5：接入个人网站

只有 HF0–HF4 完成后：

- 使用 reviewed HTTPS Space URL 配置个人站的 `DcfaDemoEmbed.astro`；
- 如果 host framing policy 不兼容，使用 screenshot/video + direct-link fallback；
- 增加独立 DCFA project entry，区分 TabCF research 与 agent workflow engineering；
- 运行个人网站 `npm run verify`；
- 验证 GitHub Pages production page、移动端、键盘、外链和 iframe；
- 经用户明确确认后再公开发布项目文案与简历链接。

## 7. Verification matrix

| Boundary | Required evidence |
|---|---|
| Prepared mode has zero API usage | network-disabled browser/integration test; fail-on-call Gemini/TabPFN clients |
| Stored result is authentic | artifact verifier success plus prompt/CSV/result/commit hashes |
| Visitor projection is faithful | exact raw-value parity before tested display rounding; warning/support parity |
| Public Space has no owner secrets | Space settings review, env/readiness test, secret-pattern scan |
| Duplicate missing secrets fails closed | no provider construction, no output artifact, actionable safe message |
| Duplicate custom run preserves boundaries | exactly one Gemini request, zero rows/actual interventions to Gemini, bounded TabPFN calls |
| Credentials are not persisted | DOM, log, exception, artifact and filesystem scans |
| Unsupported requests stay blocked | no value, plot or evidence on outside-support/invalid scope |
| Public deployment is current | visible short revision matches deployed release commit |
| Personal-site integration is safe | reviewed HTTPS URL, iframe/direct-link test, `npm run verify` |

## 8. Release gate

正式公开 URL 需要同时满足：

1. P0/P1 acceptance 已完成；
2. prepared artifact 是当前 release identity 下新生成并独立验证的版本；
3. public original 不含任何 owner Gemini/TabPFN secret；
4. prepared replay 的外部网络调用计数为零；
5. public original 的 custom mode 不能执行，只引导 Duplicate Space；
6. duplicate-live fake-client acceptance 完整通过；
7. public Space 的 health/base readiness 为 200；
8. mobile、keyboard、DOM redaction 和 direct-link/iframe 检查通过；
9. claims 明确区分 production website、precomputed demonstration 和 scientific evidence；
10. 个人网站尚未接入临时、未验收或会变化的 share URL。

任何 hard gate 失败都阻止正式公开，不用漂亮截图或已有 local smoke 抵消。

## 9. 可以公开表达的能力

可使用的核心描述：

> DCFA is an auditable causal-analysis agent that compiles bounded natural-language requests
> into typed specifications, delegates numerical work to deterministic tools, blocks unsupported
> claims, and links displayed results to verifiable evidence.

prepared demo 应称为：

- a precomputed replay of a verified end-to-end workflow；
- a portfolio demonstration of agent architecture, safety gates and evidence handling；
- a synthetic, development-only example。

不得称为：

- a live analysis when replaying stored output；
- production causal advice；
- proof of IV validity；
- locked or publishable Track T evidence；
- evidence that the agent outperforms the fixed workflow；
- a general causal-analysis system。

## 10. 实施 handoff 要求

最终 handoff 至少报告：

- P0/P1 dependency 的 commit 和验收证据；
- prepared prompt、CSV、profile、artifact 和 release identities；
- zero-network test 的具体命令与结果；
- Space repository/URL、Docker build 和 health/readiness；
- public original 是否完全无 secrets；
- duplicate missing/configured-secret tests；
- desktop/mobile/keyboard/iframe QA；
- personal website verify 和部署状态；
- 所有未验证的 live provider、cost、quota、retention 或 cross-platform 边界；
- DCFA commit、push destination、最终 Git 状态和个人网站对应 commit。

## 11. 实施时需重新核对的官方资料

这些接口和平台行为可能变化，实施与正式发布当天必须重新查阅官方资料，而不能只依赖本计划：

- Hugging Face Spaces overview、Docker Spaces、secrets 和 Duplicate Space 行为：
  `https://huggingface.co/docs/hub/spaces-overview`
- Hugging Face Space management：
  `https://huggingface.co/docs/huggingface_hub/guides/manage-spaces`
- Gemini API key/security requirements：
  `https://ai.google.dev/gemini-api/docs/api-key`
- Prior Labs `tabpfn-client` authentication 和 cloud-data boundary：
  `https://github.com/PriorLabs/tabpfn-client`

如果官方行为与本计划冲突，应先更新 architecture decision 和本计划版本，再实施；不得通过
未记录的兼容层或 silent fallback 绕过平台变化。
