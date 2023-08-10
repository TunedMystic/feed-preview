FROM python:3.11.4-alpine3.18 as base


#
#
# ------------------ Stage 1 --------------------
# Install application + system dependencies.
# -----------------------------------------------
#
#

FROM base AS stage-one

ARG ENVIRONMENT

ENV LANG=C.UTF-8 \
    PATH=/opt/local/bin:$PATH \
    PIP_PREFIX=/opt/local \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .

RUN if [ "$ENVIRONMENT" = "dev" ]; then \
        pip install $(sed 's/# dev //g' requirements.txt | tr '\n' ' '); \
    else \
        pip install -r requirements.txt; \
    fi;


#
#
# ------------------------- Stage 2 ---------------------------------
# Copy project source. Copy installed dependencies from Stage 1.
# -------------------------------------------------------------------
#
#

FROM base AS stage-two

RUN apk add --no-cache bash

# Copy requirements from builder image
COPY --from=stage-one /opt/local /opt/local

ENV LANG=C.UTF-8 \
    PATH=/opt/local/bin:$PATH \
    PYTHONPATH=/opt/local/lib/python3.11/site-packages:/x/app \
    PYTHONUNBUFFERED=1

WORKDIR /x

COPY . /x

EXPOSE 8000

STOPSIGNAL SIGINT

CMD ["waitress-serve", "--port=8000", "--threads=1", "--channel-timeout=0", "app.main:app"]
