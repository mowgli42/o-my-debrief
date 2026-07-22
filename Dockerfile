FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
RUN pip install --no-cache-dir -e .
COPY data ./data
ENV DEBRIEF_DATA_DIR=/app/data/debrief
ENV DEBRIEF_RULES=/app/config/milestone-rules.yaml
EXPOSE 8020
CMD ["uvicorn", "omy_debrief.api.app:app", "--host", "0.0.0.0", "--port", "8020"]
