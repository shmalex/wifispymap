import os
import pandas as pd
import numpy as np


devices_df = pd.read_csv(os.path.join('..', 'data', 'devices.csv'))
manufacture_name_df = pd.read_pickle(os.path.join(
    '..', 'data', 'device_names.pickle'), compression='gzip')

print(devices_df.head())
manufacture_name_df.set_index('mac',inplace=True)
#devices_df.set_index('mac')
print(manufacture_name_df.head())


def device_name(mac):
    name = ''
    try:
        name = ' a.k.a. ['+devices_df['name'][mac]+']'
    except KeyError:
        pass

    try:
        return manufacture_name_df['name'][mac[:8]] + ' #'+mac+name
    except KeyError:
        pass
    return mac + name
