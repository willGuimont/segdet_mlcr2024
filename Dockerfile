ARG PYTORCH="2.2.1"
ARG CUDA="12.1"
ARG CUDNN="8"

FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel

RUN apt-get update \
    && apt-get install -y ffmpeg libsm6 libxext6 git ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip
RUN pip install openmim
#RUN mim install mmcv==2.1.0
#RUN mim install mmdet==3.3.0

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN python -m pip install -r /app/requirements.txt
ENV PYTHONPATH=/app:$PYTHONPATH
