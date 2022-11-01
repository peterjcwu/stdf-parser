FROM continuumio/anaconda3
COPY ./ /opt/src/stdfparser
WORKDIR /opt/src/stdfparser
RUN pip install --upgrade --quiet pip && \
    pip install --no-cache-dir --quiet . && \
    pip install -r requirements.txt --quiet && \
    conda install -y --quiet jupyter jupyterlab
EXPOSE 8888

