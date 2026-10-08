#!/usr/bin/env python3
import json
from pathlib import Path

md_path = Path("RESEARCH_APPROACH_NOTE.md")
html_path = Path("RESEARCH_APPROACH_NOTE.html")

md_content = md_path.read_text(encoding="utf-8")
escaped_md = json.dumps(md_content)

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>The One Introduction Problem: Research Approach Note</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    window.MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
      }
    };
  </script>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      line-height: 1.6;
      color: #24292e;
      max-width: 900px;
      margin: 40px auto;
      padding: 0 25px;
    }
    h1, h2, h3, h4 { color: #1a202c; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
    h1 { font-size: 2.2em; border-bottom: 2px solid #2b6cb0; }
    h2 { font-size: 1.6em; margin-top: 1.5em; }
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 1.5em 0;
    }
    th, td {
      border: 1px solid #cbd5e0;
      padding: 10px 14px;
      text-align: left;
    }
    th {
      background-color: #f7fafc;
      font-weight: 600;
    }
    tr:nth-child(even) { background-color: #f8fafc; }
    code {
      background-color: #edf2f7;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: Menlo, Monaco, Consolas, monospace;
      font-size: 0.9em;
    }
    pre {
      background-color: #2d3748;
      color: #f7fafc;
      padding: 16px;
      border-radius: 6px;
      overflow-x: auto;
    }
    pre code { background: none; color: inherit; padding: 0; }
    blockquote {
      border-left: 4px solid #4299e1;
      padding-left: 16px;
      color: #4a5568;
      margin: 1.5em 0;
    }
    .print-btn {
      position: fixed;
      top: 20px;
      right: 20px;
      background: #3182ce;
      color: white;
      border: none;
      padding: 10px 18px;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    @media print {
      .print-btn { display: none; }
      body { margin: 0; padding: 0; max-width: 100%; }
    }
  </style>
</head>
<body>
  <button class="print-btn" onclick="window.print()">🖨️ Save as PDF</button>
  <div id="content"></div>
  <script>
    const markdown = __MARKDOWN_PLACEHOLDER__;
    document.getElementById('content').innerHTML = marked.parse(markdown);
  </script>
</body>
</html>
"""

html_out = html_template.replace("__MARKDOWN_PLACEHOLDER__", escaped_md)
html_path.write_text(html_out, encoding="utf-8")
print(f"Generated printable HTML note -> {html_path.absolute()}")
