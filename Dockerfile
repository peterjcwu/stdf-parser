FROM continuumio/anaconda3
COPY ./ /opt/src/stdfparser
WORKDIR /opt/src/stdfparser
RUN pip install --upgrade --quiet pip && \
    pip install --no-cache-dir --quiet . && \
    pip install -r requirements.txt --quiet && \
    pip install --no-cache-dir --quiet lets-plot && \
    conda install -y --quiet jupyter jupyterlab
EXPOSE 8888
CMD ["jupyter", "lab", "--notebook-dir=/opt/src/stdfparser/lab", "--ip=0.0.0.0", "--no-browser", "--allow-root" ]
