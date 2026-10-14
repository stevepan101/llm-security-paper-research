#!/usr/bin/env python3
"""Claude 自动改进闭环（审查 → issue → 修复 → 验证 → 复盘）的胶水脚本。

分工原则：Claude 只读写仓库文件，并按 JSON schema 返回结构化结果；
所有 GitHub 写操作都由这里的确定性代码完成，包括建 issue、提交、开 PR、打标签、
触发下一阶段。这样每一步都可审计、可限流，Claude 也不需要 GitHub 写权限。
各子命令由 .github/workflows/claude-*.yml 调用，设计说明见 docs/claude-auto-improve-loop.md。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from functools import cache
from pathlib import Path

CTX = Path(".claude-loop")  # 给 Claude 读的上下文文件，已加入 .gitignore，不会被提交
SCHEMAS = Path(".github/claude/schemas")
GOALS_FILE = ".github/claude/review-goals.md"
FIX_WORKFLOW = "claude-fix.yml"
VERIFY_WORKFLOW = "claude-verify.yml"
BOT_LOGIN = "github-actions"  # 工作流用 GITHUB_TOKEN 发评论时的作者
BOT_GIT = ["-c", "user.name=github-actions[bot]",
           "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com"]

LABELS = {
    "claude-audit": ("5319e7", "Claude 审查发现的问题"),
    "claude-fix": ("1d76db", "允许 Claude 自动修复"),
    "claude-autofix": ("0e8a16", "Claude 自动修复的 PR"),
    "claude-verified": ("2ea44f", "Claude 验证通过，等待人工合并"),
    "needs-human": ("d93f0b", "自动闭环无法解决，需要人工处理"),
    "claude-retro": ("c5def5", "审查标准复盘"),
    "severity:high": ("b60205", "严重：事实错误或误导读者"),
    "severity:medium": ("fbca04", "中等：影响准确性或一致性"),
    "severity:low": ("c2e0c6", "轻微：措辞、格式"),
}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
SEVERITY_ZH = {"high": "高", "medium": "中", "low": "低"}
STATUS_ICON = {"met": "✅ 满足", "partial": "🟡 部分满足", "unmet": "❌ 未满足"}
VERDICT_ZH = {"pass": "✅ 通过", "fail": "❌ 未通过", "needs_human": "🙋 需要人工判断"}
# 修复阶段只允许改 Markdown 内容文件。工作流（.github/）和 Claude 自身的配置（CLAUDE.md、.claude/）
# 一律不许改，否则被注入的修复方可以借此影响验证方
FIX_ALLOWED = re.compile(r"^(?!\.github/|\.claude/)(?!(?:.*/)?CLAUDE\.md$).+\.md$")
TRUSTED_CONFIG = [".github", ".claude", "CLAUDE.md"]
MARKER_RE = re.compile(r"<!-- claude-loop:(\w+)((?: [\w-]+=\S+)*) -->")


# ---------- 基础工具 ----------

def run(*cmd: str, stdin: str | None = None, check: bool = True) -> str:
    proc = subprocess.run(cmd, input=stdin, text=True, capture_output=True)
    if check and proc.returncode != 0:
        sys.stderr.write(proc.stdout + proc.stderr)
        raise SystemExit(f"命令失败（{proc.returncode}）：{' '.join(cmd[:4])} …")
    return proc.stdout.strip()


def gh(*args: str, **kw) -> str:
    return run("gh", *args, **kw)


def gh_json(*args: str):
    out = gh(*args)
    return json.loads(out) if out else None


def git(*args: str, **kw) -> str:
    return run("git", *args, **kw)


def env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, "")
    if value:
        return value
    if default is None:
        raise SystemExit(f"缺少环境变量 {name}")
    return default


def set_output(**values) -> None:
    lines = "".join(f"{k}={v}\n" for k, v in values.items())
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(lines)
    else:
        print(lines, end="")


def step_summary(text: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)


def run_url() -> str:
    return "{}/{}/actions/runs/{}".format(
        os.environ.get("GITHUB_SERVER_URL", "https://github.com"),
        os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GITHUB_RUN_ID", ""))


@cache
def default_branch() -> str:
    return gh("repo", "view", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name")


def schema(name: str) -> str:
    """压成一行，供 claude_args 的 --json-schema '…' 使用。"""
    data = json.loads((SCHEMAS / f"{name}.json").read_text(encoding="utf-8"))
    return json.dumps(data, separators=(",", ":"))


def load_result() -> dict:
    raw = os.environ.get("RESULT", "").strip()
    if not raw:
        raise SystemExit("Claude 没有返回结构化结果（可能超出了 max-turns），请查看本次运行日志")
    return json.loads(raw)


def write_ctx(name: str, text: str) -> None:
    CTX.mkdir(exist_ok=True)
    (CTX / name).write_text(text, encoding="utf-8")


def ensure_labels() -> None:
    for name, (color, description) in LABELS.items():
        gh("label", "create", name, "--color", color, "--description", description, "--force")


def dispatch(workflow: str, **inputs) -> None:
    """用 workflow_dispatch 串联下一阶段。

    GITHUB_TOKEN 产生的事件（建 issue、开 PR、push）不会触发其他工作流，
    workflow_dispatch 是例外，所以阶段之间显式调用，轮次作为参数传递。
    """
    args = ["workflow", "run", workflow, "--ref", default_branch()]
    for key, value in inputs.items():
        args += ["-f", f"{key}={value}"]
    gh(*args)


# ---------- issue / PR 操作 ----------

def marker(kind: str, **attrs) -> str:
    text = "".join(f" {k}={v}" for k, v in attrs.items())
    return f"<!-- claude-loop:{kind}{text} -->"


def parse_marker(body: str, kind: str) -> dict | None:
    for match in MARKER_RE.finditer(body or ""):
        if match.group(1) == kind:
            return dict(pair.split("=", 1) for pair in match.group(2).split())
    return None


def cell(text) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip() or " "


def bullets(items) -> str:
    return "\n".join(f"- {item}" for item in items) or "- 无"


def add_labels(kind: str, number, *labels: str) -> None:
    gh(kind, "edit", str(number), "--add-label", ",".join(labels))


def remove_labels(kind: str, number, *labels: str) -> None:
    gh(kind, "edit", str(number), "--remove-label", ",".join(labels), check=False)


def comment(kind: str, number, body: str) -> None:
    gh(kind, "comment", str(number), "--body-file", "-", stdin=body)


def branch_for(issue) -> str:
    return f"claude/issue-{issue}"


def open_pr_for(branch: str) -> int | None:
    prs = gh_json("pr", "list", "--head", branch, "--state", "open", "--json", "number") or []
    return prs[0]["number"] if prs else None


def is_bot(c: dict) -> bool:
    return ((c.get("author") or {}).get("login") or "").removesuffix("[bot]") == BOT_LOGIN


def latest_bot_comment(kind: str, number, marker_kind: str) -> str | None:
    """取工作流自己发的、带指定标记的最新评论；忽略其他人伪造的同名标记。"""
    comments = gh_json(kind, "view", str(number), "--json", "comments")["comments"]
    for c in reversed(comments):
        if is_bot(c) and parse_marker(c["body"], marker_kind) is not None:
            return c["body"]
    return None


def issue_markdown(issue: dict) -> str:
    return f"# #{issue['number']} {issue['title']}\n\n{issue['body'] or ''}\n"


def link_check() -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, ".github/scripts/check_links.py"],
                          text=True, capture_output=True)
    return proc.returncode == 0, proc.stdout + proc.stderr


def staged_files() -> list[str]:
    git("add", "-A")
    git("reset", "-q", "--", str(CTX), ".claude")  # 上下文文件和 Claude 配置永不提交
    out = git("-c", "core.quotePath=false", "diff", "--cached", "--name-only")
    return [line for line in out.splitlines() if line]


def escalate(issue, pr, reason: str) -> None:
    text = f"{marker('escalate')}\n🙋 **转人工处理**：{reason}\n\n[运行记录]({run_url()})"
    if issue:
        add_labels("issue", issue, "needs-human")
        comment("issue", issue, text)
    if pr:
        add_labels("pr", pr, "needs-human")
        comment("pr", pr, text)
    step_summary(f"转人工处理：{reason}")


# ---------- ① 审查 ----------

def cmd_audit_context(_args) -> None:
    ensure_labels()
    issues = gh_json("issue", "list", "--label", "claude-audit", "--state", "all", "--limit", "500",
                     "--json", "number,title,state,stateReason,body") or []
    known = [{
        "number": it["number"],
        "title": it["title"],
        "state": it["state"],
        "stateReason": it.get("stateReason") or "",
        "fingerprint": (parse_marker(it["body"], "audit") or {}).get("fingerprint", ""),
    } for it in issues]
    write_ctx("known-issues.json", json.dumps(known, ensure_ascii=False, indent=2))
    _, report = link_check()
    write_ctx("link-check.txt", report)

    open_count = sum(1 for k in known if k["state"] == "OPEN")
    budget = max(0, min(int(env("MAX_NEW", "5")), int(env("MAX_OPEN", "10")) - open_count))
    if budget == 0:
        step_summary(f"积压的审查 issue 已有 {open_count} 个，达到上限，本次跳过审查。")
    set_output(budget=budget, schema=schema("audit"))


def normalize_fingerprint(fp: str) -> str:
    return re.sub(r"[^\w./:#-]+", "-", fp.strip()).strip("-")


def render_issue(f: dict, fingerprint: str) -> str:
    files = "\n".join(f"- `{p}`" for p in f["files"]) or "- （未指明）"
    criteria = "\n".join(f"- [ ] {c}" for c in f["acceptance_criteria"])
    return f"""{marker('audit', fingerprint=fingerprint)}
