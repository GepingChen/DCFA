---
title: "DCFA GitHub Pages + Colab 正式展示版发布计划"
language: "zh-CN"
version: "2.0"
status: "Static replay and public Colab CTA released; fresh credentialed Colab run not repeated"
approved_on: "2026-08-19"
supersedes: "Hugging_Face_Space_Public_Demo_Release_Plan_ZH.md at commit cea25b0"
ui_dependencies: "Phase 0 b4d3e7d and Phase 1 76ca4bc are complete"
affected_repositories:
  - "/Users/chgp/Dropbox/tabcf_agents"
  - "/Users/chgp/Dropbox/nova/website"
affected_surface: "Static portfolio replay on GitHub Pages and user-owned Colab execution"
affected_evidence_tracks: "None; no new Track T, H, or A evidence"
implementation_updated_on: "2026-08-20"
---

# DCFA GitHub Pages + Colab 正式展示版发布计划

## 0. 已批准的发布决策

本计划以 GitHub Pages + Google Colab 取代先前批准但尚未实施的 Hugging Face Space 方案。
不再要求 Hugging Face 注册、PRO 订阅、Docker Space、Space secrets 或
`Duplicate this Space`。

第一版正式 website tool 使用以下双入口：

```text
https://gepingchen.github.io/projects/dcfa/
├── Replay the verified example
│   └── frozen prompt + prepared synthetic CSV + verified stored result
│       static Astro/HTML/JS; zero API calls; zero credentials; zero inference cost
│
└── Analyze your own data
    └── Open in Google Colab
        ├── user-owned ephemeral notebook runtime
        ├── user-owned Gemini secret
        ├── user-owned Prior Labs TabPFN token
        ├── user-uploaded bounded CSV and prompt
        └── the existing typed DCFA runtime produces user-downloadable artifacts
```

公共主页只托管一个预计算且经过独立验证的 replay，不运行 Python、Gradio、Gemini 或
TabPFN。自定义分析在访问者自己的 Colab runtime 中完成；项目所有者的服务器、API keys、
quota 和文件系统均不参与。

本决策区分三种状态：

- GitHub Pages 页面可以是正式发布且稳定可访问的 portfolio website tool；
- prepared replay 是一个真实运行的冻结展示，不是点击时发生的 live analysis；
- prepared 和 Colab live 结果继续保持真实的
  `local_development / tabpfn / development_only` 身份，不升级为 locked Track T、
  Track A agent 优势或真实世界因果证据。

## 1. 已满足基线和开始条件

UI/UX 优化的前两阶段已经完成并推送：

- Phase 0 visitor/audit presentation boundary：`b4d3e7d`；
- Phase 1 result-first workflow and four visitor stages：`76ca4bc`。

实现本计划前仍需确认：

1. 两个提交的测试和浏览器验收记录仍与当前 `main` 一致；
2. 工作区不存在与 prepared-demo export、Colab adapter 或个人站 DCFA route 重叠的
   未提交改动；
3. 在 `docs/DECISIONS.md` 追加新的 architecture decision，明确本计划 supersede
   Hugging Face deployment direction，但不修改旧 decision 历史；
4. prepared prompt、synthetic CSV 和公开英文文案由用户最终确认；
5. 新的正式 prepared artifact 必须在发布代码冻结后生成，不复用 source identity 已过期的
   local artifact。

P2 不阻止开始 artifact 和 Colab 实施，但正式公开页面前仍必须完成与发布直接相关的移动端、
键盘、reduced-motion、标题层级、状态提示、图表替代文本和 CSV 流程检查。

## 2. 仓库职责和准确路径

### 2.1 DCFA source repository

Repository：`/Users/chgp/Dropbox/tabcf_agents`

负责：

- prepared input 和完整验证 bundle 的权威生成；
- public showcase projection 和 manifest；
- Colab notebook 与 notebook-specific credential/input adapter；
- agent、data、support、evidence 和 provider boundaries；
- artifact/Colab tests 和 release provenance。

计划新增或修改的准确路径：

