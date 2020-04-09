FROM python:3.6-slim

ENV AWS_ACCESS_KEY_ID=<<YOUR AWS_ACCESS_KEY_ID>>
ENV AWS_SECRET_ACCESS_KEY=<<YOUR AWS_SECRET_ACCESS_KEY>>
ENV AWS_DEFAULT_REGION=us-east-1

WORKDIR /workspace
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN chalice new-project image-classification
COPY ./image-classification /workspace/image-classification
WORKDIR /workspace/image-classification
RUN chalice deploy
