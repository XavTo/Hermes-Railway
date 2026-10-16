"""Run the official s6 per-profile manager underneath Railway's init."""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, '/opt/hermes')
from hermes_cli.config import load_config, save_config, save_env_value

home = Path('/opt/data')
# Native tool subprocesses intentionally scrub web-provider settings from
# their inherited environment. Persist this one connection through Hermes's
# supported env store so the provider and diagnostics can resolve it there.
if os.environ.get('SEARXNG_URL'):
    save_env_value('SEARXNG_URL', os.environ['SEARXNG_URL'])
marker = home / '.railway-research-seeded-v1'
if not marker.exists():
    cfg = load_config()
    cfg.setdefault('web', {}).update(search_backend='searxng', extract_backend='native',
                                    keyless_fallback=False, keyless_rescue=False)
    cfg.setdefault('browser', {}).update(backend='off', cloud_provider='local', engine='chrome')
    save_config(cfg)
    skill = home / 'skills' / 'research' / 'railway-research'
    skill.mkdir(parents=True, exist_ok=True)
    (skill / 'SKILL.md').write_text(Path('/opt/railway/research-skill.md').read_text())
    marker.write_text('Seeded once. User configuration is preserved on restart.\n')

assert os.environ.get('HERMES_DASHBOARD_BASIC_AUTH_PASSWORD'), 'Dashboard password is required'
assert os.environ.get('HERMES_DASHBOARD_BASIC_AUTH_SECRET'), 'Stable dashboard signing secret is required'
assert os.environ.get('HERMES_DASHBOARD_PUBLIC_URL', '').startswith('https://'), 'Set the public HTTPS URL'

service = Path('/run/service/railway-dashboard')
service.mkdir(exist_ok=True)
run = service / 'run'
run.write_text('#!/bin/sh\ncd /opt/data/workspace\nexec /opt/hermes/.venv/bin/hermes dashboard '
               '--host 0.0.0.0 --port "${PORT:-8080}" --no-open\n')
run.chmod(0o700)
scanner = subprocess.Popen(['/command/s6-svscan', '/run/service'])
Path('/run/hermes-railway/s6.pid').write_text(str(scanner.pid))
stopping = False

def stop(signum, frame):
    global stopping
    stopping = True
    # -t terminates all supervised processes and waits for them.
    subprocess.run(['/command/s6-svscanctl', '-t', '/run/service'], check=False)

signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
try:
    for _ in range(100):
        if Path('/run/service/.s6-svscan/control').exists():
            break
        if scanner.poll() is not None:
            raise RuntimeError('s6 exited during initialization')
        time.sleep(0.1)
    subprocess.run(['/opt/hermes/.venv/bin/python', '-m', 'hermes_cli.container_boot'],
                   check=True, cwd='/opt/hermes')
    # The official reconciler normally runs before the scanner's first pass.
    # Here the scanner is already live, so explicitly discover its new slots.
    subprocess.run(['/command/s6-svscanctl', '-a', '/run/service'], check=True)
    print('[railway] s6 gateway supervision and authenticated dashboard initialized', flush=True)
    rc = scanner.wait()
finally:
    if scanner.poll() is None:
        stop(None, None)
        try:
            scanner.wait(timeout=25)
        except subprocess.TimeoutExpired:
            scanner.kill()
sys.exit(0 if stopping else (rc or 1))