| Path | Planned role |
|---|---|
| `/Users/chgp/Dropbox/tabcf_agents/docs/DECISIONS.md` | Append the GitHub Pages + Colab architecture decision |
| `/Users/chgp/Dropbox/tabcf_agents/docs/CODEBASE_MAP.md` | Record showcase export and Colab entry point after they exist |
| `/Users/chgp/Dropbox/tabcf_agents/docs/WEBSITE_DEMO.md` | Separate local live demo, static public replay and Colab user-run instructions |
| `/Users/chgp/Dropbox/tabcf_agents/showcase/prepared_demo_v1/` | Proposed committed public-safe source-of-truth showcase bundle |
| `/Users/chgp/Dropbox/tabcf_agents/notebooks/DCFA_Custom_Analysis_Colab.ipynb` | Proposed notebook-native custom workflow |
| `/Users/chgp/Dropbox/tabcf_agents/src/dcfa_colab/` | Proposed minimal Colab adapter only if direct reuse cannot preserve secret/input boundaries |
| `/Users/chgp/Dropbox/tabcf_agents/tests/integration/test_colab_workflow.py` | Proposed notebook adapter and fake-provider integration checks |
| `/Users/chgp/Dropbox/tabcf_agents/tests/integration/test_prepared_showcase.py` | Proposed zero-network, parity and tamper tests |

`showcase/`、`notebooks/` 和 `src/dcfa_colab/` 当前均不存在；上表是经本计划批准的目标路径，
实现时必须以最小可行文件集为准。若现有模块可以安全复用，不得为了匹配表格而创建空 package
或兼容层。

### 2.2 Personal website repository

Repository：`/Users/chgp/Dropbox/nova/website`

Production origin：`https://gepingchen.github.io`

正式 DCFA route：

> `https://gepingchen.github.io/projects/dcfa/`

个人网站必须与 DCFA release 在同一实施阶段同步修改、验证、commit 和 push。计划涉及的准确
路径如下：

| Path | Planned change |
|---|---|
| `/Users/chgp/Dropbox/nova/website/src/pages/projects/dcfa.astro` | New static project detail and prepared replay page; builds `/projects/dcfa/` |
| `/Users/chgp/Dropbox/nova/website/src/components/DcfaPreparedDemo.astro` | New visitor-safe static replay component with minimal progressive enhancement |
| `/Users/chgp/Dropbox/nova/website/src/data/dcfa/prepared-demo-v1.json` | Build-time visitor projection and public manifest fields |
| `/Users/chgp/Dropbox/nova/website/public/dcfa/prepared-demo-v1/prepared-demo.csv` | Downloadable approved synthetic CSV |
| `/Users/chgp/Dropbox/nova/website/public/dcfa/prepared-demo-v1/prepared-prompt.txt` | Downloadable exact prepared prompt |
| `/Users/chgp/Dropbox/nova/website/public/dcfa/prepared-demo-v1/visitor-plot.png` | Public visitor plot derived from the validated bundle |
| `/Users/chgp/Dropbox/nova/website/public/dcfa/prepared-demo-v1/verification-summary.json` | Public-safe verification summary and hashes |
| `/Users/chgp/Dropbox/nova/website/src/content/projects/dcfa.md` | New project card with contribution, status and evidence links |
| `/Users/chgp/Dropbox/nova/website/src/pages/projects.astro` | Replace the hard-coded “Three evidence-backed projects” count and expose the DCFA card |
| `/Users/chgp/Dropbox/nova/website/src/components/DcfaDemoEmbed.astro` | Remove or retire the now-unneeded iframe component after confirming it remains unreferenced |
| `/Users/chgp/Dropbox/nova/website/scripts/verify-dist.mjs` | Require the new route/assets and validate public copy, internal links, forbidden content and Colab URL |
| `/Users/chgp/Dropbox/nova/website/src/styles/global.css` | Change only if shared tokens are insufficient; prefer scoped component styles |

No change is expected in:

- `/Users/chgp/Dropbox/nova/website/astro.config.mjs`；
- `/Users/chgp/Dropbox/nova/website/.github/workflows/deploy.yml`；
- `/Users/chgp/Dropbox/nova/website/package.json`。

They must still be inspected and verified. Do not add React, a runtime API, analytics or a new frontend framework
only for this page.

### 2.3 Colab entry URL

The stable source path is:

> `/Users/chgp/Dropbox/tabcf_agents/notebooks/DCFA_Custom_Analysis_Colab.ipynb`

The public convenience URL is expected to be:

> `https://colab.research.google.com/github/GepingChen/DCFA/blob/main/notebooks/DCFA_Custom_Analysis_Colab.ipynb`

