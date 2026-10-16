#!/bin/sh
set -eu
export PATH="/command:/package/admin/s6/command:${PATH}"
# Preserve official permission repair, browser paths, SQLite, skills and API key seed.
/opt/hermes/docker/stage2-hook.sh
# with-contenv is a no-op in the wrapped-runtime supervisor. Carry the
# official stage2 browser-path selection into the inherited environment.
if [ -z "${AGENT_BROWSER_EXECUTABLE_PATH:-}" ] && [ -f /etc/hermes/agent-browser-executable-path ]; then
    AGENT_BROWSER_EXECUTABLE_PATH="$(cat /etc/hermes/agent-browser-executable-path)"
    export AGENT_BROWSER_EXECUTABLE_PATH
fi
mkdir -p /run/service /run/hermes-railway /opt/data/workspace
chown hermes:hermes /run/service /run/hermes-railway /opt/data/workspace
exec /command/s6-setuidgid hermes /opt/hermes/.venv/bin/python /opt/railway/supervise.py
