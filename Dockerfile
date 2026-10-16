FROM nousresearch/hermes-agent:v0.22.2@sha256:36099926da316742423544e055d4734777105ffe6341873af5459b957d0c2919
USER root
COPY railway /opt/railway
COPY plugins/railway_local /opt/hermes/plugins/web/railway_local
RUN /opt/hermes/.venv/bin/python /opt/railway/patch_supervisor.py \
    && chmod +x /opt/railway/entrypoint.sh /opt/railway/doctor.py \
    && ln -s /opt/railway/doctor.py /usr/local/bin/hermes-railway-doctor
ENV S6_KEEP_ENV=1 HERMES_GATEWAY_BOOTSTRAP_STATE=running HERMES_RAILWAY_HTTPS=1 \
    HERMES_HOME=/opt/data HOME=/opt/data HERMES_DASHBOARD_HOST=0.0.0.0 \
    TERMINAL_CWD=/opt/data/workspace PYTHONUNBUFFERED=1
WORKDIR /opt/hermes
EXPOSE 8080
ENTRYPOINT ["/opt/railway/entrypoint.sh"]
CMD []