The notebook file may live at the stable `main` URL, but its setup cell must pin the exact approved DCFA release
commit/profile. The website must display a short release identity so a later `main` change cannot silently alter the
runtime represented by a prepared artifact.

## 3. Public prepared demo contract

### 3.1 Public interaction

The GitHub Pages route allows a visitor to:

- inspect the exact prepared natural-language question；
- inspect Y/X/Z roles, row count and a safe CSV preview；
- download the approved synthetic CSV and prompt；
- click `Replay the verified example`；
- see four previously executed workflow stages；
- read one direction-aware visitor-safe answer；
- see support status, mapped warnings, development-only boundary and visitor plot；
- inspect a short verification summary and release hash；
- open the Colab workflow or the DCFA GitHub repository。

It must not：

- call Gemini、Prior Labs or any inference endpoint；
- import or execute the Python DCFA runtime in the browser；
- request, read or store API keys；
- accept a public arbitrary CSV or prompt for execution；
- recompute the headline number from the plot, CSV or browser code；
- animate the stored stages as if live provider requests are occurring；
- expose internal enum、warning code、trace、bundle/specification/evidence ID、SDK field or raw provider error。

Required adjacent disclosure：

> This replays a previously executed and independently verified workflow. No API call is made.

### 3.2 Static implementation boundary

The prepared page is generated by Astro and served by GitHub Pages. Small progressive enhancement may control
replay/reveal state, but：

- the complete answer and limitations remain available without JavaScript；
- the enhancement does not derive or change numerical values；
- keyboard and screen-reader users receive equivalent content；
- `prefers-reduced-motion` disables staged motion；
- no external JavaScript, CDN analytics or client-side LLM SDK is introduced；
- Content Security Policy and GitHub Pages constraints are reviewed before release。

## 4. Prepared artifact contract

### 4.1 Freeze before run

Prepared demo input must be an approved, redistributable synthetic CSV. Freeze before the one authorized live run：

- `prepared_demo_id` and schema version；
- exact prompt bytes and SHA-256；
- exact CSV bytes and SHA-256；
- Y/X/Z role mapping；
- row count, seed and intervention-label contract；
- Gemini website profile ID/hash；
- managed TabPFN profile ID/hash；
- DCFA source/commit identity；
- public projection schema；
- required success and warning-preservation behavior。

Do not inspect a result and then tune the prompt, CSV or seed to obtain a more favorable number. Any material change
creates `prepared_demo_v2`; v1 remains immutable.

### 4.2 Source-of-truth bundle

Proposed DCFA public-safe source bundle：

```text
/Users/chgp/Dropbox/tabcf_agents/showcase/prepared_demo_v1/
├── prepared_demo_manifest.json
├── prepared_demo.csv
├── prepared_prompt.txt
├── visitor_result.json
├── visitor_plot.png
└── verification_summary.json
```

The ignored full live run remains in a new immutable `artifacts/local/...` directory and must independently verify.
Only the explicitly approved small public-safe projection is committed under `showcase/`.

The personal website receives byte-for-byte approved static assets plus build-time visitor data. Its
`prepared-demo-v1.json` must bind the DCFA release commit and hashes of every copied public asset. A website build
fails when copied assets no longer match the declared manifest.

### 4.3 Zero-network proof

Prepared replay is a stored projection, not a cache hit. Automated acceptance must prove：

- provider SDKs are absent from the website dependency/runtime path；
- Gemini/TabPFN clients and credential loaders are never constructed；
- network denied/fail-on-call conditions do not affect replay；
- replay creates no analysis artifact and no browser storage entry；
- visitor value equals the verified raw value before tested display rounding；
- warning/support/plot projection matches the frozen bundle；
- unknown or tampered manifest content suppresses the numerical result at build or release validation。

## 5. Colab custom-analysis contract

### 5.1 Notebook-native workflow

Colab is an interactive notebook, not a free public application server. Do not launch a public Gradio share link,
remote desktop, SSH tunnel or a web UI intended to bypass the notebook interface.

The notebook should expose a short sequence：

