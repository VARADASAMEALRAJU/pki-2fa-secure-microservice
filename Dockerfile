# ---------- Stage 1: builder ----------
FROM python:3.11-slim AS builder
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install build deps only in builder
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential libffi-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install into prefix (/install) to copy later
COPY app/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefix=/install -r /app/requirements.txt

# Copy only source to keep layer small (we will copy to runtime)
COPY app /app/app
COPY scripts /app/scripts
COPY cron/2fa-cron /app/cron-2fa-cron

# ---------- Stage 2: runtime ----------
FROM python:3.11-slim
ENV TZ=UTC
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install runtime system packages (cron + tzdata)
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    # set timezone to UTC (ensure tzdata configured)
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder to runtime
COPY --from=builder /install /usr/local

# Copy application code and scripts
COPY --from=builder /app/app /app/app
COPY --from=builder /app/scripts /app/scripts
# copy cron file into correct location and ensure LF preserved by .gitattributes on host
COPY --from=builder /app/cron-2fa-cron /etc/cron.d/2fa-cron

# Copy key files (must be present in repo root; docker-compose mounts will also make them available)
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem

# Create persistent dirs and set permissions
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Install cron job (permissions 0644)
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron

# Expose API port
EXPOSE 8080

# Start cron and uvicorn (FastAPI)
CMD cron && uvicorn app.main:app --host 0.0.0.0 --port 8080
