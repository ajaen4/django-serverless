# pull official base image
FROM python:3.11.4-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    awscli \
    jq \
    gdal-bin \
    binutils \
    libproj-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY . app/
WORKDIR /app

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Create a user with UID 1000 and GID 1000
RUN groupadd -g 1000 appgroup && \
    useradd -r -u 1000 -g appgroup appuser

# Change ownership of the /app directory to appuser:appgroup
RUN chown -R appuser:appgroup /app

# Create the staticfiles directory and set permissions before switching to the user
RUN mkdir -p staticfiles && \
    chown -R appuser:appgroup staticfiles

# Switch to the non-root user
USER 1000:1000

ENTRYPOINT ["./entrypoint.sh"]