1. scope, privacy and cost disclosure；
2. pinned DCFA installation and source-identity check；
3. Gemini and TabPFN secret readiness；
4. CSV upload and local preflight；
5. explicit Y/X/Z role mapping；
6. bounded natural-language prompt；
7. separate confirmation of the Google and Prior Labs transfers；
8. one Gemini compilation and bounded managed TabPFN execution；
9. visitor-safe result plus artifact verification；
10. downloadable artifact archive and explicit runtime cleanup instructions。

No cell should imply that Colab resources, provider availability or free usage are guaranteed.

### 5.2 Secret boundary

Use user-owned Colab Secrets with final implementation names documented in the notebook. Proposed names：

- `DCFA_GEMINI_API_KEY`；
- `DCFA_TABPFN_TOKEN`。

Requirements：

- retrieve secrets only after the user runs the readiness cell；
- never print secret value、length、prefix or exception context containing it；
- never commit or save secrets into the notebook；
- never write secrets into result artifacts、Google Drive or the uploaded CSV directory；
- use request-scoped client objects where possible；
- if a mode-600 temporary credential file is unavoidable, create it under the ephemeral runtime, delete it in
  `finally`, scan artifacts and document the limitation；
- reset any process-global TabPFN client token after success or failure；
- missing secrets fail before provider construction or output allocation。

The user must use their own Gemini and Prior Labs accounts, accept provider terms and remain responsible for quota
and charges.

### 5.3 Data and execution boundary

The Colab path preserves the existing website-demo scope：

- exactly one continuous outcome Y、one continuous treatment X、one scalar IV Z；
- no baseline covariates W；
- 120–256 rows and exactly three selected numeric columns；
- finite values and current distinct-value presentation gates；
- question text, generic roles and symbolic labels only to Gemini；
- authorized Y/X/Z rows and prediction grids to Prior Labs；
- exactly one Gemini request per run；
- no retry、no LLM bypass、no sklearn fallback；
- outside-support/provider/evidence failure displays no number；
- every successful run uses a new immutable runtime directory and is independently verified。

The notebook does not add a general causal router, Hillstrom path, W support or local silent backend.

## 6. Personal website information architecture

### 6.1 Route and project card

`/Users/chgp/Dropbox/nova/website/src/content/projects/dcfa.md` adds DCFA as a distinct engineering project, not a
replacement for the existing TabCF research entry. It should state the owner's individual contribution and link to：

- `/projects/dcfa/`；
- `https://github.com/GepingChen/DCFA`；
- the verified Colab notebook；
- an optional public-safe verification summary。

`/Users/chgp/Dropbox/nova/website/src/pages/projects.astro` currently hard-codes “Three evidence-backed projects.”
Implementation must remove that stale count or derive it safely from the collection before the fourth public project
is added.

### 6.2 DCFA detail page

`/Users/chgp/Dropbox/nova/website/src/pages/projects/dcfa.astro` builds the canonical public route and contains：

1. project title and one-sentence value proposition；
2. author contribution and narrow supported scope；
3. `DcfaPreparedDemo` replay component；
4. architecture: prompt → typed specification → deterministic tool → evidence or stop；
5. development-only and identification limitations；
6. `Open in Colab` and GitHub links；
7. provider data-transfer explanation for the Colab path；
8. no iframe and no live Python service。

### 6.3 Replace the old iframe component

`/Users/chgp/Dropbox/nova/website/src/components/DcfaDemoEmbed.astro` currently accepts an HTTP(S) runtime URL and
renders a sandboxed iframe. It is unreferenced and no longer matches the approved static architecture.

Implementation should：

1. confirm again that it has no imports；
2. add `/Users/chgp/Dropbox/nova/website/src/components/DcfaPreparedDemo.astro`；
3. delete `DcfaDemoEmbed.astro` in the same verified website change rather than retain a misleading dead path；
4. ensure no temporary/local/runtime URL appears in built HTML。

## 7. Implementation phases

### GC0：Freeze the cross-repository decision and schemas

Deliver：

- append the GitHub Pages + Colab decision to DCFA `docs/DECISIONS.md`；
- define public showcase and Colab result contracts；
- freeze prepared prompt、CSV、profile and release naming；
- record both repository clean states and current commits；
- confirm the personal-site route and public English copy。

Acceptance：no live API call; schema、claims、privacy and path review complete。

### GC1：Generate and verify the prepared showcase

Deliver：

- one newly authorized live run in a fresh ignored directory；
- independent full artifact verification；
- deterministic export to `showcase/prepared_demo_v1/`；
- public-safe secret/path/metadata scan；
- tamper and zero-network tests。

