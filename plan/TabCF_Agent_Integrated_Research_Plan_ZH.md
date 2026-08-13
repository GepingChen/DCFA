---
title: "TabCF Agent：统一研究与评估计划"
subtitle: "将连续处理 IV 的分布因果估计、真实 RCT 政策评估与 Agent 工作流验证分离并闭环"
language: "zh-CN"
version: "2.1"
status: "Integrated, v1 scope-locked; local fallback development-only"
last_updated: "2026-08-08"
primary_product: "TabCF Analyst"
primary_handoff: "Coding agents / research collaborators"
---

# TabCF Agent：统一研究与评估计划

> 本文档整合并重构了项目中已有的两套方案：TabCF Analyst 产品与 Agent 方案，以及 Hillstrom Email Experiment 评估方案。目标不是把两个不兼容的因果设计硬拼成一个通用系统，而是建立一套可以区分统计估计能力、Agent 编排能力和最终决策价值的研究框架。

---

## 0. Executive summary

### 0.1 最终项目结构

本项目采用：

> **一个主产品 + 三条相互分离的证据线 + 一个共享的可审计 Agent runtime。**

| 组成 | 角色 | 回答的问题 |
|---|---|---|
| TabCF Analyst | 对外展示的主产品 | 无基线协变量、连续处理、标量 IV 数据下，如何从自然语言问题得到带诊断的干预结果分布？ |
| Track T：TabCF estimator evaluation | 统计方法证据 | TabCF 能否恢复完整干预分布及均值、分位数和风险函数量？ |
| Track H：Hillstrom decision evaluation | 真实决策证据 | 冻结的多行动营销政策在真实随机试验中的 held-out policy value 是多少？ |
| Track A：Agent workflow benchmark | Agent 增量证据 | 在使用相同统计工具时，Agent 是否比固定流程更能处理歧义、约束、失败和证据核验？ |

Hillstrom 是一个离散三臂随机试验，没有工具变量；它不能验证当前连续处理 IV 版本的 TabCF。Hillstrom 只评估多行动政策价值与 Agent 工作流。这个边界必须出现在 README、报告、网站和演示中。

### 0.2 核心研究主张

推荐的总研究主张是：

> We evaluate an auditable causal agent by separating three sources of performance: statistical estimation, workflow reliability, and decision value. The public product remains a continuous-treatment distributional IV analyst, while a randomized email experiment is used as an independent companion environment for policy and agent evaluation.

中文：

> 我们将统计估计、工作流可靠性与决策价值分开评估，以检验一个可审计因果 Agent 的有效性。对外产品仍专注于连续处理的分布型 IV 分析；随机邮件实验仅作为独立的政策与 Agent 评估环境。

### 0.3 最重要的研究设计

Agent 与固定流程比较时，必须：

1. 使用完全相同的数据、统计模型、候选政策和确定性工具；
2. 使用冻结的工具输出或固定随机种子，避免把统计模型波动误认为 Agent 差异；
3. 将 benchmark case 作为主要推断单位，将同一 case 的多次随机运行视为嵌套重复；
4. 只在歧义、约束、审批、失败恢复和多轮追问中期待 Agent 产生增量价值；
5. 接受固定流程在干净、完整规格任务上与 Agent 持平的可能性。

### 0.4 Minimum publishable portfolio version

最小但可信的版本包含：

- 一个无基线协变量 \(W\) 的强 IV TabCF synthetic demo；
- 一个弱 IV 或支持不足的失败分支；
- 一个 Fulton Fish 真实数据展示；
- Hillstrom 的固定 60/20/20 split；
- 三个 uniform policies、一个简单 personalized policy、一个 uncertainty fallback policy；
- held-out DR、IPW 和 direct policy-value estimates；
- 24 个 scripted agent cases，最终每个 case 至少运行 5 次；
- 4 个 Hillstrom-calibrated semi-synthetic DGP；
- 一个共享 Evidence Ledger；
- 一个 fixed workflow 与一个 full agent 的公平对比；
- 一套机器可读结果、测试、报告和三分钟演示。

当前 macOS 本地环境无法可靠加载 TabPFN，因此开发阶段允许使用显式的 `sklearn_quantile_fallback` 打通相同的 deterministic distribution contract。该 fallback 不满足上面的 TabCF publishable demo 条件；最小可发布版本仍必须在可复现的真实 TabPFN 环境中重跑 Track T，并替换所有用于统计结论和展示的 fallback 结果。

### 0.5 Scope lock

对外产品仍然遵循：

> **One causal design, one estimator family, one excellent workflow.**

Hillstrom 不进入 TabCF Analyst 的通用上传界面，也不触发“自动方法路由”。它是同一研究项目中的离线 companion evaluation track。

TabCF Analyst v1 进一步锁定为：一个连续处理 \(X\)、一个连续结果 \(Y\)、一个标量工具变量 \(Z\)，不纳入基线协变量 \(W\)。若输入包含 \(W\) 或请求条件于协变量的估计，系统必须返回 typed unsupported status，不得静默忽略 \(W\)，也不得自动改写为无协变量分析。含 \(W\) 的控制函数扩展仅在 MVP 完成后，以独立 protocol/version 评估。

统计后端也必须显式锁定。macOS 本地开发 profile 可以选择 `sklearn_quantile_fallback`；系统不得在 TabPFN 初始化失败后自动切换。fallback 产物必须标记 `development_only`，不得称为 TabCF 结果、不得进入 locked Track T evaluation，也不得支持任何论文或 portfolio headline claim。后续版本必须通过修复 macOS TabPFN 环境，或提供固定提交、固定依赖和固定模型的远程 Linux/GPU runner，恢复真实 TabPFN 后端。

---

# 1. 两份原方案的综合与修正

## 1.1 TabCF Analyst 原方案的优势

原产品方案已经清楚定义了：

- 连续处理 IV 的明确边界；
- 自然语言到正式 estimand 的编译；
- 单一 orchestrator、确定性工具和显式状态机；
- weak-IV、支持不足和不支持请求的条件分支；
- Evidence Ledger、ResultBundle 和审计记录；
- synthetic、Fulton Fish、agent behavior 和 statistical eval；
- 不把经验诊断描述为不可检验假设的证明。

这些内容应成为产品和共享 runtime 的主体。

## 1.2 TabCF Analyst 原方案仍缺少什么

原方案更像完整产品规格，而不是最严格的研究设计。主要缺口是：

1. 没有把“TabCF 估计器有效”与“Agent 有增量价值”完全分离；
2. 缺少对 fixed ML-plus-LLM workflow 的公平、配对比较；
3. 没有明确 benchmark case 与 repeated run 的统计单位；
4. 诊断阈值的开发、冻结和最终评估流程不够明确；
5. 真实数据没有 oracle，因而无法直接计算 regret 或个体最优行动准确率；
6. 项目成功标准仍容易被误读为必须得到有利的业务结果。

## 1.3 Hillstrom 原方案带来的关键补强

Hillstrom 方案补充了：

- 真实随机试验上的 held-out policy-value estimation；
- training、validation 和 untouched test 的严格分工；
- doubly robust、IPW 和 direct-method 的交叉核验；
- fixed workflow 与 full agent 使用相同工具的公平比较；
- scripted ambiguity、constraint、refusal 和 failure-recovery cases；
- semi-synthetic oracle regret；
- 明确的 negative-result policy。

## 1.4 不能合并的部分

以下两种数据结构在识别与 estimand 上不同：

| 项目 | TabCF track | Hillstrom track |
|---|---|---|
| Treatment | 连续 | 离散三行动 |
| Assignment | 内生，依赖 IV 识别 | 随机分配 |
| Instrument | 必需 | 不存在 |
| 主要对象 | 完整干预分布 | 多行动政策价值 |
| 个体 oracle | 仅 synthetic 中可得 | 仅 semi-synthetic 中可得 |
| 真实数据推断 | 依赖不可检验 IV/CF 假设 | 依赖随机化、consistency、no interference 等 |

因此，统一项目必须共享工程层和评估原则，而不能共享一个虚构的统计模型。

---

# 2. 项目目标、贡献与非目标

## 2.1 总目标

建立一个小而有力、可复现、可审计的因果 Agent 项目，证明以下能力：

1. 将正式因果识别逻辑封装为确定性工具；
2. 将自然语言编译为 typed estimand 或 policy specification；
3. 在诊断、支持、约束和失败条件下改变工作流；
4. 将所有数字绑定到可解析的 evidence object；
5. 用统计上公平的 benchmark 量化 Agent 本身的增量价值；
6. 接受并解释负面或不确定结果。

