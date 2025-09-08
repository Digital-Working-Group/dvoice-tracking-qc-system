FROM continuumio/miniconda3
RUN conda create -y -n env python=3.13.1
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH
WORKDIR /scripts
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt