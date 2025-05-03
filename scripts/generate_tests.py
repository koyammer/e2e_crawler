#!/usr/bin/env python
"""generate_tests.py – v5.1  (YAML 専用ワンショット変換)

specs/tests.yml を読み込み、Playwright+pytest テストを
 tests/generated/test_<slug>.py として書き出します。
"""
import pathlib, yaml, re, textwrap, sys

SPEC = pathlib.Path("specs/tests.yml")
DEST = pathlib.Path("tests/generated")
DEST.mkdir(parents=True, exist_ok=True)

# --- 入力チェック --------------------------------------------------
if not SPEC.exists():
    sys.exit("❌ specs/tests.yml が見つかりません。まず yaml_generator.py 等で作成してください")

spec = yaml.safe_load(SPEC.read_text())
base_url = spec.get("base_url")
pages = spec.get("pages", [])
if not base_url or not pages:
    sys.exit("❌ YAML に base_url または pages が定義されていません")

# 既存生成ファイルを削除
for f in DEST.glob("test_*.py"):
    f.unlink()

# テストファイル共通ヘッダ
head = textwrap.dedent(f"""
import pytest
from playwright.sync_api import Page, expect

BASE_URL = '{base_url}'
""")

# slug 生成関数
def slug(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", path.strip("/")) or "root"

# --- ページごとにテスト関数を生成 ---------------------------------
for page in pages:
    path = page["path"]
    assertions = page.get("assertions", [])

    lines = [head]
    lines.append(f"def test_{slug(path)}(page: Page):")
    lines.append(f"    page.goto(BASE_URL + '{path}', wait_until='load')")

    for a in assertions:
        if a.startswith("status_code"):
            status = a.split(":", 1)[-1]
            lines.append(f"    assert page.response().status == {status}")

        elif a.startswith("no_js_errors"):
            # JS エラーは conftest の fixture で自動検知
            continue

        elif a.startswith("contains_text"):
            txt = a.split(":", 1)[-1].replace("'", "\'")
            lines.append(f"    expect(page).to_have_text('{txt}')")

        elif a.startswith("css:"):
            # 形式: css:<selector>:<cond>
            _, sel, cond = a.split(":", 2)
            if cond.startswith("contains_text"):
                txt = cond.split(":", 1)[-1].replace("'", "\'")
                lines.append(f"    expect(page.locator('{sel}')).to_have_text('{txt}')")
            else:
                lines.append(f"    assert page.locator('{sel}').count() > 0")

        elif a.startswith("click:"):
            sel = a.split(":", 1)[-1]
            lines.append(f"    page.locator('{sel}').first.click()")

    # テストファイル書き出し
    (DEST / f"test_{slug(path)}.py").write_text("".join(lines))

print(f"✅ {len(pages)} test file(s) generated → {DEST}")
"""python"""

#!/usr/bin/env python
"""generate_tests.py – v5.1  (YAML 専用ワンショット変換)

specs/tests.yml を読み込み、Playwright+pytest テストを
 tests/generated/test_<slug>.py として書き出します。
"""
import pathlib, yaml, re, textwrap, sys

SPEC = pathlib.Path("specs/tests.yml")
DEST = pathlib.Path("tests/generated")
DEST.mkdir(parents=True, exist_ok=True)

# --- 入力チェック ---
if not SPEC.exists():
    print("❌ specs/tests.yml が見つかりません。まず yaml_generator.py 等で作成してください")
    sys.exit(1)

spec = yaml.safe_load(SPEC.read_text())
base_url = spec["base_url"]
pages = spec.get("pages", [])
if not pages:
    print("⚠️  YAML に pages が定義されていません")
    sys.exit(1)

# 既存ファイル削除
for f in DEST.glob("test_*.py"):
    f.unlink()

# ヘッダ
head = textwrap.dedent(f"""
import pytest
from playwright.sync_api import Page, expect

BASE_URL = '{base_url}'
""")

# --- 変換 ---
slug = lambda p: re.sub(r'[^A-Za-z0-9]+', '_', p.strip('/')) or 'root'

for page in pages:
    path = page["path"]
    assertions = page.get("assertions", [])
    code = [head, f"def test_{slug(path)}(page: Page):", f"    page.goto(BASE_URL + '{path}', wait_until='load')"]
    for a in assertions:
        if a.startswith("status_code"):
            status = a.split(":")[-1]
            code.append(f"    assert page.response().status == {status}")
        elif a.startswith("no_js_errors"):
            pass  # fixture で検知
        elif a.startswith("contains_text"):
            txt = a.split(":", 1)[-1].replace("'", "\'")
            code.append(f"    expect(page).to_have_text('{txt}')")
        elif a.startswith("css:"):
            # css:#selector:assertion
            _, sel, cond = a.split(":", 2)
            if cond.startswith("contains_text"):
                txt = cond.split(":",1)[-1].replace("'","\'")
                code.append(f"    expect(page.locator('{sel}')).to_have_text('{txt}')")
            else:  # exists:true 等
                code.append(f"    assert page.locator('{sel}').count() > 0")
    (DEST / f"test_{slug(path)}.py").write_text("".join(code))

print(f"✅ {len(pages)} test(s) generated → {DEST}")