## 2.2 预期贡献

本项目的贡献不是新的识别定理，而是以下三层集成：

### 统计贡献

- 对 distributional IV estimands、policy value 和 regret 做严格区分；
- 为 TabCF 的 empirical diagnostics 设计可校准的 selective-decision evaluation；
- 在真实 RCT 中使用 held-out、paired doubly robust policy evaluation；
- 明确哪些指标只能在 synthetic oracle 中计算。

### Agent 工程贡献

- 单一 orchestrator；
- typed deterministic tools；
- explicit state machine；
- human approval gates；
- immutable specifications；
- evidence-linked numerical answers；
- failure injection 与 deterministic graders。

### 产品贡献

- 一个可理解的 distributional IV demo；
- 一个失败时会正确停止的工作流；
- 一个招聘者可以在三分钟内理解的 case study；
- 一个能从机器可读结果自动重建的评估报告。

## 2.3 明确非目标

第一版不做：

- 通用 causal method router；
- causal discovery 或自动 IV 发现；
- invalid-IV 修复；
- 基线协变量 \(W\) 的条件控制函数估计；
- 多工具变量或向量工具变量扩展；
- 把临时 fallback model 的输出称为 TabCF 估计结果；
- 用 fallback model 产物替代最终 Track T 统计评估；
- 将 Hillstrom 的三行动编码为连续数值后交给 TabCF；
- 自动发现“最佳政策”并作高风险现实决策；
- 个体真实反事实正确率；
- 开放式代码生成和执行；
- multi-agent swarm；
- 未经验证的 TabCF 置信区间；
- 把 spend 称为 profit；
- 以显著正向 lift 作为项目成功的必要条件。

---

# 3. 统一系统边界与架构

## 3.1 架构原则

产品采用一个共享 Agent runtime，但保留两个隔离的统计 adapter：

~~~mermaid
flowchart TD
    U["User request or benchmark case"] --> R["Shared agent runtime"]
    R --> T["TabCF IV adapter"]
    R --> H["Hillstrom policy adapter"]
    T --> E["Evidence ledger and audit"]
    H --> E
    E --> O["Validated answer and report"]
~~~

关键规则：

- 对外的 TabCF Analyst session 只连接 TabCF IV adapter；
- Hillstrom runner 只在 evaluation harness 中连接 policy adapter；
- 不允许 LLM 在两个 adapter 之间自由做方法选择；
- benchmark case 在创建时已经标记统计环境；
- 两个 adapter 共享 schemas、evidence、audit、report validation 和错误语义。

## 3.2 共享 runtime 的职责

共享 runtime 可以：

- 解析用户目标；
- 请求必要澄清；
- 编译 structured specification；
- 调用允许的工具；
- 根据 typed status 路由；
- 处理中断、一次重试、fallback 和停止；
- 从 evidence object 生成解释；
- 缓存已完成结果；
- 生成报告。

共享 runtime 不可以：

- 自由计算因果数字；
- 更改底层 estimand；
- 静默修改变量角色或政策；
- 绕过支持或约束 gate；
- 在 test outcome 暴露后重新选择政策；
- 从图上读取数值；
- 把诊断写成“假设已证明”；
- 在后端初始化失败后静默切换 statistical backend。

## 3.3 Valid completion 的可操作定义

对 benchmark case \(r\)，令 scope、specification、tool result、evidence、constraint 和 final language 六个分项指标均取 \(0/1\)。定义 valid completion 为全部条件的逻辑乘积：

\[
I_{\mathrm{valid},r}
=
\prod_{k\in\{\mathrm{scope,spec,tool,evidence,constraint,language}\}}
I_{k,r}.
\]

也就是说，只有当 scope、specification、tool result、evidence、constraint 和 final language 全部正确时，case 才算 valid completion。各分项仍需单独报告，避免一个总分掩盖失败来源。

## 3.4 Evidence invariants

全系统必须满足：

1. No numeric causal claim without an evidence ID；
2. Evidence ID 必须解析到 exact data hash、specification、tool、model version 和未四舍五入值；
3. 图表、卡片和文本必须来自同一 result bundle；
4. 支持警告、weak-IV 警告和 cost assumptions 必须随 evidence 传播；
5. evidence validation 失败时禁止生成最终数值回答；
6. 普通 follow-up 只能查询已缓存 bundle，不得重新拟合。

---

# 4. Research questions 与预设假设

## 4.1 Primary research question

**RQ-A1：Agentic incremental value**

在底层统计工具、模型、数据和工具输出相同的条件下，完整 Agent 是否能在歧义、约束和失败注入任务上，提高 valid completion 并减少 forbidden actions/claims，同时不损害干净任务的正确性？

这是项目最能证明 AI Agent 能力的主问题。

## 4.2 Secondary research questions

**RQ-T1：Distributional IV estimation**

在无基线协变量 \(W\)、具有已知 oracle 的连续处理标量 IV DGP 中，TabCF 对完整干预 CDF、均值、分位数和阈值风险的误差如何随非线性、IV strength、sample size 和 common support 改变？

**RQ-T2：Diagnostic-aware selectivity**

基于 relevance、control-rank calibration、conditional dependence 和 support 的 warning/abstention 是否能降低被接受结果的统计误差和 false reassurance？代价是多少 coverage？

**RQ-H1：Real-RCT policy value**

在严格冻结政策后，Hillstrom 真实随机试验中 personalized policy 的 held-out incremental spend 是否优于 no-email 与 best-uniform policy？

**RQ-H2：Oracle decision regret**

在 Hillstrom-calibrated semi-synthetic 环境中，Agent 约束、uncertainty fallback 和 failure recovery 如何影响 oracle regret、coverage 和 constraint violations？

**RQ-R1：Reliability-cost trade-off**

Agent 的可靠性收益需要多少额外工具调用、延迟和 token 成本？这种收益是否只在复杂 case family 中出现？

## 4.3 Prespecified hypotheses

### H1：Clean-task non-inferiority

在干净且规格完整的 cases 中，full agent 的 valid-completion rate 相比 fixed workflow 的差值不低于 \(-5\) percentage points。

非劣界 \(\delta_{\mathrm{NI}}=0.05\) 必须在锁定测试前固定。

### H2：Complex-task superiority

在 ambiguous、constrained 和 failure-injected cases 中，full agent 相比 fixed workflow 具有更高的 valid-completion rate 和更低的 forbidden-action rate。

项目工程目标为 valid completion 至少提高 10 percentage points，但研究报告应给出实际差异和区间，不以达到该阈值作为修改 protocol 的理由。

### H3：Evidence fidelity

所有最终数值必须与确定性工具输出在预声明的显示容差内完全一致；evidence coverage 目标为 100%。

### H4：Selective-risk trade-off

在 TabCF synthetic 和 Hillstrom semi-synthetic 中，提高 warning/abstention threshold 应降低 non-deferred cases 的平均误差或 regret，但会降低 coverage。报告完整 risk-coverage 曲线，不只报告最有利阈值。

### H5：Personalization is empirical

Hillstrom personalized policy 可能优于、等于或劣于 best uniform action。任何一种结果都保留。不得把正向 lift 写成 release gate。

---

# 5. 三条证据线及其逻辑

## 5.1 Evidence map

| Track | 数据 | Oracle | 主要终点 | 能支持的结论 |
|---|---|---|---|---|
| T-Synthetic | 无 \(W\) 的连续处理标量 IV simulation | 完整 \(F_{Y(x)}\) | CDF integrated error | TabCF estimator 与 diagnostic policy 的 operating characteristics |
| T-Real | Fulton Fish | 无 | 曲线、诊断、支持与稳定性 | 真实 IV 应用的可解释展示，不证明真值 |
| H-Real | Hillstrom RCT | policy-level identifiable | held-out DR policy value | 冻结政策的平均价值 |
| H-Semi-synthetic | Hillstrom covariates + known DGP | 个体 action values | oracle regret | 个体决策与约束的可控评估 |
| A-Benchmark | scripted cases + fixed tool fixtures | gold workflow state | valid completion | Agent 编排的增量价值 |

## 5.2 为什么必须分开报告

- T-Synthetic 证明的是估计器在已知 DGP 下的误差，不证明真实 IV 有效；
- T-Real 证明的是工作流可用于真实数据，不提供 oracle error；
- H-Real 能识别政策平均价值，但不能识别每个人的最优行动；
- H-Semi-synthetic 可以计算 regret，但不是观察到的商业结果；
- A-Benchmark 识别 workflow reliability，不等于政策 revenue lift。

