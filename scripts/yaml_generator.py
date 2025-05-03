#!/usr/bin/env python
"""yaml_generator.py – v7.0  全リンク・バナー・ボタン押下用

- requests で HTML を取得 (サーバーレンダリング)
- BeautifulSoup でクリック対象を抽出：
    • <button>
    • <input type=button|submit|reset>
    • role="button" を持つ要素 (<a>,<div>,<span>…)
    • すべての <a href> リンク
    • バナー的 <img> : <a><img> または img.banner/img.ad/img.hero
- クリック対象は 1 ページ 100 個まで (過剰クリック防止)
- YAML には status_code と click:<selector> を列挙
"""
import argparse, pathlib, sys, urllib.parse as up, yaml, re, requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("--urls", nargs="*", help="フル URL 群 (同一ホスト)")
parser.add_argument("--base", help="ルート URL")
parser.add_argument("--paths", nargs="*", help="相対パス群")
parser.add_argument("--max", type=int, default=100, help="1ページの最大クリック数")
args = parser.parse_args()

if args.urls:
    parsed = [up.urlparse(u) for u in args.urls]
    hosts = {f"{p.scheme}://{p.netloc}" for p in parsed}
    if len(hosts) != 1:
        sys.exit("❌ --urls は同一ホストのみ")
    BASE = hosts.pop()
    paths = [(p.path or "/") for p in parsed]
elif args.base:
    BASE = args.base.rstrip("/")
    paths = args.paths or ["/"]
else:
    sys.exit("❌ --urls か --base を指定してください")

specs = []
for path in paths:
    url = f"{BASE}{path}"
    try:
        resp = requests.get(url, timeout=15)
        status = resp.status_code
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"⚠️  Fetch failed {url}: {e}")
        status = 0; soup = BeautifulSoup("", "html.parser")

    selectors = []

    # 1. button tags
    selectors += [f"button:nth-of-type({i+1})" for i,_ in enumerate(soup.select("button"))]

    # 2. input type button/submit/reset
    selectors += [f"input[type={inp.get('type')}]:nth-of-type({i+1})"
                  for i,inp in enumerate(soup.select("input[type=button],input[type=submit],input[type=reset]"))]

    # 3. role="button"
    selectors += [f"{el.name}[role=button]:nth-of-type({i+1})" for i,el in enumerate(soup.select("[role=button]"))]

    # 4. all anchor links
    selectors += [f"a[href]:nth-of-type({i+1})" for i,_ in enumerate(soup.select("a[href]"))]

    # 5. banner images (<a><img>) or <img class*=banner|ad|hero>
    for i,a in enumerate(soup.select("a:has(img)")):
        selectors.append(f"a:has(img):nth-of-type({i+1})")
    for i,img in enumerate(soup.select("img[class*='banner'], img[class*='ad'], img[class*='hero']")):
        selectors.append(f"img[class*='banner ad hero']:nth-of-type({i+1})")

    # 去重 & 上限
    uniq = []
    for s in selectors:
        if s not in uniq:
            uniq.append(s)
    selectors = uniq[:args.max]

    assertions = [f"status_code:{status}"] + [f"click:{sel}" for sel in selectors]
    specs.append({"path": path, "assertions": assertions})

out = pathlib.Path("specs/tests.yml")
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", encoding="utf-8") as f:
    yaml.dump({"base_url": BASE, "pages": specs}, f, allow_unicode=True)

print(f"✅ YAML written → {out}  (total clicks: {sum(len(p['assertions'])-1 for p in specs)})")