Acceptance：full bundle valid; public values/warnings/support equal the validated source; no credential or private
path is present。

### GC2：Implement the Colab workflow

Deliver：

- `notebooks/DCFA_Custom_Analysis_Colab.ipynb`；
- minimal reusable adapter only if required；
- pinned setup、secret readiness、CSV preflight、consent、execution、verification and download cells；
- fake-client tests plus notebook static validation；
- one manual Colab clean-runtime acceptance using synthetic data and user-owned credentials, separately authorized。

Acceptance：clean Google account runtime can follow the notebook; secrets do not enter output; all failure paths are
no-number and no-fallback。

### GC3：Implement the personal-site route in the same delivery

Deliver in `/Users/chgp/Dropbox/nova/website`：

- new `src/pages/projects/dcfa.astro`；
- new `src/components/DcfaPreparedDemo.astro`；
- new project content entry；
- copied hash-bound public assets；
- retired `DcfaDemoEmbed.astro`；
- updated projects heading and `scripts/verify-dist.mjs`；
- no new runtime dependency。

Acceptance：`npm run verify` passes; built output includes `dist/projects/dcfa/index.html`; replay works with network
blocked and JavaScript disabled; Colab/GitHub/download links resolve。

### GC4：Browser and cross-repository release QA

At minimum cover：

- 1280 px and 390 px；
- keyboard-only and visible focus；
- screen-reader headings/status and plot alternative；
- reduced motion；
- prepared replay/no-JS fallback；
- asset hash and forbidden-content scans；
- no outbound provider request from GitHub Pages；
- clean Colab setup, missing-secret and fake-provider failure；
- exact DCFA commit bound in website data；
- production GitHub Pages URL after deployment。

### GC5：Commit, push and publication verification

Use separate repository commits：

1. DCFA source/showcase/notebook/docs/tests commit and non-force push to its configured upstream；
2. personal website route/content/assets/verifier commit and non-force push to its configured upstream；
3. verify both remote refs equal their local release commits；
4. wait for GitHub Pages deployment and verify
   `https://gepingchen.github.io/projects/dcfa/`；
5. do not publish resume copy until the user confirms the exact wording and public links。

Do not combine the two repositories' claims or report the personal-site deployment complete before the live URL is
checked。

## 8. Verification matrix

| Boundary | Required evidence |
|---|---|
| Prepared page has zero API usage | browser/network inspection plus fail-on-call provider test |
| Stored result is authentic | current artifact verifier plus prompt/CSV/result/source hashes |
| Website copy matches source | cross-repository public asset hash check |
| Visitor projection is faithful | raw-value parity before tested rounding; warning/support parity |
| No secret reaches GitHub | repository, dist, notebook-output and artifact scans |
| Colab missing secret fails closed | no provider construction, no run directory, safe remediation text |
| Colab Gemini boundary | exactly one request; no rows or actual intervention values |
| Colab TabPFN boundary | only confirmed Y/X/Z rows; bounded prediction calls; reset after run |
| Unsupported requests stay blocked | no value, visitor plot or evidence on invalid/outside-support requests |
| Static page remains useful without JS | full answer, limitations and links remain readable |
| Personal-site route is current | built and production revision markers match approved commits |
| Public links are stable | GitHub repo, Colab main path and downloadable prepared assets resolve |

## 9. Release gate

Formal publication requires all of the following：

1. GC0–GC4 accepted；
2. prepared artifact is generated under the approved current release identity；
3. public GitHub Pages route makes zero Gemini/TabPFN calls；
4. no secret、private path、raw service context or machine audit identifier appears in the website repository/dist；
5. prepared replay is explicitly labeled precomputed；
6. Colab notebook pins the approved DCFA commit/profile and uses user-owned secrets；
7. Colab has no public Gradio tunnel or long-running service workaround；
8. visitor values/warnings/support/plot match the validated bundle；
9. `/projects/` and `/projects/dcfa/` pass desktop/mobile/keyboard/reduced-motion QA；
10. `npm run verify` and DCFA relevant/full gates pass；
11. both repository commits are pushed and remote refs verified；
12. `https://gepingchen.github.io/projects/dcfa/` returns the reviewed current build；
13. public claims distinguish website release, prepared demonstration and scientific evidence。