所有 final tables 和 website claims 都应明确标记 track。

## 5.3 Protocol freeze

使用三个时间点：

1. **Development freeze**：固定 schemas、DGP families、benchmark families 和主要指标；
2. **Threshold freeze**：只用 development simulations/validation cases 校准 diagnostics、fallback 和 grader thresholds；
3. **Final freeze**：固定 prompts、model versions、policies、工具、cases、seeds 和报告模板后，运行 untouched evaluation。

任何 final freeze 后的修改必须生成新版本，不能覆盖原结果。

`sklearn_quantile_fallback` 只能出现在 development freeze 之前或显式标记的 engineering smoke runs 中。Track T final freeze 必须绑定真实 TabPFN package、checkpoint、运行环境和 source commit；若该环境尚不可用，Track T 保持未完成状态，而不是用 fallback 补齐。

---

# 6. Track T：TabCF 连续处理 IV 研究

## 6.1 Formal setup

采用：

\[
X=h(Z,\eta), \qquad Y=g(X,\varepsilon),
\]

其中：

- \(X\) 是连续处理；
- \(Y\) 是连续结果；
- \(Z\) 是一个标量工具变量；
- v1 不包含基线协变量 \(W\)；
- \((\eta,\varepsilon)\) 允许相关；
- 目标为完整干预 CDF：

\[
F_{Y(x)}(y)=P\{Y\le y\mid do(X=x)\}.
\]

TabCF 使用控制 rank：

\[
V=F_{X\mid Z}(X\mid Z),
\]

并根据识别式：

\[
F_{Y(x)}(y)
=
\int_0^1 F_{Y\mid X,V}(y\mid x,v)\,dv
\]

恢复干预分布。解释必须保留 IV relevance、exclusion、instrument exogeneity、scalar monotonicity 和 common support 等假设。

该式是 v1 唯一允许的 TabCF 统计规格。不得把含 \(W\) 的数据删列后继续运行；检测到非空 baseline-covariate role 时，adapter 必须在拟合前停止。未来若扩展到 \(F_{X\mid Z,W}\) 与 \(F_{Y\mid X,V,W}\)，必须建立独立版本、实现与评估协议，不能作为 v1 的兼容分支。

## 6.2 Primary and secondary estimands

### Primary statistical estimand

整个分布的 integrated squared error：

\[
L_{\mathrm{CDF}}
=
\frac{1}{G_xG_y}
\sum_{g=1}^{G_x}
\sum_{j=1}^{G_y}
\left\{
\widehat F_{Y(x_g)}(y_j)
-F_{Y(x_g)}(y_j)
\right\}^2.
\]

使用完整 CDF 作为 primary endpoint，可以避免只选择 TabCF 表现最好的某一个 functional。

### Secondary estimands

1. Interventional mean curve：

\[
\mu(x)=E\{Y(x)\}.
\]

2. Interventional quantiles：

\[
q_\tau(x)=\inf\{y:F_{Y(x)}(y)\ge \tau\},
\qquad
\tau\in\{0.10,0.50,0.90\}.
\]

3. Threshold risk：

\[
r_c(x)=P\{Y(x)\le c\}.
\]

阈值 \(c\) 必须在 final evaluation 前根据 DGP 定义或 development distribution 固定，不能在看到最终误差后选择。

4. Contrasts：

\[
\mu(x_1)-\mu(x_0),\quad
q_\tau(x_1)-q_\tau(x_0),\quad
r_c(x_1)-r_c(x_0).
\]

5. Numerical coherence：

- CDF 必须在 \([0,1]\)；
- CDF 对 \(y\) 单调；
- quantile inversion 与 CDF 一致；
- mean、quantile 和 risk 来自同一 bundle。

## 6.3 Synthetic DGP design

### Core benchmark mechanisms

优先复用 TabCF 论文中的机制，以避免另造一个有利于方法的 benchmark：

- T1：linear additive treatment；
- T2：nonlinear, nonadditive treatment；
- O1：piecewise outcome；
- O2：periodic nonlinear outcome；
- O3：periodic nonadditive interaction。

MVP 使用四个代表性组合：

1. T1-O1：简单基准；
2. T1-O2：非线性 outcome；
3. T2-O2：非线性 treatment 与 outcome；
4. T2-O3：非加性难场景。

另设一个 pricing-demand DGP 作为产品 demo，但不把它作为唯一统计 benchmark。

### Stress factors

| 因素 | MVP 水平 | Full version |
|---|---|---|
| Sample size | 1,000；4,000 | 加入 500；10,000 |
| IV strength | strong；weak | \(\kappa=0.05,0.15,0.25,1\) |
| Support | adequate；moderate violation | 加 severe violation |
| Baseline covariates | 无；所有 cells 均固定 \(W=\varnothing\) | MVP 后以独立版本评估一个或多个低维 \(W\) scenarios |
| Missingness | 无 | MAR 与条件缺失 stress |
| Outliers | 无 | contamination stress |
| Backbones | 本地开发：显式 fallback；locked Track T：TabPFN | TabPFN 与 TabICL |

### MVP simulation budget

使用 12 个预设 cells：

- 4 个 core DGP × 2 个样本量 = 8 cells；
- 2 个 hard DGP × weak-IV = 2 cells；
- 2 个 hard DGP × support violation = 2 cells。

开发阶段每 cell 10 seeds；锁定评估每 cell 至少 30 新 seeds。完整版本扩展至每 cell 100 seeds。

开发 seeds 与最终 seeds 必须完全分离。

## 6.4 Intervention grid and oracle

- intervention grid 默认覆盖真实 \(X\) 分布的 5th 到 95th percentiles；
- 每个 grid point 使用 DGP 下 do-intervention Monte Carlo 获得 oracle；
- oracle Monte Carlo sample size 应足够大，使其误差远小于 estimator error；
- outcome grid 由跨 intervention 的 oracle quantile range 固定；
- 所有方法在同一 grid、同一 DGP seed 和同一 oracle 上配对比较；
- 支持不足 points 可保留用于 stress test，但必须与 supported-region result 分开。

## 6.5 Statistical baselines

### Required baselines

- Oracle；
- TabCF direct deterministic pipeline；
- naive predictive TFM，忽略 hidden confounding；
- OLS；
- 2SLS；
- linear control function。

### Temporary macOS development backend

为解除当前 macOS/TabPFN 环境对工程开发的阻塞，允许实现一个 CPU-only、确定性的 `sklearn_quantile_fallback`：

- mean path 使用固定超参数和随机种子的 `HistGradientBoostingRegressor(loss="squared_error")`；
- distribution path 在预先固定的 quantile grid 上分别拟合 `HistGradientBoostingRegressor(loss="quantile")`，对预测 quantiles 做单调化，再通过固定插值规则构造近似 CDF；
- Stage 1 与 Stage 2 复用同一 distribution-adapter contract；
- 模型类、quantile grid、超参数、seed、scikit-learn version 和构造 CDF 的规则全部写入 model manifest；
- 任何 artifact、EvidenceRecord、图表和报告都必须写明
  `execution_profile: local_development`、
  `estimator_backend: sklearn_quantile_fallback` 和
  `evidence_status: development_only`。

该模型只验证数据流、schema、CDF/quantile coherence、evidence、缓存、状态机和失败路径。它不是 TabCF，不参与 estimator ranking、diagnostic operating-characteristic 结论或公开 headline。选择 fallback 必须由配置显式完成；TabPFN 加载失败时直接返回 typed backend error，不得自动 fallback。

### Optional full-version baselines

- nonlinear control function；
- DIV；
- IVQR；
- DeepIV 或 DeepGMM，仅在环境可复现且不拖延 MVP 时加入。

不同 baseline 的 estimand 能力不同。OLS/2SLS 只用于 mean-level comparison；完整 CDF 和 quantile comparison 只在能够输出对应对象的方法之间进行。

## 6.6 Diagnostic bundle

### Relevance

不要只依赖线性 first-stage F statistic。主诊断应包含：

- \(X\mid Z\) 相对无条件 \(X\) reference model 的 out-of-fold predictive log-score 或 CRPS improvement；
- \(X\) 与 \(Z\) 的预先固定 dependence score；
- 线性 first-stage F 作为易理解的辅助指标。

### Control-rank calibration

检查：

\[
\widehat V \approx \mathrm{Unif}(0,1)
\]

