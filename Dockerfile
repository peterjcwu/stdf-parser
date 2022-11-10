FROM continuumio/anaconda3
COPY ./ /opt/src/stdfparser
WORKDIR /opt/src/stdfparser
RUN pip install --upgrade --quiet pip && \
    pip install --no-cache-dir --quiet . && \
    pip install -r requirements.txt --quiet && \
    pip install --no-cache-dir --quiet lets-plot && \
    conda install -y --quiet jupyter jupyterlab
EXPOSE 8888
COPY ./lab/ /opt/lab
CMD ["jupyter", "lab",  "--notebook-dir=/opt/lab", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--NotebookApp.password='argon2:$argon2id$v=19$m=10240,t=10,p=8$3zxXNvq86tCUywRjvjE+DQ$2i8M0IiSf/p/CbL6diM1jA'"]