**审查目标**：{f['goal']}　**严重程度**：{SEVERITY_ZH.get(f['severity'], f['severity'])}　**可自动修复**：{'是' if f['auto_fixable'] else '否'}

### 问题
{f['problem']}

### 涉及文件
{files}

### 证据
{f['evidence']}

### 修复建议
{f['suggestion']}

### 验收标准
{criteria}

---
_由 Claude 自动审查生成（[运行记录]({run_url()})）。如果是误报，请选择 “Close as not planned” 关闭，之后的审查会避开同类问题；如果同意自动修复，给本 issue 加上 `claude-fix` 标签。_
"""


def cmd_create_issues(_args) -> None:
    result = load_result()
    budget = int(env("BUDGET"))
    auto_fix = env("AUTO_FIX", "true") == "true"
    auto_severities = {s.strip() for s in env("AUTO_FIX_SEVERITIES", "low,medium").split(",")}
    known = json.loads((CTX / "known-issues.json").read_text(encoding="utf-8"))
    # 指纹去重：与未关闭的 issue 重复，或被人工判定为误报（not planned）的，都不再报告。
    # 修复后再次出现的问题（completed）允许重新报告，视为回归。
    blocked = {k["fingerprint"] for k in known if k["fingerprint"]
               and (k["state"] == "OPEN" or k["stateReason"] == "NOT_PLANNED")}

    lines = [f"## 审查结果\n\n{result.get('summary', '')}\n"]
    created = 0
    findings = sorted(result.get("findings", []), key=lambda f: SEVERITY_ORDER.get(f["severity"], 9))
    for f in findings:
        fingerprint = normalize_fingerprint(f["fingerprint"])
        if created >= budget:
            lines.append(f"- 超出本次额度，未创建：{f['title']}")
            continue
        if fingerprint in blocked:
            lines.append(f"- 与已有 issue 重复或已判定为误报，跳过：{f['title']}（`{fingerprint}`）")
            continue
        blocked.add(fingerprint)
        url = gh("issue", "create", "--title", f["title"], "--body-file", "-",
                 "--label", f"claude-audit,severity:{f['severity']}", stdin=render_issue(f, fingerprint))
        number = int(url.rstrip("/").rsplit("/", 1)[1])
        created += 1
        auto = auto_fix and f["auto_fixable"] and f["severity"] in auto_severities
        if auto:
            add_labels("issue", number, "claude-fix")
            dispatch(FIX_WORKFLOW, issue=number, round=1)
        lines.append(f"- 已创建 #{number}（{f['severity']}）{'，已分派自动修复' if auto else ''}：{f['title']}")
    step_summary("\n".join(lines))


# ---------- ② 修复 ----------

def cmd_fix_context(_args) -> None:
    ensure_labels()
    number, rnd = int(env("ISSUE")), int(env("ROUND", "1"))
    issue = gh_json("issue", "view", str(number), "--json", "number,title,body,state")
    branch = branch_for(number)
    pr = open_pr_for(branch)

    skip = None
    if issue["state"] != "OPEN":
        skip = f"issue #{number} 已关闭"
    elif rnd == 1 and pr:
        skip = f"issue #{number} 已有进行中的 PR #{pr}，跳过重复触发"
    elif rnd > 1 and not pr:
        skip = f"第 {rnd} 轮修复找不到 issue #{number} 对应的 PR"
    if skip:
        print(f"::notice::{skip}")
        step_summary(skip)
        set_output(skip="true")
        return

    base = default_branch()
    git("fetch", "origin", base)
    if rnd == 1:
        git("checkout", "-B", branch, f"origin/{base}")
    else:
        git("fetch", "origin", branch)
        git("checkout", "-B", branch, "FETCH_HEAD")
        write_ctx("feedback.md", latest_bot_comment("pr", pr, "verify") or "（没有找到上一轮的验证意见）")
        write_ctx("current.diff", git("diff", f"origin/{base}...HEAD"))
    write_ctx("issue.md", issue_markdown(issue))
    set_output(skip="false", branch=branch, pr=pr or "", schema=schema("fix"))


def render_fix_report(r: dict, rnd: int) -> str:
    changes = "\n".join(f"- `{c['file']}`：{c['description']}" for c in r["changes"]) or "- 无"
    rows = "\n".join(f"| {cell(c['criterion'])} | {'✅' if c['addressed'] else '⚠️'} | {cell(c['note'])} |"
                     for c in r["criteria"])
    text = f"""## Claude 修复说明（第 {rnd} 轮）

