
FROM continuumio/miniconda3

WORKDIR /app

COPY . /app

COPY usrfile.txt /usr
COPY sensitive_info_root.txt /root


ARG is_OCI=false


RUN echo "is_OCI is set to ${is_OCI}"


RUN conda init bash


RUN chmod +x init.sh
RUN apt-get update -y
RUN apt-get install -y xxd wget curl

RUN pip install flask
RUN pip install requests
RUN pip install pyyaml
RUN pip install jsonpickle
RUN pip install psutil
RUN pip install pyperclip
RUN pip install pillow
RUN pip install watchdog
RUN chmod +x start_processes.sh

RUN if [ "$is_OCI" = "true" ]; then \
    echo "is_OCI is true"; \
    cp /app/environment.yml /app; \
    ls -l /app; \
    cat /app/environment.yml; \
    conda env create -f /app/environment.yml --verbose; \
    fi

ENTRYPOINT ["/app/init.sh"]
