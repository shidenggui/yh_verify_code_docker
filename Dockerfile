FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
	tesseract-ocr-chi-sim \
	python-pip

COPY digits /usr/share/tesseract-ocr/tessdata/configs/digits

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt 
COPY app.py /app.py
CMD gunicorn -w 4 -k gevent app:app -b 0.0.0.0:5000
