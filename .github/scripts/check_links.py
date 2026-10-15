#!/usr/bin/env python3
"""确定性检查：相对链接是否有效，README 是否索引了全部分析文章，文章编号是否连续。

审查阶段把结果交给 Claude 作为证据；验证阶段如果检查失败，
即使 Claude 判定“通过”也会被否决。退出码 0 表示通过，1 表示有问题。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
# README 必须索引这些目录下的每一篇文章
CONTENT_DIRS = ["ai-for-security", "security-for-ai"]
SKIP_DIRS = {".git", ".claude-loop", "node_modules"}

LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
EXTERNAL_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)  # http:、https:、mailto: 等


def md_files():
    for path in sorted(ROOT.rglob("*.md")):
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


def links(path: Path):
    """逐个返回 (行号, 链接目标)，跳过代码块。"""
    in_fence = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            for match in LINK_RE.finditer(line):
                yield lineno, match.group(1)


def local_target(md: Path, target: str) -> Path | None:
    """把相对链接解析成文件路径；外部链接和页内锚点返回 None。"""
    if EXTERNAL_RE.match(target) or target.startswith("#"):
        return None
    file_part = unquote(target.split("#", 1)[0])
    if not file_part:
        return None
    if file_part.startswith("/"):
        return ROOT / file_part.lstrip("/")
    return md.parent / file_part


def main() -> int:
    problems = []
    for md in md_files():
        for lineno, target in links(md):
            resolved = local_target(md, target)
            if resolved is not None and not resolved.exists():
                problems.append(f"{md.relative_to(ROOT)}:{lineno}: 链接目标不存在：{target}")

    readme = ROOT / "README.md"
    if readme.exists():
        indexed = {p.resolve() for _, t in links(readme) if (p := local_target(readme, t))}
        for directory in CONTENT_DIRS:
            for article in sorted((ROOT / directory).glob("*.md")):
                if article.resolve() not in indexed:
                    problems.append(f"README.md: 没有索引 {article.relative_to(ROOT)}")

    # 文章编号全仓库连续且不重复（新增论文取最大编号 + 1）
    numbers = {}
    for directory in CONTENT_DIRS:
        for article in (ROOT / directory).glob("*.md"):
            if match := re.match(r"(\d+)-", article.name):
                numbers.setdefault(int(match.group(1)), []).append(str(article.relative_to(ROOT)))
    for number, files in sorted(numbers.items()):
        if len(files) > 1:
            problems.append(f"文章编号 {number:02d} 重复：{'、'.join(sorted(files))}")
    missing = sorted(set(range(1, max(numbers, default=0) + 1)) - set(numbers))
    if missing:
        problems.append("文章编号不连续，缺少：" + "、".join(f"{n:02d}" for n in missing))

    if problems:
        print("\n".join(problems))
        print(f"\n共 {len(problems)} 个问题")
        return 1
    print("相对链接、README 索引与文章编号检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