Any hard-gate failure blocks publication; do not compensate with screenshots, prior local smoke or a successful
notebook run。

## 10. Public claims

Approved core description：

> DCFA is an auditable causal-analysis agent that compiles bounded natural-language requests
> into typed specifications, delegates numerical work to deterministic tools, blocks unsupported
> claims, and links displayed results to verifiable evidence.

Prepared demo may be described as：

- a precomputed replay of a verified end-to-end workflow；
- a static portfolio demonstration of agent architecture, safety gates and evidence handling；
- a synthetic, development-only example that makes no API call when replayed。

Colab may be described as：

- a user-run notebook for the bounded custom CSV workflow；
- a workflow that uses the user's own Gemini and Prior Labs accounts；
- a notebook-native route that produces independently verifiable artifacts。

Do not describe either route as：

- production causal advice；
- proof of IV validity；
- locked or publishable Track T evidence；
- evidence that the agent outperforms a fixed workflow；
- a general causal-analysis system；
- a free or guaranteed Colab runtime；
- a live analysis when showing the prepared replay。

## 11. Implementation handoff

Final handoff must report：

- P0/P1 baseline commits；
- prepared prompt、CSV、profiles、artifact、verification and release identities；
- zero-network test commands/results；
- Colab notebook path, public URL, pinned commit and clean-runtime QA；
- secret and uploaded-data scans；
- all changed files in both repositories；
- `npm run verify` and DCFA test results；
- desktop/mobile/keyboard/reduced-motion checks；
- production URL and deployment status；
- unverified provider、quota、Colab availability or cross-platform boundaries；
- both commit hashes、push destinations、remote-ref verification and final Git states。

## 12. Official documentation to recheck at implementation

These platform behaviors may change. Recheck on implementation and release day：

- Google Colab FAQ and free-runtime restrictions：
  `https://research.google.com/colaboratory/faq.html`
- Google Colab repository notebook URL behavior：
  `https://colab.research.google.com/`
- Gemini API key/security requirements：
  `https://ai.google.dev/gemini-api/docs/api-key`
- Prior Labs `tabpfn-client` authentication and cloud-data boundary：
  `https://github.com/PriorLabs/tabpfn-client`
- GitHub Pages and Actions behavior for the personal-site repository：
  `https://docs.github.com/pages`

If official behavior conflicts with this plan, append a new architecture decision and version this plan before
implementation. Do not introduce an undocumented fallback or a free-runtime policy workaround。

## 13. 2026-08-19 实施记录

- GC0：完成。追加 D-032，冻结 `prepared_demo_v1`、公开 projection schema、两个 provider
  profile、DCFA source hash 与 release commit。
- GC1：完成。唯一一次 live run 使用 1 次 Gemini compile 与 3 次 managed TabPFN
  predictions；完整 artifact 和公开 projection 均独立验证为 valid。公开 release hash 为
  `sha256:4b686a1ee94b52ef573e84c3d0f71233bba11802604a4787bbbcd2c7d35c50af`。
- GC2：代码、fake-provider integration、notebook static validation、secret/consent/archive gates
  完成；真实 clean Colab runtime 尚未人工执行。
- GC3：完成。个人站 `/projects/dcfa/`、prepared replay、hash-bound assets、项目卡和 release
  validator 已实现；旧 iframe component 已删除。
- GC4：静态页面的 1280 px/390 px、focus、heading/landmark、plot alt、reduced-motion、无
  overflow、零 iframe/零脚本/零 console error 与 production asset hash 已验证。Clean Colab
  runtime 未验证。
- GC5：两个仓库均已普通 commit/push 并核对 remote ref；GitHub Pages Actions 成功部署静态
  replay。2026-08-20，用户将 `GepingChen/DCFA` 设为 public；匿名访问 repository、GitHub
  notebook、raw notebook 与精确 Colab URL 均成功，Projects 卡片与详情页的 `Open in Colab`
  CTA 已恢复。

本次 CTA 恢复只验证公开 source/link 与既有 notebook 静态契约，没有在 Colab 中重新传输用户
密钥、问题或 Y/X/Z 数据，也没有新增 Gemini/managed TabPFN 请求。若需要把“fresh clean Colab
runtime with live providers”作为独立验收结论，仍需单独授权该有成本的外部执行。
