# pull official base image
FROM python:3.11.4-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

# Create a user with UID 1000 and GID 1000
RUN groupadd -g 1000 appgroup && \
    useradd -r -u 1000 -g appgroup appuser
# Switch to this user
USER 1000:1000
