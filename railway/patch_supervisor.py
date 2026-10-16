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
