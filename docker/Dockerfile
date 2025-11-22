
# ---- builder ----
FROM python:3.11-slim AS builder
ARG PIP_EXTRA_INDEX_URL=""
WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip wheel --no-cache-dir --no-deps -w /wheels -r requirements.txt

# ---- runtime ----
FROM python:3.11-slim
WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

RUN mkdir -p /app/uploads /var/log/calorie_tracker \
 && chown -R appuser:appgroup /app /app/uploads /var/log/calorie_tracker

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

COPY . /app
RUN chown -R appuser:appgroup /app

USER appuser
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--workers", "4", "--bind", "0.0.0.0:8000", "app.main:app"]
