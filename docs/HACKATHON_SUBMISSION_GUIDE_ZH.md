# TabPFN-3.5 Hackathon 提交教程

2026-10-06 更新：用户授权的前三步已完成，源码已推送至
[公开参赛仓库](https://github.com/GepingChen/agentic-tabcf-hackathon)，提交 `e2710cf`，
GitHub 识别许可证为 Apache-2.0。见 [发布记录](HACKATHON_PUBLICATION_20261006.md)。
官网操作和正式提交由用户完成。下文保留此前的完整准备教程。

核对日期：2026-10-06。这是提交准备教程，不是已提交凭证。

## 先看截止时间和真正要交的东西

官方截止是 **2026 年 10 月 6 日 23:59 CEST**，对应：

| 时区 | 截止时间 |
|---|---|
| America/Chicago（你当前所在时区，CDT） | **10 月 6 日 16:59** |
| UTC | 10 月 6 日 21:59 |
| 北京时间（UTC+8） | 10 月 7 日 05:59 |

以 Prior Labs 系统收到的时间为准。截止前可以更新，最后一次提交算数；
过期不接受。不要等到最后一分钟。

提交入口：[官方 Hackathon 页面](https://platform.priorlabs.ai/hackathon-3.5)。
进入页面后打开 **View the Terms & Conditions**。本次重新阅读了完整条款。
第 3 节要求公开 Apache-2.0 源码仓库、项目说明、可运行的代码/说明以及
输入数据或公开数据 URL，且 TabPFN-3.5 必须是核心组件。视频是可选材料。
**本地 ZIP、API 使用记录或一个 Hugging Face Space 都不等于正式报名。**
评分见第 4 节：TabPFN-3.5 展示 50%，创意/原创性/实用价值 30%，技术质量和
可复现性 20%。已有 TabCF 方法与本次新增工作应明确区分。

## 当前我替你准备的东西

| 材料 | 状态 / 路径 |
|---|---|
| 当前完整本地候选包 | `artifacts/local/agentic-tabcf-submission-v6.zip`；保留原有运行时、原始证据和比较结果 |
| 专用源码仓库待发布目录 | `artifacts/local/agentic-tabcf-public-repo-v6/`；根 Apache-2.0、可读入口源码和 MIT 父项目源码、原安装 wheel/lock、公开例子和真实例子证据 |
| 英文表单文案 | `submission/FORM_TEXT.md`；标题、短说明、完整说明可直接复制 |
| 评委可直接看的报告 | `submission/reports/cigarette-tabpfn35.html`；离线英文 HTML，真实 3.5 运行的回放 |
| 录屏脚本 | `submission/DEMO_SCRIPT.md`；约 2–3 分钟；视频本身尚未录制 |
| 本地复现 prompt | `submission/CIGARETTE_PROMPTS.md`；修正了 Space 登录/密码框与本地密钥文件的区别 |

这些准备不重新调用模型，也不改变估计器或研究协议。历史安装、真实运行和
浏览器验收属于已有证据；此次检验针对重新打包和源码导出，不能当作新的统计验证。
v3/v4/v5 保留原样。

## 第 1 步：确认参赛资格和许可证

1. 用你自己的有效 Prior Labs 账户参赛；条款要求已满 18 岁或所在国法定成年年龄。
2. 确認你拥有发布所选代码、数据和材料的必要权利。不要填未经确认的声明。
3. 此次实际查询 GitHub，现有 `GepingChen/DCFA` 已是公开仓库，但根许可证为 MIT。
   不要直接把其根链接描述为一个 Apache-2.0 项目。
4. 待发布目录的根 `LICENSE` 已是 Apache-2.0，覆盖参赛入口和新材料；
   `vendor/dcfa/LICENSE`、`PARENT_MIT_LICENSE`、`TABCF_MIT_LICENSE` 保留 MIT，
   cigarette 数据仍有独立来源和 GPL-2.0 声明，模型/服务有另外的条款。
   阅读 `NOTICE`，不要把整个目录说成所有内容都统一 Apache-2.0。
5. 官网要求 Apache-2.0 项目，未说明此种混合依赖的具体解释。已备好 Apache
   入口和分开的声明，但主办方是否接受这一形式尚未确认。如果不能确认，
   保持这项不确定性可见；不要擅自把第三方代码、数据或模型重新标为 Apache。

独立参赛仓库的作用是给评委一个清楚的入口，保留父项目现有许可证和历史。
源码目录在本地准备好，**尚未创建新的远程仓库或发布它**。

## 第 2 步：先检查作品，无需装环境

1. 解压 v6 ZIP，或者打开待发布目录。
2. 用浏览器 **File → Open File** 打开 `reports/cigarette-tabpfn35.html`。
   GitHub 文件页面显示 HTML 源码，需要下载后打开。
3. 看标题、价格 100→120、CDF/近似 PDF、25/50/75 分位数、明确请求的超阈值概率、
   警告和可展开证据。它是保存的真实 3.5 结果，不能声称正在直播计算。
4. 阅读根 `README.md`、`PROJECT.md` 和 `NOTICE`。待发布目录中的 README 对应
   该目录的实际结构，不要用旧 v3 的说明替换它。

如果只为赶截止，优先把源码链接和项目说明提交完整；视频可之后在截止前补上。
这不免除可复现与权利要求。

## 第 3 步：发布独立 GitHub 源码仓库

这是你接下来执行的外部发布动作。本次仅准备目录和命令，没有替你发布。
推荐名字 `agentic-tabcf-hackathon`，只是建议，尚不存在的 URL 不可填入表单。

1. 登录 GitHub，点 **New repository**。
2. Owner 选择你有权使用的账户；名称用上面的名字或自己的名字。
3. 选择 **Public**。不要勾选自动生成 README、.gitignore 或许可证，目录里已经有。
4. 点击 **Create repository**，复制页面实际显示的 SSH repository URL。
5. 终端运行下面的命令。只在待发布目录操作，不要在父项目根目录执行 `git init`。
   `git add` 使用明确路径，避免把后续本地环境、密钥或日志加入。

```bash
cd /Users/chgp/Dropbox/tabcf_agents/artifacts/local/agentic-tabcf-public-repo-v6
git init -b main
git add .gitignore README.md PROJECT.md DEMO_SCRIPT.md FORM_TEXT.md LICENSE NOTICE PARENT_MIT_LICENSE TABCF_MIT_LICENSE SOURCE_LAYOUT.md parent_commit.txt tabcf_commit.txt pyproject.toml requirements.lock src vendor wheels examples reports results
git diff --cached --stat
git status --short
git commit -m "Prepare Agentic TabCF hackathon entry"
```

审阅暂存内容后再 commit。然后把以下 URL 换为刚创建仓库的实际 SSH URL：

```bash
git remote add origin git@github.com:YOUR_ACCOUNT/YOUR_REPOSITORY.git
git push -u origin main
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

最后两个命令的提交 SHA 应一致。使用当前已有的 GitHub SSH 认证；若认证失败，
解决账户/SSH 登录问题，不能通过 force push 或写入 token 到仓库绕过。

6. 退出登录或用无痕窗口打开仓库根 URL，确认别人能看见 README、Apache
   入口源码 `src/`、MIT 父项目源码 `vendor/dcfa/`、依赖文件、例子和报告。
7. 正式表单填这个**仓库根 URL**，不要填本地路径、虚构 URL 或仅一个 ZIP 下载链接。

## 第 4 步：按需检验现场运行

保存报告不需要密钥。若希望自己重新跑一遍，在待发布目录或解压包根目录执行：

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
mkdir -p ~/.config/dcfa
```

用你自己的编辑器把现有 Gemini 和 Prior Labs API keys 分别放入：

- `~/.config/dcfa/gemini_api_key`
- `~/.config/dcfa/tabpfn_api_key`

不要把密钥粘贴到聊天、GitHub、视频、例子或日志。然后运行：

```bash
chmod 600 ~/.config/dcfa/gemini_api_key ~/.config/dcfa/tabpfn_api_key
.venv/bin/agentic-tabcf
```

1. 打开 `http://127.0.0.1:7860`。
2. 上传 `examples/cigarette/cigarette_144.csv`，Advanced seed 设为 `20260920`。
3. 阅读数据传输说明并授权：Gemini 接收对话和列名；Prior Labs 接收所选 Y/X/Z 行。
4. 复制 `examples/cigarette/PROMPTS.md` 的完整 prompt。
5. 检查列角色、无 W、已有自然对数、100/120 原单位价格、分位数、阈值和方向。
6. 点一次 **Confirm and generate report**。聊天里输入 Confirm 不会执行。
7. 完成后下载报告，普通追问复用缓存；改问题/数据则重置。

本次不额外消耗你账户额度。已有真实安装和分析证据在旧包中；新的运行需要
自己的密钥及可用额度。3.5 失败就停止，不能用 v2 或 sklearn 的结果冒充 3.5。

## 第 5 步：可选录制 2–3 分钟视频

按 `DEMO_SCRIPT.md` 录制即可：问题 → 角色/单位审阅 → 标注为 saved replay 的
3.5 报告 → 曲线/分位数/证据 → 方法边界 → 复现入口。
录制前打开离线报告，可使用包里已有公开确认/结果截图；不要把截图当成直播。
长等待可以快进，但要标注。不要重新花额度只为录像。

若上传 YouTube，可选择 Unlisted；若用其他平台，保证无需你个人登录即可观看。
用无痕窗口检查实际视频 URL。官方可选字段不限于某个平台，未录好可留空。
不要填写不存在的视频链接。

## 第 6 步：登录官网并接受参赛条款

1. 打开 [官方入口](https://platform.priorlabs.ai/hackathon-3.5)。
2. 点 **Sign in to join**。
3. 本次看到了登录页：Email/Password、**Continue with GitHub**、
   **Continue with Google** 和 **Sign up**。使用自己的已有账户；必要时自行注册。
4. 登录后返回 hackathon 页面，阅读并由你本人接受参赛条款。
   其中含作品分享、权利声明和可选社交资料的公开署名约定。
5. 找到新增作品/提交入口。本次没有登录你的账户、接受条款或看到登录后的表单，
   因此不猜具体按钮名、字段顺序或字符上限，以实际页面为准。

## 第 7 步：填写表单

打开 `FORM_TEXT.md`，复制实际页面所需内容：

| 页面若出现该字段 | 填什么 |
|---|---|
| Project title/name | `Agentic TabCF: Distributional Causal Analysis with TabPFN` |
| Public repository URL | 第 3 步实际发布并检查过的仓库根 URL |
| Project description | Full description；若有长度限制，用 Short description |
| Video URL | 已完成并检验可访问的视频 URL，或留空 |
| Additional materials/demo URL | 仅填实际可访问、版本明确的材料；可选 |
| X/LinkedIn | 仅填你愿意用于公开署名和 tag 的资料；可选 |
| 姓名、账户、年龄和权利声明 | 由你本人准确填写和判断 |

官网条款明确必需的是仓库链接和足够详细的描述；标题等其余行是文案映射，
不是声称每个字段都已在登录后的表单里核实。不要写“3.5 全面优于 v2”、
“证明工具变量有效”、“个人因果效果”、“已发布最终研究结果”等无证据主张。

## 第 8 步：完成正式提交并保存凭证

1. 确认仓库 Public、实际 URL 可访问、许可声明真实、描述与代码一致。
2. **由你在官网点击最终提交按钮**，在 16:59 CDT 之前完成。
3. 检查官网成功提示，以及账户中实际出现的作品条目/已提交状态。
   只点按钮、保留草稿或填写表单不代表系统收到。
4. 保存作品条目、时间和确认信息截图；如果官网发送邮件，也保存邮件。
   不保证官网一定会发邮件或一定有某种编号。
5. 若需更新，在截止前从官网修改该作品，重新检查保存/提交成功。
   多个项目应分别作为条目提交，不要误把重复条目当成更新。

到这里才可以说“已提交”。本次准备工作的终点是材料、教程和本地待发布源码，
不代表新的远程仓库已经创建、混合许可证已获主办方确认、条款已接受或参赛成功。