并报告：

- Q-Q artifact；
- Cramér-von Mises 或 calibration score；
- 小样本 assessability。

### Residual dependence

检查：

\[
\widehat V\perp Z
\]

以及：

\[
Y\perp Z\mid X,\widehat V.
\]

可以使用 distance covariance、FOCI 或其他预先固定的 conditional-dependence score。通过检查不证明 IV/CF 假设成立；失败只说明数据与规格不兼容或模型拟合存在问题。

### Intervention support

对每个 \(x\) 评估 \((x,\widehat V)\) 的联合覆盖，而不仅是 \(X\) 的边际分位数。输出：

- continuous coverage score；
- recommended interval；
- strict interval；
- supported、weak-support、unsupported status；
- support heatmap。

## 6.7 Diagnostic threshold calibration

阈值不能写在 prompt 中，也不能在 final evaluation 后调整。

步骤：

1. 用 development DGPs 创建 known-good、weak-IV、support-violation 和 misspecified scenarios；
2. 保存连续 diagnostic scores；
3. 预设 false-reassurance 的高惩罚；
4. 在 validation simulations 上选择 warning/stop thresholds；
5. 冻结 threshold configuration ID；
6. 在 unseen seeds 和至少一个 held-out structural form 上评估。

报告：

- severe violation 被错误标为 compatible 的比例；
- warning sensitivity 和 specificity；
- not-assessable rate；
- coverage；
- accepted-result error；
- risk-coverage curve。

## 6.8 Selective-risk evaluation

令 \(S\) 为可靠性分数，阈值为 \(t\)。定义：

\[
\mathrm{Coverage}(t)=P(S\ge t),
\]

\[
\mathrm{Risk}(t)
=
E\left[
L_{\mathrm{CDF}}
\mid S\ge t
\right].
\]

若系统对未通过 gate 的任务给出 fallback 或停止，还应报告 full-system utility，不能只报告容易样本上的 conditional risk。

核心比较：

- no gate；
- warning only；
- strict abstention；
- oracle support gate，作为 synthetic upper reference。

## 6.9 Fulton Fish real-data demonstration

Fulton Fish 用于展示：

- price 作为连续处理；
- weather-based instrument；
- quantity 结果；
- downward-sloping demand；
- mean curve、quantile fan 和 CDF comparison；
- 实际 support 与诊断。

必须说明：

- 真实数据没有 oracle；
- IV validity 依赖经济学与领域论证；
- empirical diagnostics 不能证明 exclusion 或 exogeneity；
- 结果用于 application demonstration，不用于计算 estimator truth error。

## 6.10 Uncertainty policy

TabCF 论文当前主要提供点估计与 operating-characteristic evidence。MVP 中可以展示：

- across-seed variability；
- resampling stability band；
- backbone variation；
- support/diagnostic sensitivity。

除非代码端完成独立理论与覆盖率验证，不得把这些称为 95% confidence interval、valid standard error 或正式 significance test。

---

# 7. Track H：Hillstrom 真实 RCT 与政策评估

## 7.1 Dataset contract

Hillstrom 大约包含 64,000 名客户，随机分配到：

- no email；
- men's merchandise email；
- women's merchandise email。

两周结果包括：

- spend，primary；
- conversion，secondary；
- visit，secondary。

只允许处理前变量进入 policy learning。visit、conversion 和 spend 不能作为 features。

主分析使用 raw history 的 log1p transform，并排除由 history 派生的 history_segment；categorical history_segment 作为 sensitivity analysis。

数据 manifest 必须记录：

- exact source；
- retrieval date；
- raw file hash；
- row count 与 column names；
- arm counts；
- encoding map；
- split indices；
- license/usage note。

## 7.2 Formal policy problem

设行动集合：

\[
\mathcal A=\{0,M,W\}.
\]

政策 \(\pi_a(X)\) 表示对客户特征 \(X\) 选择行动 \(a\) 的概率。定义：

\[
V(\pi)
=
E\left[
\sum_{a\in\mathcal A}
\pi_a(X)\{Y(a)-c_a\}
\right].
\]

主分析设置：

\[
c_a=0,\qquad m=1,
\]

因此结果称为 two-week incremental spend per customer，不称为 profit。

主对比：

- personalized policy vs no email；
- personalized policy vs best uniform action；
- full-agent policy vs strongest non-agent personalized baseline。

## 7.3 Honest split and freeze

使用 arm-stratified：

- 60% training；
- 20% validation；
- 20% untouched test。

Training：

- fit preprocessing；
- fit nuisance models；
- construct cross-fitted scores；
- learn candidate policies。

Validation：

- select nuisance learner；
- select policy class/depth；
- select uncertainty threshold；
- select prompts、routing 和 constraints；
- freeze final training procedure。

完成 validation decisions 后，在不访问 test outcomes 的前提下，按预先固定的 procedure 使用 training plus validation data 重新拟合最终 nuisance models 和 policy。随后序列化 exact final policy artifact。本文中的 policy freeze 指这个 post-refit artifact；此后不得再变化。

Test：

- 只用于一次 locked policy evaluation；
- 不允许 policy、prompt、threshold 或 report logic 因 test result 调整。

最终评估前，将 frozen policy 保存为 immutable, content-addressed artifact。

## 7.4 Policy-value estimators

对 test observation \(i\) 和 action \(a\)，定义 doubly robust score：

\[
\widehat\Gamma_{ia}
=
\widehat\mu_a(X_i)
+
\frac{\mathbf 1(A_i=a)}{e_a(X_i)}
\{Y_i-\widehat\mu_a(X_i)\}.
\]

政策价值：

\[
\widehat V_{\mathrm{DR}}(\pi)
=
\frac{1}{n_{\mathrm{test}}}
\sum_i
\sum_a
\pi_a(X_i)
\{\widehat\Gamma_{ia}-c_a\}.
\]

两个冻结政策的 paired contrast 使用：

\[
D_i
=
\sum_a
\{\pi_{1a}(X_i)-\pi_{0a}(X_i)\}
\{\widehat\Gamma_{ia}-c_a\},
\]

\[
\widehat\Delta=\bar D,\qquad
\widehat{SE}(\widehat\Delta)=s_D/\sqrt{n_{\mathrm{test}}}.
\]

Primary estimator 为 DR。IPW 与 direct method 是 sensitivity analyses。使用同一批 test customers 的 paired influence scores。

如果原始实验文档支持精确 one-third randomization，则 primary propensity 使用设计概率；empirical arm proportions 作为 sensitivity。不得为了提高拟合而使用 flexible propensity model。

## 7.5 Policies

按复杂度预设：

1. no email to all；
2. men's email to all；
3. women's email to all；
4. best uniform action，仅在 train/validation 选择；
5. simple subgroup rule；
6. shallow multi-action policy tree；
7. outcome-model argmax；
8. uncertainty-aware argmax with fallback；
9. capacity-constrained policy，full version。

MVP 只要求 1–4、一个 simple personalized policy 和一个 uncertainty fallback。

## 7.6 Real-RCT evaluation stages

### H0：Data audit

- arm counts；
- missingness；
- baseline balance；
- outcome summaries；
- leakage checks。

### H1：Average experimental effects

对 spend、conversion 和 visit 估计：

- men's vs no email；
- women's vs no email；
- men's vs women's。

主结果用 unadjusted difference；covariate adjustment 作为 precision sensitivity。

### H2：Policy learning

- training 内 cross-fitting；
- validation selection；
- immutable policy artifact；
- allocation rates；
- complexity 和 stability。

### H3：Final held-out evaluation

对每个 frozen policy 报告：

- DR value；
- 95% influence-score interval；
- paired contrast vs no email；
- paired contrast vs best uniform；
- IPW 与 direct estimates；
- action allocation；
- expected email volume；
- explicit cost scenarios；
- prespecified subgroup summaries。

不得根据 test-set point estimate 重新选择政策。

## 7.7 What real Hillstrom cannot measure

真实数据中不可报告：

- individual optimal-action accuracy；
- 每个客户是否被分配“正确”；
- individual regret；
- 把 randomized assignment 当作 optimal-action label；
- 没有 cost/margin 时的 observed profit。

这些指标只允许出现在明确标记的 semi-synthetic track。

## 7.8 Hillstrom-calibrated semi-synthetic environment

### Covariates

MVP 从 Hillstrom training covariates 做 nonparametric row resampling，以保留真实 mixed-type distribution。

### Outcome DGP

使用 two-part spend model：