{r['summary']}

### 改动明细
{changes}

### 验收标准处理情况
| 验收标准 | 已处理 | 说明 |
|---|---|---|
{rows}
"""
    if r.get("notes_for_reviewer"):
        text += f"\n### 请验证者关注\n{r['notes_for_reviewer']}\n"
    return text


def cmd_open_pr(_args) -> None:
    number, rnd = int(env("ISSUE")), int(env("ROUND", "1"))
    branch, pr = env("BRANCH"), os.environ.get("PR") or None
    result = load_result()

    files = staged_files()
    outside = [f for f in files if not FIX_ALLOWED.match(f)]
    if result["cannot_fix"] or not files or outside:
        if result["cannot_fix"]:
            reason = f"Claude 认为无法自动修复：{result['cannot_fix_reason']}"
        elif outside:
            reason = "修复改动了允许范围以外的文件：" + "、".join(f"`{f}`" for f in outside)
        else:
            reason = "Claude 没有做出任何修改"
        escalate(number, pr, reason)
        return

    title = gh_json("issue", "view", str(number), "--json", "title")["title"]
    git(*BOT_GIT, "commit", "-m", f"修复 #{number}（第 {rnd} 轮）：{title}\n\n由 Claude 自动改进闭环生成：{run_url()}")
    # 首轮总是从主干新建分支，覆盖之前已关闭 PR 留下的同名分支
    git("push", *(["--force"] if rnd == 1 else []), "origin", f"HEAD:refs/heads/{branch}")

    report = render_fix_report(result, rnd)
    if pr is None:
        body = (f"Closes #{number}\n\n{marker('pr', issue=number)}\n{report}\n---\n"
                "_本 PR 由 Claude 自动改进闭环生成。独立验证的结果会以评论形式出现在下方；"
                "验证通过后会加上 `claude-verified` 标签，等待人工审阅合并。_\n")
        url = gh("pr", "create", "--base", default_branch(), "--head", branch,
                 "--title", f"[Claude] {title}", "--body-file", "-", "--label", "claude-autofix", stdin=body)
        pr = int(url.rstrip("/").rsplit("/", 1)[1])
        comment("issue", number, f"已创建修复 PR #{pr}，正在进行独立验证。")
    else:
        comment("pr", pr, f"{marker('fix', round=rnd)}\n{report}")
        remove_labels("pr", pr, "claude-verified")
    dispatch(VERIFY_WORKFLOW, pr=pr, round=rnd)
    step_summary(f"第 {rnd} 轮修复已推送到 PR #{pr}，已触发验证。")


# ---------- ③ 验证 ----------

def cmd_verify_context(_args) -> None:
    ensure_labels()
    pr_number = int(env("PR"))
    pr = gh_json("pr", "view", str(pr_number), "--json",
                 "number,title,body,state,headRefName,closingIssuesReferences")
    refs = pr.get("closingIssuesReferences") or []
    issue_no = refs[0]["number"] if refs else int((parse_marker(pr["body"], "pr") or {}).get("issue", 0))
    if pr["state"] != "OPEN" or not issue_no:
        reason = f"PR #{pr_number} 已不是打开状态" if pr["state"] != "OPEN" else f"PR #{pr_number} 没有关联 issue"
        print(f"::notice::{reason}")
        step_summary(reason)
        set_output(skip="true")
        return

    base, head = default_branch(), pr["headRefName"]
    git("fetch", "origin", base)
    git("fetch", "origin", head)
    git("checkout", "-B", head, "FETCH_HEAD")
    for path in TRUSTED_CONFIG:  # 验证方使用主干上的约定和标准，不用 PR 里的版本
        git("checkout", f"origin/{base}", "--", path, check=False)

    issue = gh_json("issue", "view", str(issue_no), "--json", "number,title,body")
    write_ctx("issue.md", issue_markdown(issue))
    write_ctx("pr.diff", git("diff", f"origin/{base}...HEAD"))
    previous = latest_bot_comment("pr", pr_number, "verify")
    if previous:
        write_ctx("prev-feedback.md", previous)
    links_ok, report = link_check()
    write_ctx("link-check.txt", report)
    set_output(skip="false", issue=issue_no, links_ok=str(links_ok).lower(), schema=schema("verify"))


def render_verify(r: dict, verdict: str, regressions: list[str], rnd: int, next_step: str) -> str:
    rows = "\n".join(f"| {cell(c['criterion'])} | {STATUS_ICON.get(c['status'], c['status'])} | {cell(c['evidence'])} |"
                     for c in r["criteria"])
    suggestions = "\n".join(f"{i}. {s}" for i, s in enumerate(r["suggestions"], 1)) or "无"
    return f"""{marker('verify', round=rnd, verdict=verdict)}
