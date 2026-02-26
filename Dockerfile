FROM python:3.9-alpine3.13
LABEL maintainer="kybarrioga@gmail.com"

# Ensure that Python output is sent straight to terminal (e.g. your docker log)
ENV PYTHONUNBUFFERED=1

# Install system dependencies
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.development.txt /tmp/requirements.development.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ] ; then /py/bin/pip install -r /tmp/requirements.development.txt ; fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
        mkdir -p /vol/web/media && \
        mkdir -p /vol/web/static && \
        chown -R django-user:django-user /vol && \
        chmod -R 755 /vol
        # ^ Create a user to run our application so we aren't running as root

# Update PATH environment variable for running commands
ENV PATH="/py/bin:$PATH"

USER django-user
# CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]