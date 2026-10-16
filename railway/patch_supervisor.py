"""Narrow compatibility shim: Railway owns PID 1, s6 still supervises its children.

Keep the upstream manager and lifecycle implementation; recognize our live s6
child in addition to upstream's PID-1-only detection. Fail the build on drift.
"""
from pathlib import Path

path = Path('/opt/hermes/hermes_cli/service_manager.py')
source = path.read_text()
needle = '    return comm == "s6-svscan" and Path("/run/s6/basedir").is_dir()'
replacement = '''    if Path("/run/hermes-railway/s6.pid").exists():
        try:
            pid = int(Path("/run/hermes-railway/s6.pid").read_text())
            return (pid > 1
                    and Path(f"/proc/{pid}/comm").read_text().strip() == "s6-svscan"
                    and Path("/run/service/.s6-svscan/control").exists())
        except (OSError, ValueError):
            return False
    return comm == "s6-svscan" and Path("/run/s6/basedir").is_dir()'''
assert source.count(needle) == 1, 'Hermes service-manager changed; review the Railway shim'
path.write_text(source.replace(needle, replacement))

# Railway terminates HTTPS before the container. Keep upstream's bounded
# proxy trust, while making its cookie helpers honor this HTTPS-only stack.
# Never trust a client-supplied forwarded header to decide cookie security.
path = Path('/opt/hermes/hermes_cli/dashboard_auth/cookies.py')
source = path.read_text()
needle = '    return request.url.scheme == "https"'
assert source.count(needle) == 1, 'Hermes cookie helper changed; review HTTPS integration'
if '\nimport os\n' not in source:
    source = source.replace('\nimport json\n', '\nimport json\nimport os\n', 1)
    assert '\nimport os\n' in source
replacement = ('    return (request.url.scheme == "https"\n'
               '            or os.environ.get("HERMES_RAILWAY_HTTPS") == "1")')
path.write_text(source.replace(needle, replacement))