## Claude 验证结果（第 {rnd} 轮）：{VERDICT_ZH[verdict]}

{r['summary']}

| 验收标准 | 结论 | 证据 |
|---|---|---|
{rows}

### 引入的新问题
{bullets(regressions)}

### 修改建议
{suggestions}

**下一步**：{next_step}

<sub>验证由独立的 Claude 会话完成，不参考修复方的自述（[运行记录]({run_url()})）。</sub>
"""


def cmd_verify_route(_args) -> None:
    pr, issue, rnd = int(env("PR")), int(env("ISSUE")), int(env("ROUND", "1"))
    max_rounds = int(env("MAX_ROUNDS", "3"))
    merge_severities = {s.strip() for s in env("AUTO_MERGE_SEVERITIES", "none").split(",")}
    r = load_result()

    verdict, regressions = r["verdict"], list(r["regressions"])
    if env("LINKS_OK", "true") != "true":
        # 确定性检查优先于 LLM 的判断
        regressions.append("确定性检查未通过（check_links.py）：存在失效的相对链接，或 README 缺少文章索引")
        if verdict == "pass":
            verdict = "fail"

    severity = next((l["name"].split(":", 1)[1] for l in
                     gh_json("issue", "view", str(issue), "--json", "labels")["labels"]
                     if l["name"].startswith("severity:")), "")
    auto_merge = verdict == "pass" and severity in merge_severities
    if verdict == "pass":
        next_step = "按配置自动合并。" if auto_merge else "等待人工审阅合并。"
    elif verdict == "fail" and rnd < max_rounds:
        next_step = f"已自动触发第 {rnd + 1} 轮修复，修复方会逐条处理上面的建议。"
    elif verdict == "fail":
        next_step = f"已达到 {max_rounds} 轮上限，转人工处理。"
    else:
        next_step = "验证者认为该 issue 本身需要人工判断，转人工处理。"

    # 先发验证评论，再触发下一轮：下一轮修复读取的正是这条评论
    comment("pr", pr, render_verify(r, verdict, regressions, rnd, next_step))
    if verdict == "pass":
        add_labels("pr", pr, "claude-verified")
        remove_labels("pr", pr, "needs-human")
        comment("issue", issue, f"修复 PR #{pr} 已通过 Claude 验证（第 {rnd} 轮），{next_step}")
        if auto_merge:
            gh("pr", "merge", str(pr), "--squash", "--delete-branch")
    elif verdict == "fail" and rnd < max_rounds:
        dispatch(FIX_WORKFLOW, issue=issue, round=rnd + 1)
    else:
        add_labels("pr", pr, "needs-human")
        add_labels("issue", issue, "needs-human")
    step_summary(f"PR #{pr} 第 {rnd} 轮验证：{VERDICT_ZH[verdict]}；{next_step}")


# ---------- ④ 复盘 ----------

def verdicts(item: dict) -> list[str]:
    return [m["verdict"] for c in item["comments"]
            if is_bot(c) and (m := parse_marker(c["body"], "verify")) and "verdict" in m]


def has_label(item: dict, name: str) -> bool:
    return any(l["name"] == name for l in item["labels"])


def clip(text: str, limit: int = 1500) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[:limit] + "…（已截断）"


def cmd_retro_context(_args) -> None:
    ensure_labels()
    days = int(env("RETRO_DAYS", "30"))
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    issues = gh_json("issue", "list", "--label", "claude-audit", "--state", "all", "--limit", "200",
                     "--search", f"updated:>={since}",
                     "--json", "number,title,state,stateReason,labels,body,comments") or []
    prs = gh_json("pr", "list", "--label", "claude-autofix", "--state", "all", "--limit", "200",
                  "--search", f"updated:>={since}", "--json", "number,title,state,labels,comments") or []
    if not issues and not prs:
        step_summary(f"最近 {days} 天没有闭环活动，跳过复盘。")
        set_output(skip="true")
        return

    rounds = [len(verdicts(p)) for p in prs if verdicts(p)]
    stats = {
        "period": f"最近 {days} 天（{since} 起）",
        "issues": {
            "total": len(issues),
            "open": sum(i["state"] == "OPEN" for i in issues),
            "fixed": sum(i.get("stateReason") == "COMPLETED" for i in issues),
            "false_positive_not_planned": sum(i.get("stateReason") == "NOT_PLANNED" for i in issues),
            "needs_human": sum(has_label(i, "needs-human") for i in issues),
        },
        "prs": {
            "total": len(prs),
            "merged": sum(p["state"] == "MERGED" for p in prs),
            "closed_without_merge": sum(p["state"] == "CLOSED" for p in prs),
            "first_round_pass": sum(verdicts(p)[:1] == ["pass"] for p in prs),
            "needs_human": sum(has_label(p, "needs-human") for p in prs),
            "avg_verify_rounds": round(sum(rounds) / len(rounds), 2) if rounds else 0,
        },
    }
    write_ctx("retro-stats.json", json.dumps(stats, ensure_ascii=False, indent=2))

    cases = ["# 复盘案例\n"]
    for i in issues:
        if i.get("stateReason") == "NOT_PLANNED":
            human = [c for c in i["comments"] if not is_bot(c)][-3:]  # 人工关闭时写的理由
            cases.append(f"## 误报：#{i['number']} {i['title']}\n\n{clip(i['body'])}\n\n"
                         + "\n".join(f"> 评论：{clip(c['body'], 500)}" for c in human))
    for p in prs:
        if has_label(p, "needs-human") or len(verdicts(p)) >= 2:
            history = [c["body"] for c in p["comments"] if is_bot(c) and parse_marker(c["body"], "verify")]
            cases.append(f"## 多轮或转人工：PR #{p['number']} {p['title']}\n\n"
                         + "\n\n".join(clip(h, 1200) for h in history))
    write_ctx("retro-cases.md", "\n\n".join(cases))
    set_output(skip="false", schema=schema("retro"))


def cmd_open_retro_pr(_args) -> None:
    result = load_result()
    files = staged_files()
    if not files:
        step_summary(f"本期复盘结论：无需修改审查标准。\n\n{result['summary']}")
        return
    if files != [GOALS_FILE]:
        raise SystemExit(f"复盘只允许修改 {GOALS_FILE}，实际改动：{files}")

    stats = json.loads((CTX / "retro-stats.json").read_text(encoding="utf-8"))
    branch = f"claude/retro-{dt.date.today():%Y-%m-%d}"
    git("checkout", "-B", branch)
    git(*BOT_GIT, "commit", "-m", f"复盘：根据最近的闭环效果更新审查标准\n\n{run_url()}")
    git("push", "--force", "origin", f"HEAD:refs/heads/{branch}")
    body = f"""## 审查标准复盘：{stats['period']}