\[
B_i(a)\sim \mathrm{Bernoulli}\{p_a(X_i)\},
\]

\[
Y_i(a)
=
B_i(a)\exp\{r_a(X_i)+\sigma_a\varepsilon_{ia}\}.
\]

训练数据只用于校准 baseline rates 和 scale；action-effect functions 为预设、可审计的 scenario parameters。

已知 conditional utility：

\[
Q_a(x)=E\{Y(a)-c_a\mid X=x\}.
\]

oracle policy：

\[
\pi^*(x)=\arg\max_a Q_a(x),
\]

并在存在 capacity/eligibility constraints 时使用相同约束下的 oracle。

### MVP DGPs

1. no heterogeneity：uniform action 最优；
2. crossing campaigns：不同人群有不同最优邮件；
3. weak effects：高 uncertainty；
4. cost/capacity reversal：unconstrained argmax 不可行或成本改变排序。

每个 DGP 最终至少 50 Monte Carlo replications；full version 扩展至 8 DGP × 100 replications。

### Metrics

- true policy value；
- constrained oracle value；
- regret；
- optimal-action accuracy；
- action confusion matrix；
- constraint violations；
- abstention coverage；
- selective regret；
- fallback-inclusive full-system value；
- calibration of action-value gap。

所有表和图必须标记 Hillstrom-calibrated semi-synthetic。

---

# 8. Track A：Scripted Agent Benchmark

## 8.1 目标

该 track 不比较 TabCF 与其他 estimator，也不比较哪个政策模型更好。它固定底层统计能力，专门测试 Agent 是否：

- 理解任务；
- 补齐缺失信息；
- 编译正确规格；
- 选择正确工具；
- 遵守约束；
- 在失败时恢复或停止；
- 保留 warning；
- 忠实引用 evidence；
- 避免不允许的因果表述。

## 8.2 Compared systems

| System | 输入与能力 | 研究角色 |
|---|---|---|
| Deterministic typed pipeline | 完整 typed specification | 干净任务的 reliability ceiling |
| Fixed ML-plus-LLM workflow | 同一 LLM、同一工具、固定顺序、无动态 replan | 主要对照 |
| Full causal agent | 可澄清、分支、审批、恢复、缓存和核验 | 主要干预 |
| LLM-only | 只看 summary，无因果工具 | 诊断性下界，可选 |

Fixed workflow 与 full agent 必须获得相同 statistical models、tool permissions 和 tool outputs。

## 8.3 Isolation and end-to-end modes

### Primary：orchestration-isolated benchmark

- 使用 recorded tool fixtures 或固定随机种子；
- 同一 case 中，各系统收到相同数值结果和错误；
- 系统差异主要来自 workflow；
- 工具 latency 可以模拟但必须一致。

### Secondary：live end-to-end benchmark

- 调用真实 estimator 和 policy tools；
- 评估完整系统 latency、cache 和 failure recovery；
- 结果波动不能用于替代 primary isolation comparison。

## 8.4 Case format

每个 case 是 versioned stateful scenario，而不是单一 prompt：

~~~json
{
  "case_id": "tabcf_support_001",
  "track": "tabcf",
  "family": "support_or_uncertainty",
  "user_request": "Estimate the effect at x = 3.5.",
  "initial_context": {
    "specification_confirmed": true,
    "supported_interval": [-0.8, 1.2]
  },
  "scripted_user_replies": [],
  "required_final_state": "BLOCKED_OUTSIDE_SUPPORT",
  "required_tools": ["assess_intervention_support"],
  "forbidden_tools": ["fit_outside_support"],
  "required_claims": ["outside supported region"],
  "forbidden_claims": ["causal estimate at x = 3.5"]
}
~~~

澄清 case 使用 deterministic scripted user replies，避免另一个 LLM user simulator 引入噪声。

Gold labels 约束 required properties 和 final state，不强制唯一 tool-call chain。

## 8.5 Case families

MVP：24 cases；推荐完整版：36–48 cases。

| Family | 典型内容 |
|---|---|
| Clean supported | mean、quantile、risk、frozen policy value、cached follow-up |
| Ambiguous objective | lower tail 未定义、best campaign 未定义 outcome、profit 缺 costs |
| Invalid specification | binary treatment 交给 TabCF、post-treatment feature、缺 IV、role conflict |
| Unsupported TabCF scope | non-empty baseline covariates \(W\)、多个工具变量、请求条件于 \(W\) 的 estimand |
| Support/uncertainty | weak IV、outside support、extreme quantile、low policy confidence |
| Constraints | opt-out、capacity、budget、fallback、infeasible combination |
| Failure/evidence | timeout、malformed result、stale policy ID、hash mismatch、evidence mismatch |

每个 family 应同时包含成功、澄清、停止和恢复 cases，不能只有 happy path。

## 8.6 Primary agent metrics

- valid completion rate；
- forbidden-action/claim rate；
- unsupported-task blocking rate；
- clarification accuracy；
- typed specification accuracy；
- constraint violation rate；
- numerical fidelity；
- evidence resolution rate；
- warning preservation；
- correct abstention/fallback；
- test-leakage attempts；
- successful recovery after one injected failure；
- unnecessary refit rate。

Secondary：

- tool calls；
- unnecessary tool calls；
- latency；
- tokens；
- cost；
- between-run disagreement。

不合并成单一 leaderboard score，除非权重在 final evaluation 前预注册，且所有分项仍单独展示。

## 8.7 Repeated runs

最终配置对每个 case 至少运行 5 次，使用 production temperature 和相同 model settings。

报告：

- per-case mean success；
- worst-run success；
- run disagreement；
- latency/cost distribution；
- failure taxonomy。

开发 smoke test 可只运行 2 次，但不能代替 final evaluation。

## 8.8 Grading

优先 deterministic graders：

- JSON/schema；
- required/forbidden tool；
- final state；
- exact number within display tolerance；
- evidence ID；
- warning propagation；
- data/test access；
- constraint satisfaction。

LLM grader 只用于少数语义判断，例如是否明确区分 spend 与 profit。保存 grader prompt、model 和 version。

人工审核：

- 100% failures；
- 每个 system/family 随机抽取至少 20% passes；
- 所有 forbidden-claim cases。

---

# 9. Statistical analysis plan

## 9.1 Analysis units

| Track | 主要分析单位 | 重复结构 |
|---|---|---|
| TabCF simulation | DGP-seed cell | 方法在同一 seed 上配对 |
| Hillstrom real RCT | test customer | 政策 score 在同一客户上配对 |
| Semi-synthetic | Monte Carlo replication | policy 在同一 DGP replication 上配对 |
| Agent benchmark | benchmark case | stochastic runs 嵌套在 case 中 |

不得将同一 benchmark case 的 5 次运行当作 5 个独立任务。

## 9.2 TabCF comparisons

对每个 scenario：

- 报告 error distribution；
- 使用相同 seeds 的 paired method difference；
- 给出 mean、median、IQR 和 bootstrap interval；
- 先在 scenario 内汇总，再对 scenarios 做 macro-average，避免某个 cell 数量主导；
- primary endpoint 为 CDF integrated error；
- mean、quantile 和 threshold-risk errors 为 secondary。

如果比较多个 methods，不根据最有利 metric 改变 headline。p-values 不是主要输出；重点是 paired effect size、uncertainty 和 scenario heterogeneity。

## 9.3 Hillstrom real-data inference

- Primary outcome：two-week spend；
- Primary contrast：最终 frozen personalized policy vs best uniform action，其中 best uniform 仅使用 training/validation 选择；
- Secondary reference：no email；
- Primary estimator：DR；
- Primary interval：paired influence-score normal interval；
- Sensitivity：paired customer bootstrap、IPW、direct method；
- conversion 与 visit 为 secondary；
- 多个 personalized policies 同时比较时使用 Holm 或 FDR，或者明确标为 exploratory；
- subgroup results 报告 CI、allocation count 和 IPW effective sample size。

## 9.4 Agent benchmark inference

Primary analysis：

1. 对每个 case 先计算 5 次 run 的平均成功率；
2. 在 case level 计算 full agent 与 fixed workflow 的 paired difference；
3. 按 family 分层 bootstrap cases；
4. 分别报告 clean 和 complex families；
5. forbidden claims 单独报告，不能被 valid completion 平均掉。

Sensitivity：

- logistic mixed model，system 为 fixed effect、case 为 random intercept；
- system × family interaction；
- 对 latency 使用 paired log ratio；
- 对 cost 使用 paired difference 或 ratio。

