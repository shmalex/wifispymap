import datetime
import os
from urllib.parse import urlparse

#import src.db as db


def object_build(fields, arow, instance):
    for field, val in zip(fields, arow):
        instance.__setattr__(field, val)
    return instance


class DevicesActivity(object):
    def __init__(self):
        self.ne = None
        self.mac = None

    @staticmethod
    def from_row(row):
        ret = DevicesActivity()
        ret = object_build(['ne', 'mac'], row, ret)
        return ret


class PowerActivity(object):
    def __init__(self):
        self.ne = None
        self.apa = None

    @staticmethod
    def from_row(row):
        ret = PowerActivity()
        ret = object_build(['ne', 'apa'], row, ret)
        return ret


class Activity(object):
    def __init__(self):
        self.dt = None
        self.src = None
        self.dst = None
        self.apa = None
        self.apn = None

    @staticmethod
    def from_row(row):
        ret = Activity()
        ret = object_build(['dt', 'src', 'dst', 'apa', 'apn'], row, ret)
        return ret
