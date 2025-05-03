
#!/usr/bin/env bash
set -e
pytest -q --html=reports/report.html --self-contained-html
echo "✅ Report: reports/report.html"