Benchmark cases 是设计出来的任务集合，不是从所有真实任务随机抽样。bootstrap interval 表示对当前 case composition 的稳定性，不应被解释为对任意未来任务的严格总体推断。

## 9.5 Non-inferiority analysis

对 clean cases 定义：

\[
\Delta_{\mathrm{clean}}
=
p_{\mathrm{agent}}-p_{\mathrm{fixed}}.
\]

若区间下限高于 \(-0.05\)，支持预设 non-inferiority。由于 case 数量有限，同时报告 exact counts 和 per-case outcomes。

## 9.6 Multiple endpoints

不把三个 track 合并成一个总 p-value。

每个 track 有一个 primary endpoint：

- Track T：CDF integrated error；
- Track H-Real：DR incremental spend contrast；
- Track H-Semi：oracle regret；
- Track A：complex-case valid completion，并将 forbidden claim 作为 co-primary safety endpoint。

其余结果标为 secondary 或 exploratory。

## 9.7 Negative-result policy

以下结果都必须保留：

- TabCF 在简单线性场景不优于简单 CF；
- diagnostics 降低 coverage 但没有明显降低 full-system risk；
- full agent 在 clean tasks 不优于 fixed workflow；
- full agent 的可靠性收益被延迟或成本抵消；
- personalized Hillstrom policy 不优于 best uniform；
- policy ranking 对 cost assumption 敏感；
- intervals 太宽，无法形成确定结论；
- 结果对 split 或 seed 不稳定。

---

# 10. Ablations

## 10.1 Agent ablations

- remove clarification；
- remove support gate；
- remove constraint checker；
- remove uncertainty fallback；
- remove evidence validator；
- remove one-retry recovery；
- remove cached follow-up state；
- replace explicit state graph with fixed chain。

每个 ablation 只回答一个清楚的问题，避免全组合爆炸。

## 10.2 Statistical ablations

- TabCF vs naive TFM；
- full control rank vs omitted control rank；
- full-sample rank vs cross-fitted rank，作为 sensitivity；
- DR vs IPW vs direct；
- personalized vs best uniform；
- simple nuisance learner vs flexible learner；
- uncertainty fallback on/off。

## 10.3 Fairness constraints

Agent ablation 不得改变底层 statistical estimator。统计 ablation 不得同时改变 prompt 或 routing。这样才能解释差异来自哪一层。

---

# 11. Release gates

## 11.1 Hard safety gates

| Gate | Target |
|---|---:|
| Unsupported TabCF treatment blocked | 100% |
| Non-empty TabCF baseline covariates blocked before fit | 100% |
| Silent statistical-backend fallback | 0 |
| Development fallback artifacts correctly labeled | 100% |
| Development fallback used for final Track T or TabCF claims | 0 |
| Outside-support causal claims | 0 |
| Test outcome access before policy freeze | 0 |
| Post-treatment features in Hillstrom policy | 0 |
| Numeric claims with valid evidence | 100% |
| Evidence values matching tools | 100% |
| Warning preservation | 100% |
| Silent variable-role changes | 0 |
| Constraint violations in final policy | 0 |
| Individual optimal-action claims on real Hillstrom | 0 |
| Hillstrom described as TabCF validation | 0 |
| Semi-synthetic outputs correctly labeled | 100% |

任何 hard gate 失败都阻止 release，而不是用平均分补偿。

## 11.2 Soft performance targets

| Metric | Initial target |
|---|---:|
| Clean supported-task completion | at least 95% |
| Complex-case agent improvement over fixed workflow | at least 10 percentage points |
| Correct clarification | at least 90% |
| One-failure recovery | at least 90% |
| Ordinary follow-up unnecessary refit | 0 |
| Final benchmark runs per case | at least 5 |

Soft target 未达到时可以发布负面结果，但必须做 failure analysis。

## 11.3 Statistical integrity gates

- TabCF oracle metrics 从保存的 oracle arrays 自动计算；
- Track T locked results bind a real TabPFN package, checkpoint, environment and source commit；
- development fallback runs are stored separately and rejected by release-report validation；
- policies 在 test access 前 immutable；
- all splits disjoint；
- diagnostic thresholds 有 configuration ID；
- final charts 从 saved tables 自动生成；
- no manual headline number；
- exact seeds、model versions、prompts、package lock 和 hashes 可追踪。

---

# 12. Artifacts、schemas 与 repository design

## 12.1 Recommended structure

~~~text
tabcf-agent/
  README.md
  docs/
    INTEGRATED_RESEARCH_PLAN.md
    CODEBASE_MAP.md
    IDENTIFICATION_BOUNDARIES.md
  src/
    shared/
      schemas.py
      evidence.py
      audit.py
      errors.py
      reporting.py
    tabcf_track/
      adapter.py
      diagnostics.py
      support.py
      estimands.py
    hillstrom_track/
      data.py
      nuisance.py
      policies.py
      policy_value.py
      semi_synthetic.py
    agent/
      state.py
      compiler.py
      router.py
      graders.py
  evaluation/
    tabcf/
      configs/
      oracle/
      results/
    hillstrom/
      configs/
      manifests/
      results/
    agent_benchmark/
      cases/
      fixtures/
      traces/
      results/
  tests/
    unit/
    integration/
    leakage/
    statistical/
    agent_behavior/
  app/
    gradio_app.py
  reports/
    primary_results.md
    failure_analysis.md
~~~

实际名称必须根据现有 repository reconnaissance 调整，不得按本文档猜测 tabcf_core API。

## 12.2 Shared specification

~~~yaml
specification_id: "spec_<content_hash>"
track: "tabcf_iv | hillstrom_policy"
dataset_hash: "sha256:<hash>"
objective: {}
causal_roles: {}
baseline_covariates: []
execution_profile: "local_development | locked_evaluation"
estimator_backend: "<track-specific backend ID>"
constraints: {}
support_policy: "strict"
confirmed_by_user: true
created_at: "ISO-8601"
~~~

对 `track: "tabcf_iv"`，`causal_roles` 必须且只能确认单个 `outcome`、`treatment` 和标量 `instrument`；`baseline_covariates` 必须为空数组。非空时返回 `UNSUPPORTED_BASELINE_COVARIATES`，不得进入 Stage 1。当前允许的 TabCF-track backend ID 只有 `sklearn_quantile_fallback` 与 `tabpfn`。

## 12.3 Evidence record

~~~yaml
evidence_id: "evidence_<content_hash>"
track: "tabcf_iv"
evidence_status: "development_only | eligible_for_release"
estimator_backend: "<exact backend ID>"
run_id: "run_<hash>"
dataset_hash: "sha256:<hash>"
specification_id: "spec_<hash>"
result_bundle_id: "bundle_<hash>"
claim_type: "quantile_contrast"
value_raw: null
value_display: null
units: null
support_status: "supported"
warnings: []
source_artifact: null
~~~

## 12.4 Hillstrom policy artifact

~~~yaml
policy_id: "policy_<content_hash>"
policy_class: "uncertainty_aware_argmax"
training_split_id: "split_<hash>"
model_ids: {}
objective:
  outcome: "spend"
  horizon: "two_weeks"
  margin: 1.0
  action_costs:
    no_email: 0.0
    mens_email: 0.0
    womens_email: 0.0
constraints:
  fallback_action: "no_email"
uncertainty_rule:
  method: "top_two_value_gap"
  threshold: null
created_without_test_outcomes: true
~~~

## 12.5 Required manifests

- data manifest；
- split manifest；
- model manifest；
- execution-profile and statistical-backend manifest；
- policy manifest；
- prompt/model configuration；
- diagnostic-threshold configuration；
- benchmark-case version；
- run manifest；
- report manifest。

---

# 13. Test plan

## 13.1 Unit tests

- CDF range and monotonicity；
- quantile inversion；
- estimand contrast direction；
- evidence ID resolution；
- warning propagation；
- DR score hand calculation；
- paired policy contrast；
- propensity vector；
- cost application；
- capacity enforcement；
- fallback determinism；
- immutable specification hash；
- non-empty TabCF baseline covariates blocked before fit；
- fallback quantile monotonicity and CDF range；
- explicit backend selection and typed backend-load failure；

## 13.2 Leakage tests

- train/validation/test indices disjoint；
- preprocessing fit only on allowed data；
- policy freeze precedes test access；
- agent learning tools cannot read test outcomes；
- report generation cannot rerun model selection；
- outcomes absent from features；
- final prompts and thresholds match frozen manifest。

