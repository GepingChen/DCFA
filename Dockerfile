FROM python:3.11-slim@sha256:90744cff8f32887f075c47d747a173ff333e9e98801667af93c357fa9f5e28ff

ARG DCFA_BUILD_REVISION=unknown

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib \
    DCFA_SERVER_NAME=0.0.0.0 \
    DCFA_OUTPUT_ROOT=/app/artifacts/local/website-demo \
    DCFA_GEMINI_API_KEY_FILE=/run/secrets/gemini_api_key \
    DCFA_WEBSITE_GEMINI_CONFIG_FILE=/app/evaluation/configs/website_demo_gemini_v1.json \
    DCFA_BUILD_REVISION=${DCFA_BUILD_REVISION} \
    PORT=7860

WORKDIR /app

COPY requirements-website-demo.lock pyproject.toml README.md ./
RUN python -m pip install --no-cache-dir -r requirements-website-demo.lock

COPY evaluation/configs/website_demo_gemini_v1.json ./evaluation/configs/website_demo_gemini_v1.json
COPY src ./src
RUN python -m pip install --no-cache-dir . --no-deps \
    && useradd --create-home --uid 10001 dcfa \
    && mkdir -p /app/artifacts/local/website-demo /tmp/matplotlib \
    && chown -R dcfa:dcfa /app/artifacts /tmp/matplotlib

USER 10001:10001

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/readyz', timeout=2).read()"

CMD ["dcfa-website-demo"]
