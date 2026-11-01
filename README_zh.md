# Metaculus 机器人锦标赛(Fall 2026 FutureEval + MiniBench)零成本参赛指南

## 结论
- 报名免费、模板免费、GitHub Actions(公开仓库)免费、AskNews(注册的 bot 作者)免费。
- 唯一可能花钱的是 LLM。可选的 ¥0 方案:官方捐赠的 OpenRouter 额度(需申请,本季**择优发放,不保证**)、七牛 Conatus `qiniu/conatus-free`(据称免费到 11-30,需实名)、智谱 GLM-4-Flash、硅基流动免费模型、OpenRouter `:free` 模型。
- 中国大陆用户:不在制裁名单,可以参赛,也可以领奖。奖金经 Ramp 用 SWIFT USD 汇款,Ramp 的支持国家列表里**有 China**。获奖需做身份验证并填 W-8BEN;税费由收款人承担;中间行可能从奖金里扣手续费(不需要另外掏钱);到账要等赛季结束后几周到几个月。
- 赛季:2026-09-28 至 2027-01-06。截至 2027-01-01 前几周都可以加入。MiniBench 两周一轮,每轮奖池 $1k。

## 你需要亲自做的事(按顺序,标 👤)
1. 👤 注册 Metaculus 账号:https://www.metaculus.com/
2. 👤 创建 Bot,复制 API Token:https://www.metaculus.com/accounts/settings/bots/(第一个 bot 是有获奖资格的主 bot)
3. 👤 填参赛表(必填,共 3 题,同时也是 LLM 额度申请):https://forms.gle/aQdYMq9Pisrf1v7d8
4. 👤 选一个免费的 LLM,拿到 key(三选一即可):
   - 七牛 Conatus:https://www.qiniu.com/ (实名)→ `LLM_BASE_URL=https://api.qnaigc.com/v1`,`LLM_MODEL=qiniu/conatus-free`
   - 智谱:https://open.bigmodel.cn/ → `LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4`,`LLM_MODEL=glm-4-flash`
   - 硅基流动:https://cloud.siliconflow.cn/ → `LLM_BASE_URL=https://api.siliconflow.cn/v1`,`LLM_MODEL=<免费模型名>`
   - OpenRouter:https://openrouter.ai/keys → `LLM_BASE_URL=https://openrouter.ai/api/v1`,`LLM_MODEL=<xxx:free>`
5. 👤(可选)申请免费 AskNews 搜索:每个赛季要通过 Discord @freqai 或 contact@asknews.app 续期
6. 👤 Fork 模板仓库:https://github.com/Metaculus/metac-bot-template(必须是**公开**仓库,Actions 才免费;开源 bot 的额度大约翻倍)。把本目录改过的 `main.py` 覆盖进去。
7. 👤 在 GitHub 仓库 Settings → Secrets → Actions 里添加 `METACULUS_TOKEN`、`LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`,并在 workflow 的 env 里引用它们。然后启用 Actions。
8. 👤 赛季结束后填写结束问卷(获奖必须)。

## 本地运行(盒子上:/workspace/metaculus-bot,依赖已用 uv 装好,Python 3.11–3.13)
```bash
export METACULUS_TOKEN=xxx LLM_BASE_URL=https://api.qnaigc.com/v1 LLM_API_KEY=xxx LLM_MODEL=qiniu/conatus-free
uv run python main.py --mode test_questions --dry-run   # 只预测、不提交(也可以设 DRY_RUN=1)
uv run python main.py --mode tournament                  # 正式参赛:AIB + MiniBench,会提交
```
离线自测,不需要任何 key:
```bash
uv run python mock_llm_server.py &
LLM_BASE_URL=http://127.0.0.1:8765/v1 LLM_API_KEY=mock LLM_MODEL=mock uv run python dry_run_offline.py
```

