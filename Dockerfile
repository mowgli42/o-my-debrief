FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e .
COPY data ./data
ENV DEBRIEF_DATA_DIR=/app/data/debrief
EXPOSE 8020
CMD ["uvicorn", "omy_debrief.api.app:app", "--host", "0.0.0.0", "--port", "8020"]
