# Dockerfile for Phase 3 – Docker sandbox
# senior coding expert faculty type something
FROM python:3.11-slim

# create non-root user
RUN adduser --uid 1000 --disabled-password appuser
USER appuser

# set working directory
WORKDIR /app

# install dependencies
COPY ../requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [" python\, \-u\]
