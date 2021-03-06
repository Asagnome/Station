import sys
import datetime
import Adafruit_DHT

sensorNumber = 22
port = 4

def get(data=None):
    humidity, temperature = Adafruit_DHT.read_retry(sensorNumber, port)
    date = str(datetime.datetime.now())
    return [{
        "type": 'temperature',
        "value": temperature,
        "date": date
    }, {
        "type": 'humidity',
        "value": humidity,
        "date": date
    }]