# coding:utf8
import re
import os
import time
import datetime
from argparse import ArgumentParser

import pytesseract
from PIL import Image
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/yh', methods=['POST'])
def yh():
    image = request.files['image']
    image = Image.open(image)
    image = remove_noise(image)
    code = pytesseract.image_to_string(
        image, lang='chi_sim', config='-psm 7 digits')
    return map_numbers(code)


@app.route('/yh_client', methods=['POST'])
def yh_client():
    start = time.time()
    image = request.files['image']
    image = Image.open(image)
    code = pytesseract.image_to_string(image, config='-psm 7')
    use_time = time.time() - start()
    try:
        write_to_influxdb(use_time)
    except:
        pass
    return jsonify({'result': code}), 201


def write_to_influxdb(use_time):
    if os.getenv('INFLUXDB_MONITOR') is None:
        return
    from influxdb import InfluxDBClient
    client = InfluxDBClient(
        os.getenv('INFLUXDB_HOST'),
        port=os.getenv('INFLUXDB_PORT'),
        username=os.getenv('INFLUXDB_USER'),
        password=os.getenv('INFLUXDB_PASSWORD'),
        database=os.getenv('INFLUXDB_DB'))
    json_body = [{
        "measurement": "yh_verify",
        "tags": {
            "host": request.remote_addr,
        },
        "time": str(datetime.datetime.now()),
        "fields": {
            "use_time": use_time
        }
    }]
    client.write_points(json_body)


def remove_noise(image):
    width, height = image.size
    for x in range(width):
        for y in range(height):
            if image.getpixel((x, y)) > (150, 150, 150):
                image.putpixel((x, y), (256, 256, 256))
    return image.convert('L')


def map_numbers(code):
    valid_chars = re.findall('[〇一二三四五六七八九零壹贰叁肆伍陆柒捌玖]'.decode('utf8'),
                             code.decode('utf8'), re.IGNORECASE)
    label_map = {
        u'〇': u'0',
        u'一': u'1',
        u'二': u'2',
        u'三': u'3',
        u'四': u'4',
        u'五': u'5',
        u'六': u'6',
        u'七': u'7',
        u'八': u'8',
        u'九': u'9',
        u'零': u'0',
        u'壹': u'1',
        u'贰': u'2',
        u'叁': u'3',
        u'肆': u'4',
        u'伍': u'5',
        u'陆': u'6',
        u'柒': u'7',
        u'捌': u'8',
        u'玖': u'9'
    }
    v_c = []
    for e in valid_chars:
        v_c.append(label_map[e])
    return ''.join(v_c)


if __name__ == '__main__':
    opt = ArgumentParser()
    opt.add_argument('--model', default='gevent')
    args = opt.parse_args()
    if args.model == 'gevent':
        from gevent.wsgi import WSGIServer

        http_server = WSGIServer(('0.0.0.0', 5000), app)
        print('listen on 0.0.0.0:5000')
        http_server.serve_forever()
    elif args.model == 'raw':
        app.run(host='0.0.0.0')
