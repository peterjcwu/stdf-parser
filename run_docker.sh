docker run -i -t -p 8888:8888 v11-sweep:0.3 /bin/bash -c "\
    mkdir -p /opt/notebooks && \
    jupyter notebook \
    --notebook-dir=/opt/notebooks --ip='*' --port=8888 \
    --no-browser --allow-root"
