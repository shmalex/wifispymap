import datetime as dt
import json
import multiprocessing
import os
import pickle
import queue as q
import string
import time
import zlib
import sys
from multiprocessing import Array, Manager, Process

import pandas as pd
from flask import Flask, render_template, request

import dal
from dal import DAL
import devices_names as devs
from repo import ModelRepository

conf_mac = os.environ['SHWM_DEFAULT_MAC']
conf_lat = os.environ['SHWM_LAT']
conf_lon = os.environ['SHWM_LON']

print(os.environ['SHWM_DB_PATH'])


#conf_mac = os.environ['DEFAULT_MAX']

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', **{'lat': conf_lat,
                                            'lon': conf_lon})


@app.route('/range')
def range():
    try:
        tdfrom = request.args.get('from', default=dt.datetime.isoformat(
            dt.datetime.now()-dt.timedelta(minutes=60)), type=str)
        tdto = request.args.get(
            'to', default=dt.datetime.isoformat(dt.datetime.now()), type=str)
        macs = request.args.get('macs', default='', type=str)

        print(tdfrom, tdto)
        cach_key = '-'.join([macs, tdfrom, tdto])

        if cach_key in app._activity:
            ret = ''.join([chr(c) for c in app._activity[cach_key]])
            print('return from cache', cach_key, len(ret))
            return ret

        if (len(macs) > 0):
            ar_macs = macs.split(',')
            if len(ar_macs) == 1:
                pas = repository.get_from_range_by_mac(
                    ar_macs[0], tdfrom, tdto)
        else:
            pas = repository.get_from_range(tdfrom, tdto)
        print(len(pas))
        main_data = json.dumps(
            [{'ne': o.ne, 'mac': o.apa}for o in pas])
        app._activity[cach_key] = [ord(c) for c in main_data]
        return main_data
    except KeyboardInterrupt:
        return'[]'
    except Exception as ex:
        print(ex)
        return'[]'


@app.route('/devices')
def devices():
    try:
        date = request.args.get(
            'date', default=dt.datetime.now().isoformat(), type=str)

        dt_from = date+'T00:00:00.867282'
        dt_to = date + 'T23:59:59.999999'
        pas = repository.get_devices_from_range(dt_from, dt_to)
        print('returned', len(pas))
        return json.dumps(
            [{'ne': o.ne, 'mac': o.mac, 'name': devs.device_name(o.mac)}for o in pas])
    except KeyboardInterrupt:
        return'[]'
    except Exception as ex:
        print(ex)
        return'[]'


@app.route('/activity')
def search():
    try:
        mac = request.args.get('mac', default=conf_mac, type=str)
        last_min = request.args.get('t', default=90, type=int)
        app._activity['target'] = mac
        app._activity['last_min'] = last_min
        data = app._activity[mac+'-'+str(last_min)]
        ret = ''.join([chr(c) for c in data])

        print('returned', len(ret))
        return ret
    except KeyboardInterrupt:
        return'[]'
    except Exception:
        return'[]'


def data_fetcher():
    def rotate(stop):
        while not stop.is_set():
            try:
                mac = conf_mac
                if 'target' in app._activity:
                    if (len(app._activity['target']) == len(conf_mac)) | (app._activity['target'] == 'any'):
                        mac = app._activity['target']

                last_min = 90
                if 'last_min' in app._activity:
                    if app._activity['last_min'] > 0:
                        last_min = app._activity['last_min']
                print('read', mac, last_min)
                pas = repository.get_power_activity(mac, last_min=last_min)
                main_data = json.dumps(
                    [{'ne': o.ne, 'mac': o.apa}for o in pas])

                app._activity[mac+'-'+str(last_min)] = [ord(c)
                                                        for c in main_data]

                time.sleep(1)
            except KeyboardInterrupt:
                stop.set()
    stop = multiprocessing.Event()
    multiprocessing.Process(target=rotate, args=[stop]).start()
    return stop


if __name__ == '__main__':
    repository = ModelRepository()
    mgr = Manager()
    app._activity = mgr.dict()
    stop = data_fetcher()
    try:
        app.run(host='0.0.0.0', debug=True)
    except KeyboardInterrupt:
        sys.exit()
    finally:
        stop.set()
    print('done')
