#!/opt/hermes/.venv/bin/python
"""Fixed-scope stack diagnostics. Never prints provider credentials."""
import argparse
import asyncio
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/hermes')
from hermes_cli.config import load_config
from hermes_cli.service_manager import detect_service_manager

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--search', action='store_true', help='Run a public example search and page extraction')
parser.add_argument('--browser', action='store_true', help='Open example.com in the local browser and read its title')
args = parser.parse_args()
cfg = load_config()
out = {
    'uid': os.geteuid(), 'supervisor': detect_service_manager(),
    'sqlite': sqlite3.sqlite_version,
    'persistentWorkspace': Path('/opt/data/workspace').is_dir(),
    'searchBackend': cfg.get('web', {}).get('search_backend'),
    'extractBackend': cfg.get('web', {}).get('extract_backend'),
    'browserProvider': cfg.get('browser', {}).get('cloud_provider'),
    'browserEngine': cfg.get('browser', {}).get('engine'),
    'researchSkill': Path('/opt/data/skills/research/railway-research/SKILL.md').is_file(),
}
for name, command in [('git', ['git', '--version']), ('node', ['node', '--version']),
                      ('gatewaySupervisor', ['/command/s6-svstat', '/run/service/gateway-default'])]:
    r = subprocess.run(command, capture_output=True, text=True, timeout=10)
    out[name] = {'ok': r.returncode == 0, 'output': r.stdout.strip()}
if args.search:
    from tools.web_tools import web_search_tool, web_extract_tool
    result = json.loads(web_search_tool('Railway persistent volumes documentation', limit=3))
    rows = (result.get('data') or {}).get('web') or []
    out['search'] = {'ok': result.get('success') is True and bool(rows), 'resultCount': len(rows),
                     'urls': [row.get('url') for row in rows]}
    extracted = json.loads(asyncio.run(web_extract_tool(['https://example.com'], char_limit=1500)))
    pages = extracted.get('results') or []
    out['extraction'] = {'ok': bool(pages) and all(not page.get('error') for page in pages),
                         'containsExampleDomain': 'Example Domain' in json.dumps(extracted),
                         'errors': [page['error'] for page in pages if page.get('error')] or extracted.get('error')}
if args.browser:
    from tools.browser_tool import browser_navigate, browser_console
    task = 'railway-stack-diagnostics'
    nav = json.loads(browser_navigate('https://example.com', task_id=task))
    evaluated = json.loads(browser_console(expression='document.title', task_id=task))
    out['browser'] = {'ok': nav.get('success') is True and evaluated.get('success') is True,
                      'title': evaluated.get('result'), 'navigationError': nav.get('error'),
                      'evaluationError': evaluated.get('error')}
    from tools.browser_tool_lifecycle import _cleanup_single_browser_session
    _cleanup_single_browser_session(task)
print(json.dumps(out, ensure_ascii=False))
