# ---- Base Image ----
FROM python:3.11-slim

# ---- Work Directory ----
WORKDIR /app

# ---- Environment Variables ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- System Dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl && \
    rm -rf /var/lib/apt/lists/*

# ---- Install Python Packages ----
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- Copy Application ----
COPY ./app /app

# ---- Expose Port ----
EXPOSE 8000

# ---- Command ----
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