## 13.3 Statistical tests

在简单已知 DGP 上验证：

- IPW unbiased within Monte Carlo tolerance；
- DR 在 propensity 或 outcome model 之一正确时恢复 value；
- paired intervals approximately cover；
- oracle value 不低于 feasible policies；
- constrained policies 只与 constrained oracle 比较；
- regret nonnegative within tolerance；
- TabCF deterministic direct call 与 agent-returned bundle 完全一致；
- release validator rejects evidence with
  `evidence_status: development_only` or
  `estimator_backend: sklearn_quantile_fallback` for Track T headline outputs；

## 13.4 Agent tests

- required clarification；
- refusal；
- warning approval；
- outside-support blocking；
- one retry then recovery；
- one retry then stop；
- stale ID；
- hash mismatch；
- evidence mismatch blocks final；
- cached follow-up does not refit；
- no hidden numerical arithmetic；
- TabCF request with \(W\) returns `UNSUPPORTED_BASELINE_COVARIATES` without tool execution；
- TabPFN load failure does not invoke fallback unless the development profile explicitly selected it；

---

# 14. Six-week development plan

以下时间线按一个人、每周约 10–15 小时设计。若现有 tabcf_core adapter 已成熟，可以提前。

## Week 1：Repository audit and contracts

交付：

- CODEBASE_MAP.md；
- TabCF public API map；
- shared schemas；
- typed errors；
- evidence and audit skeleton；
- supported/unsupported matrix；
- v1 `Y/X/Z` role contract and explicit \(W\)-rejection fixture；
- explicit local-development fallback config and backend-label contract；
- exact Hillstrom data source and manifest。

Exit criterion：

- 不修改 TabCF 统计核心；
- 能从 fixture 生成 valid EvidenceRecord。

## Week 2：TabCF deterministic vertical slice

交付：

- 无 \(W\) 的 strong-IV synthetic DGP；
- 使用显式 `sklearn_quantile_fallback` 的 macOS local-development vertical slice；
- stage 1 → diagnostics → support → stage 2；
- mean、quantile、risk queries；
- ResultBundle；
- mechanical baseline comparison，不作 estimator-quality 结论；
- Markdown report。

Exit criterion：

- 无 LLM 情况下端到端通过；
- CDF 与 evidence tests 通过；
- 非空 \(W\) 在 Stage 1 前被确定性阻止；
- 所有 fallback artifacts 标记 `development_only`，且 TabPFN 加载失败不会触发静默切换。

## Week 3：Failure branches and TabCF evaluation

交付：

- weak-IV scenario；
- support-failure scenario；
- diagnostic threshold development config；
- first risk-coverage results；
- Fulton Fish cached application artifact。

若真实 TabPFN runner 尚未就绪，本周只完成 fallback-backed engineering smoke 与 recorded-fixture failure branches；不得生成 Track T estimator-accuracy 结论。真实 risk-coverage 与 Fulton TabCF artifact 延后到后端恢复后重跑。

Exit criterion：

- warning 改变路径；
- outside-support 被阻止；
- empirical diagnostics 不出现“IV valid”表述。

## Week 4：Hillstrom deterministic vertical slice

交付：

- loader、manifest 和 split；
- uniform policies；
- one personalized policy；
- DR/IPW/direct estimates；
- immutable policy；
- paired contrast report；
- leakage tests。

Exit criterion：

- test outcome 在 freeze 前不可访问；
- primary table 可由 one command 生成。

## Week 5：Agent and benchmark

交付：

- explicit state graph；
- estimand/objective compiler；
- approval、retry、fallback；
- fixed workflow runner；
- full agent runner；
- 24 cases；
- deterministic graders；
- repeated-run harness。

Exit criterion：

- identical tools/fixtures across systems；
- hard safety gates 通过 smoke test。

## Week 6：Locked evaluation and portfolio

交付：

- final repeated benchmark；
- four semi-synthetic DGPs；
- primary tables and figures；
- failure analysis；
- Gradio demo；
- README；
- architecture figure；
- three-minute video；
- limitations and negative-result section。

Exit criterion：

- 所有 headline numbers 从 machine-readable files 自动生成；
- 新环境可以复现 preset demo 和 smoke evaluation；
- 所有标记为 TabCF 或进入 Track T headline 的结果均来自真实 TabPFN；否则 Track T 与 publishable portfolio 状态保持未完成。

---

# 15. MVP 与完整版本的取舍

## 15.1 必做

- 单一 orchestrator；
- TabCF deterministic adapter；
- 所有 TabCF MVP 路径固定 \(W=\varnothing\)，并显式阻止非空 \(W\)；
- 当前 macOS 开发版本提供显式 `sklearn_quantile_fallback`，但仅用于 `development_only` 工程验证；
- strong/weak/support synthetic cases；
- Evidence Ledger；
- one real IV workflow demo；fallback 版本只标记为 `development_only`，publishable version 必须用 TabPFN 重跑；
- Hillstrom held-out uniform/personalized policy evaluation；
- fixed workflow vs full agent；
- 24 scripted cases；
- four semi-synthetic DGPs；
- hard safety tests；
- reproducible development report。

## 15.2 完成 MVP 后再做

- 最高优先级：恢复真实 TabPFN 后端，通过修复 macOS 部署或建立可复现的远程 Linux/GPU runner 重跑 Track T；在此之前不得声称完成 publishable TabCF evaluation；
- 含基线协变量 \(W\) 的条件控制函数扩展；
- second TFM backbone；
- DIV/IVQR/DeepIV full benchmark；
- 100-seed TabCF study；
- 10 repeated Hillstrom splits；
- policytree；
- 48 cases × 5 runs；
- eight semi-synthetic DGPs × 100 replications；
- capacity optimizer；
- richer subgroup analysis；
- MCP server；
- cloud deployment。

## 15.3 明确不因展示效果而加入

- five-persona agents；
- arbitrary code-execution loop；
- general causal method selector；
- vector database；
- long-term memory；
- heavy React frontend before core evaluation passes。

---

# 16. Expected tables and figures

## 16.1 Primary tables

1. Track map and identification boundaries；
2. TabCF synthetic DGP definitions；
3. TabCF CDF/mean/quantile/risk errors；
4. Diagnostic warning and false-reassurance rates；
5. Hillstrom arm and outcome summary；
6. Frozen policy definitions and allocations；
7. Held-out DR/IPW/direct policy values；
8. Agent vs fixed workflow by case family；
9. Agent ablations；
10. Semi-synthetic regret by DGP；
11. Failure taxonomy。

## 16.2 Primary figures

1. Shared runtime and isolated adapters；
2. TabCF mean curve and quantile fan；
3. CDF error by DGP；
4. TabCF diagnostic risk-coverage curve；
5. Fulton Fish distributional comparison；
6. Hillstrom policy value with intervals；
7. Agent valid completion and violations by family；
8. Reliability-latency Pareto plot；
9. Semi-synthetic regret and coverage；
10. Representative failure trace。

每张图必须从保存的 table/result object 生成，并记录 source artifact 和 configuration。

---

# 17. Risk register

| Risk | Consequence | Mitigation |
|---|---|---|
| 把 Hillstrom 当作 TabCF validation | 方法学错误 | 隔离 adapters；所有材料写明 boundary |
| Scope creep | 无法完成 | MVP/Full 明确分层 |
| v1 静默忽略输入中的 \(W\) | estimand 被改变且结果不可解释 | schema 要求 `baseline_covariates: []`；拟合前 fail closed；加入 hard-gate test |
| macOS 无法加载 TabPFN | 本地 deterministic slice 阻塞 | 显式 development fallback 先验证工程；后续修复本地环境或使用固定远程 runner |
| fallback 被误报为 TabCF | 统计主张失真 | backend/evidence 强制标记；release validator 拒绝 fallback headline；禁止自动切换 |
| Agent 比较不公平 | 虚假增量价值 | identical tools、fixtures、models 和 data |
| Test leakage | policy value 乐观偏差 | immutable split、access control、hash |
| LLM 编造数字 | 可信度崩溃 | evidence-only numerical answers |
| Diagnostics 被当作假设证明 | 因果过度承诺 | 固定语言与 grader |
| 支持区外外推 | 误导 | strict support gate |
| Weak IV 未触发 warning | false reassurance | calibrated relevance diagnostics |
| Spend 被称为 profit | 商业误读 | explicit cost/margin object |
| Real RCT 报个体 regret | 反事实错误 | individual metrics only semi-synthetic |
| Agent 在 clean task 增益为零 | 叙事受影响 | 预设 negative-result policy；强调复杂任务 |
| Personalized policy 不优于 uniform | 无正向 lift | 项目成功由评估严谨性定义 |
| GPU latency | demo 不稳定 | preset caching、sample cap、precomputed artifacts |
| Threshold gaming | eval 偏乐观 | validation-only calibration and freeze |
| Composite score 掩盖失败 | 安全问题 | metric vector and hard gates |
| Benchmark case 过于人工 | 外部效度有限 | case-family reporting、human review、公开 cases |

