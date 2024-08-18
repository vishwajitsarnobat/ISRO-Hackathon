import xarray as xr
import numpy as np
from paths import file_paths

def get_time_difference(path_1, path_2):

# Load the datasets
    data1 = xr.open_dataset(path_1)
    data2 = xr.open_dataset(path_2)

# Extract timestamps
    time1 = data1['time'].values[0]
    time2 = data2['time'].values[0]

# Convert to numpy datetime64 objects
    time1 = np.datetime64(time1)
    time2 = np.datetime64(time2)

# Calculate the difference in minutes
    time_difference = (time2 - time1) / np.timedelta64(1, 'm')

    return time_difference

