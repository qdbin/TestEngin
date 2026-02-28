FROM python:3.8

LABEL maintainer="qdbin"

COPY browser /qdbin/browser

COPY core /qdbin/core

COPY requirements.txt /qdbin/

COPY tools/ /qdbin/tools

COPY app/ /qdbin/app

COPY startup.py /qdbin/

WORKDIR /qdbin

RUN pip install -r requirements.txt -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

CMD ["python", "startup.py"]
