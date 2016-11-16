FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
	tesseract-ocr-chi-sim \
	python-pip

COPY digits /usr/share/tesseract-ocr/tessdata/configs/digits

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
COPY app.py /app.py
CMD python app.py