{result['summary']}

### 对 review-goals.md 的修改
{bullets(result['changes_made'])}

### 观察
{bullets(result['observations'])}

### 统计
```json
{json.dumps(stats, ensure_ascii=False, indent=2)}
```

---
_由 Claude 每月复盘生成，请人工审阅后合并。合并后，下一次审查就会使用新的标准。_
"""
    existing = open_pr_for(branch)
    if existing:
        comment("pr", existing, body)
    else:
        gh("pr", "create", "--base", default_branch(), "--head", branch, "--title", "[Claude] 复盘：更新审查标准",
           "--body-file", "-", "--label", "claude-retro", stdin=body)
    step_summary(body)


# ---------- 入口 ----------

def cmd_escalate(args) -> None:
    issue = args.issue or None
    pr = args.pr or (open_pr_for(branch_for(issue)) if issue else None)
    escalate(issue, pr, args.reason)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in {
        "audit-context": cmd_audit_context, "create-issues": cmd_create_issues,
        "fix-context": cmd_fix_context, "open-pr": cmd_open_pr,
        "verify-context": cmd_verify_context, "verify-route": cmd_verify_route,
        "retro-context": cmd_retro_context, "open-retro-pr": cmd_open_retro_pr,
    }.items():
        sub.add_parser(name).set_defaults(func=func)
    esc = sub.add_parser("escalate")
    esc.add_argument("--issue", default="")
    esc.add_argument("--pr", default="")
    esc.add_argument("--reason", required=True)
    esc.set_defaults(func=cmd_escalate)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