## 改动说明
- `main.py`:新增 `--dry-run` 参数和 `DRY_RUN=1` 环境变量(不发布预测);如果同时设置了 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`,所有角色都改用这个 OpenAI 兼容接口(litellm `openai/<model>`)。可以用 `RESEARCHER=asknews/news-summaries` 单独指定研究源。
- `dry_run_offline.py`:用本地构造的题目跑完整流程,永远不提交。
- `mock_llm_server.py`:离线的假 LLM。

## 规则要点与风险
- 全程不能有人工干预;每人只能有 1 个有获奖资格的 bot;获奖需要附带推理评论;代码可能被检查。
- 3 人及以上公司做的商业 bot 不能领奖,除非开源。
- 免费模型能力弱,限流严格,排名和奖金都不保证。Conatus 的免费期截至 11-30,之后可能收费,到时请换模型。
- `tournament` 模式每 20 分钟跑一次,免费额度可能很快用完。可以把 `predictions_per_research_report` 调小。

## GitHub Actions 自动参赛（真实提交）

1. 在 GitHub 上 **Fork** `Metaculus/metac-bot-template`（或把本目录推到你自己的仓库），确保包含本地修改：`main.py`、`llm_fallback.py`、`.github/workflows/*.yaml`。
2. 打开 Fork 仓库 → **Settings → Secrets and variables → Actions**：
   - **Secrets**（New repository secret）：
     - `METACULUS_TOKEN` — Metaculus 机器人账号 token（必须）
     - `LLM_API_KEY` — OpenRouter API key（必须）
   - **Variables**（Variables 标签页，也可作为 secret 存）：
     - `LLM_MODEL` — 例如 `nvidia/nemotron-3-ultra-550b-a55b:free,google/gemma-4-31b-it:free,google/gemma-4-26b-a4b-it:free`（逗号分隔 = 按顺序回退；必须）
     - `LLM_BASE_URL` — 可选，默认 `https://openrouter.ai/api/v1`
     - `NUM_PREDICTIONS` — 可选，每题预测次数，默认 `1`
3. 打开 **Actions** 标签页，点击 “I understand my workflows, go ahead and enable them”；再进入 “Forecast on new AI tournament questions” 工作流，若显示定时任务已禁用则点 **Enable workflow**。
4. 可先点 **Run workflow** 手动触发一次检查日志。工作流中**未设置 DRY_RUN**，会真实提交预测；定时为每 20 分钟（`7,27,47 * * * *`），已预测过的问题会被跳过。

### 请求次数预算（OpenRouter 免费额度约 50 次/天；账户充值 ≥$10 后为 1000 次/天）
- 默认不做联网调研（`RESEARCHER=no_research`，0 次请求）；每题 ≈ 1 次预测 + 1 次结构化解析，部分题型多 1 次，实测约 3 次/题 → 免费额度约够 15 道新题/天。
- 失败（429/503/超时）时指数退避重试，每个模型 `LLM_TRIES_PER_MODEL`（默认 2）次，再回退到列表中下一个模型；重试也计入额度。
- 想要更准：调大 `NUM_PREDICTIONS`（每次 +2 请求/题）或接入 AskNews 免费额度（设置 `ASKNEWS_CLIENT_ID`/`ASKNEWS_SECRET` 与 `RESEARCHER=asknews/news-summaries`）。

### 本地小规模 dry run（不提交）
```bash
set -a; . ~/.secrets/openrouter.env; . ~/.secrets/metaculus.env; set +a
export LLM_BASE_URL=https://openrouter.ai/api/v1 LLM_API_KEY="$OPENROUTER_API_KEY" \
  LLM_MODEL="nvidia/nemotron-3-ultra-550b-a55b:free,google/gemma-4-31b-it:free" MAX_QUESTIONS=2
uv run python main.py --dry-run                      # 赛事 + MiniBench 前 2 题
uv run python main.py --dry-run --mode test_questions # bot-testing-area 前 2 题
```
