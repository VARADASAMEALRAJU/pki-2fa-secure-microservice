FROM python:3.11-slim
ENV TZ=UTC
WORKDIR /app
RUN apt-get update && apt-get install -y cron tzdata && rm -rf /var/lib/apt/lists/*
COPY app /app
COPY scripts /app/scripts
COPY cron/2fa-cron /etc/cron.d/2fa-cron
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem
RUN mkdir -p /data /cron && chmod 755 /data /cron
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron
EXPOSE 8080
CMD cron && uvicorn app.main:app --host 0.0.0.0 --port 8080
