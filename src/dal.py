import os
import sqlite3


class DAL(object):

    @staticmethod
    def get_config():
        return os.environ['SHWM_DB_PATH']

    @staticmethod
    def get_lite_connection():
        db_path = DAL.get_config()
        if not os.path.exists(db_path):
            raise db_path + ' no exitist!'
        conn = sqlite3.connect(os.environ['SHWM_DB_PATH'])
        return conn


if __name__ == '__main__':
    pass
