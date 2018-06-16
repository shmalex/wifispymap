import datetime as dt
import os
import pickle
import sqlite3
from urllib.parse import urlparse

import numpy as np
import pandas as pd

from dal import DAL
from entity import Activity, DevicesActivity, PowerActivity


class ModelRepository(object):
    def __init__(self):
        self.__get_last_activitiy = ''' select timestamp dt, source_address src, destination_address dst, access_point_address apa, access_point_name apn 
        from packets 
        where timestamp > ? and 
        (source_address = ? or destination_address = ?)'''
        self.__get_power_activitiy_any = '''
            select count(*) ne, access_point_address apa
            from packets 
                    where timestamp > ?
            and not (source_address == access_point_address and destination_address == 'ff:ff:ff:ff:ff:ff')
            and not (source_address in (select mac from apas ) and destination_address in (select mac from apas ) )
            group by access_point_address  '''
        self.__get_power_activitiy = '''
            select count(*) ne, access_point_address apa
            from packets 
                    where timestamp > ? and 
                    (source_address = ? or destination_address = ?)
            group by access_point_address  '''
        self.__get_range_all = ''' select count(*) ne, access_point_address apa
            from packets where timestamp >= ? and timestamp <= ?
            and not (source_address == access_point_address and destination_address == 'ff:ff:ff:ff:ff:ff')
            group by access_point_address'''

        self.__get_range_by_mac = ''' select count(*) ne, access_point_address apa
            from packets where (timestamp >= ? and timestamp <= ?) and 
            (source_address = ? or destination_address = ?)
            and not (source_address == access_point_address and destination_address == 'ff:ff:ff:ff:ff:ff')
            group by access_point_address'''
        self.__get_devices_date = ''' select  en, mac from devices_date where en > 100'''  # where (dt >= ? and dt <= ?)  '''
        self.__get_devices = '''select count(*) en, source_address src, destination_address dst from packets 
        where (timestamp >= ? and timestamp <= ?)
        and not (source_address == access_point_address and destination_address == 'ff:ff:ff:ff:ff:ff')
        and ((source_address not in (select distinct access_point_address from packets)) or (destination_address not in (select distinct access_point_address from packets)))
        group by source_address, destination_address 
        order by 1 desc '''
        self.conn = DAL.get_lite_connection()

    def _execute_one(self, sql, targs=None, commit=False):
        try:
            self.conn = sqlite3.connect(os.environ['SHWM_DB_PATH'])
            cur = self.conn.cursor()
            if (targs == None):
                cur.execute(sql)
            else:
                cur.execute(sql, targs)
            row = cur.fetchone()
            if (commit):
                self.conn.commit()

            cur.close()
            if commit:
                return row[0]
            return row
        except Exception as err:
            print('Exception:', err)
            print('Exception:', sql)
            if (targs != None):
                print('Exception:', targs)
            return None

    def _execute_rows(self, sql, targs=None, commit=False):
        try:
            self.conn = sqlite3.connect(os.environ['SHWM_DB_PATH'])

            cur = self.conn.cursor()
            if (targs == None):
                cur.execute(sql)
            else:
                cur.execute(sql, targs)
            rows = cur.fetchall()

            cur.close()
            return rows
        except Exception as err:
            print('Exception:', err)
            print('Exception:', sql)
            if (targs != None):
                print('Exception:', targs)
            return None

    def get_power_activity(self, mac, last_min=1):
        assert len(mac) > 0

        if mac == 'any':
            ts = dt.datetime.isoformat(
                dt.datetime.now()-dt.timedelta(minutes=last_min))
            rows = self._execute_rows(self.__get_power_activitiy_any, (ts,))
        else:
            ts = dt.datetime.isoformat(
                dt.datetime.now()-dt.timedelta(minutes=last_min))
            rows = self._execute_rows(
                self.__get_power_activitiy, (ts, mac, mac))

        if rows is None:
            return None
        return [PowerActivity.from_row(row) for row in rows]

    def get_devices_from_range(self, dtfrom, dtto):
        rows = self._execute_rows(
            self.__get_devices_date)  # , (dtfrom, dtto))

        if rows is None:
            return None
        return [DevicesActivity.from_row(row) for row in rows]

    def get_from_range_by_mac(self, mac, dtfrom, dtto):
        rows = self._execute_rows(
            self.__get_range_by_mac, (dtfrom, dtto, mac, mac))

        if rows is None:
            return None
        return [PowerActivity.from_row(row) for row in rows]

    def get_from_range(self, dtfrom, dtto):
        rows = self._execute_rows(self.__get_range_all, (dtfrom, dtto))

        if rows is None:
            return None
        return [PowerActivity.from_row(row) for row in rows]

    def get_last_activity(self, mac, last_min=1):
        assert len(mac) > 0

        ts = dt.datetime.isoformat(
            dt.datetime.now() - dt.timedelta(minutes=last_min))

        rows = self._execute_rows(self.__get_last_activitiy, (ts, mac, mac))

        if rows is None:
            return None
        [Activity.from_row(row) for row in rows]
