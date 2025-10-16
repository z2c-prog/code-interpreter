FROM python:3.11-slim

ENV PIP_TRUSTED_HOST="Your artifact host"
ARG PIP_INDEX_URL

ENV PIP_INDEX_URL="${PIP_INDEX_URL}/xxxx"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR sandbox

#Switch to non-root user
#USER sandbox

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONHASHSEED=random
ENV PIP_NO_CAHCE_DIR=1
ENV PIP_DISABL_PIP_VERSION_CHECK=1


cmd ["python"]