import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))
from triage import assess_issue, assess_pr

print("=== BAD ISSUE ===")
print(assess_issue("it broke", "help it does not work").to_markdown())
print("\n=== GOOD ISSUE ===")
good = "Steps to reproduce: run demo.py\nExpected: ok\nActual: error: Traceback (most recent call last)\nVersion: 1.2.3 OS: Ubuntu Python 3.12\n```python\nimport demo\n```"
print(assess_issue("Bug in demo", good).to_markdown())
print("\n=== PR WITHOUT TESTS ===")
print(assess_pr("stuff", "wip", ["src/a.py"]).to_markdown())