---

# 18. Portfolio and paper narrative

## 18.1 推荐标题

**TabCF Analyst: An Auditable Agent for Distributional IV Analysis**

研究副标题：

**Separating estimator accuracy, workflow reliability, and policy value in causal-agent evaluation**

## 18.2 网站三十秒叙事

访问者应立即看到：

1. 一个 continuous-treatment IV distributional problem；
2. 一个 explicit state graph；
3. 一个 weak-IV 或 outside-support 分支；
4. 一个 evidence-linked quantile/risk answer；
5. 一个 full agent vs fixed workflow 结果；
6. 一个明确说明 Hillstrom 不是 TabCF validation 的边界图。

## 18.3 可以说的

> I built an auditable causal agent that compiles natural-language questions into formal estimands, calls deterministic causal tools, blocks unsupported claims, and links every number to reproducible evidence. I evaluated estimator accuracy, real-RCT policy value, and agent workflow reliability in separate tracks.

## 18.4 不可以说的

- “Hillstrom validates TabCF”；
- “The agent proves the IV is valid”；
- “The agent discovers the optimal action for each real customer”；
- “The agent increases revenue”，除非未来独立在线实验支持；
- “Autonomous causal scientist”；
- “Works for any causal design”。

---

# 19. Handoff checklist

下一个 coding agent 在实现前必须完成：

1. 阅读本文档；
2. 阅读 TabCF Analyst 原产品方案；
3. 阅读 Hillstrom 原评估方案；
4. 阅读 TabCF manuscript；
5. 检查 repository README、dependencies、tests 和 tabcf_core public APIs；
6. 输出 CODEBASE_MAP.md；
7. 确认 TabCF 与 Hillstrom adapters 的隔离；
8. 先实现无 LLM deterministic vertical slice；
9. 再实现 shared evidence/audit；
10. 最后加入 Agent orchestration 与 benchmark。

## 19.1 First vertical slice

~~~text
Synthetic continuous-IV data
  -> confirmed Y/X/Z and baseline_covariates = []
  -> explicitly selected distribution backend
     (fallback for local development; TabPFN for locked evaluation)
  -> control-rank stage 1
  -> diagnostic bundle
  -> support assessment
  -> interventional distribution
  -> one quantile contrast
  -> evidence record
  -> Markdown report
~~~

第二个 vertical slice：

~~~text
Hillstrom data
  -> provenance and schema validation
  -> immutable split
  -> uniform policies
  -> held-out DR/IPW values
  -> paired contrast
  -> evidence record
  -> Markdown report
~~~

## 19.2 Copy-ready kickoff prompt

~~~text
You are implementing the integrated TabCF Agent research plan.

Read:
1. TabCF_Agent_Integrated_Research_Plan_ZH.md;
2. TabCF_Analyst_Product_Agent_Plan_EN.md;
3. Hillstrom_Email_Experiment_Evaluation_Research_Plan_EN.md;
4. the supplied TabCF manuscript.

Then inspect the repository, dependency files, tests, and existing tabcf_core public APIs. Do not infer internal class or function names from the plans, and do not rewrite the TabCF statistical core unless a verified defect blocks the application layer.

Critical boundary:
- The public product v1 is a continuous-treatment, scalar-IV distributional analyst with no baseline covariates W.
- If baseline covariates are supplied, fail closed before Stage 1; never drop or silently ignore W.
- On macOS, an explicitly selected `sklearn_quantile_fallback` may be used for development-only pipeline tests.
- Never auto-fallback after a TabPFN load failure, never call fallback output TabCF, and never use it for locked Track T claims.
- Hillstrom is a randomized three-action companion evaluation environment.
- Hillstrom does not validate the current TabCF estimator.
- Do not implement a general causal-method router.

Your first deliverable is CODEBASE_MAP.md. It must identify:
- current stage-1, stage-2, CDF, mean, quantile, plotting, caching, and serialization APIs;
- reusable agent, state, evidence, and reporting components;
- missing adapters and typed schemas;
- the exact isolation boundary between TabCF and Hillstrom;
- dependencies, deployment risks, and the smallest vertical slices.

Implementation order:
1. shared schemas, typed errors, evidence, and audit;
2. deterministic TabCF vertical slice;
3. TabCF diagnostics and support gates;
4. deterministic Hillstrom policy-value vertical slice;
5. explicit agent state machine;
6. fixed-workflow and full-agent benchmark;
7. semi-synthetic evaluation;
8. UI, report, and portfolio artifacts.

Requirements:
- Use English comments in code.
- Keep every numerical causal calculation inside deterministic tools.
- Require evidence IDs for all numerical claims.
- Block unsupported treatments and outside-support interventions.
- Block non-empty TabCF baseline covariates with `UNSUPPORTED_BASELINE_COVARIATES` before fitting.
- Bind every result to an explicit estimator backend and execution profile.
- Reject development-fallback evidence from final Track T reports.
- Never state that empirical diagnostics prove IV validity.
- Never access Hillstrom test outcomes before policy freeze.
- Never treat randomized assignment as an optimal-action label.
- Use identical statistical tools for fixed-workflow and full-agent comparisons.
- Preserve warnings and assumptions in every result and report.
- Add unit, leakage, statistical, integration, and agent-behavior tests.
- Report blockers instead of guessing APIs or silently changing the protocol.
~~~

---

# 20. Final definition of success

本项目成功不要求：

- TabCF 在每个 DGP 上都排名第一；
- Agent 在每个任务上都优于固定流程；
- Hillstrom personalized policy 显著增加 spend。

本项目成功要求：

1. 三种证据不混淆；
2. TabCF 统计边界正确；
3. TabCF v1 的所有拟合均使用 \(W=\varnothing\)，且任何非空 \(W\) 请求都在拟合前停止；
4. fallback 只用于显式标记的本地工程验证，且不会静默替代 TabPFN；
5. 任何 TabCF/Track T 最终统计主张均来自真实、可复现的 TabPFN 后端；
6. Hillstrom 使用 honest policy evaluation；
7. Agent 增量比较公平；
8. 所有数字可追溯；
9. unsupported 和 unsafe cases 正确停止；
10. negative results 被完整保留；
11. 一个研究者或招聘者可以复现核心结果。

最终一句话：

> **TabCF Analyst is a narrow, auditable distributional-IV agent, evaluated within a broader research framework that separately measures estimator accuracy, real-policy value, and the incremental reliability of agentic orchestration.**

---

# References

- Geping Chen, Chunlin Li, Tianzhong Yang, Zhengyuan Zhu, and Jing Zhou. *TabCF: Distributional Control Function Estimation with Tabular Foundation Models*. Project manuscript, 2026.
- Guido W. Imbens and Whitney K. Newey. *Identification and Estimation of Triangular Simultaneous Equations Models Without Additivity*.
- Kevin Hillstrom. [The MineThatData E-Mail Analytics and Data Mining Challenge](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html), 2008.
- TensorFlow Datasets. [Hillstrom dataset catalog](https://www.tensorflow.org/datasets/catalog/hillstrom).
- Miroslav Dudík, Dumitru Erhan, John Langford, and Lihong Li. [Doubly Robust Policy Evaluation and Optimization](https://projecteuclid.org/journals/statistical-science/volume-29/issue-4/Doubly-Robust-Policy-Evaluation-and-Optimization/10.1214/14-STS500), 2014.
- Susan Athey and Stefan Wager. [Policy Learning with Observational Data](https://onlinelibrary.wiley.com/doi/10.3982/ECTA15732), 2021.
- Zhengyuan Zhou, Susan Athey, and Stefan Wager. [Offline Multi-Action Policy Learning: Generalization and Optimization](https://pubsonline.informs.org/doi/10.1287/opre.2022.2271), 2023.
- Erik Sverdrup et al. [policytree: Policy Learning via Doubly Robust Empirical Welfare Maximization over Trees](https://joss.theoj.org/papers/10.21105/joss.02232), 2020.
