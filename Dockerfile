# syntax = docker/dockerfile:1.4
ARG AIRFLOW_VERSION=2.7.2

FROM docker.io/apache/airflow:${AIRFLOW_VERSION} as airflow-production

COPY ./requirements.txt /opts/requirements.txt

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /opts/requirements.txt
