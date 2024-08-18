import numpy as np
import xarray as xr

dwr = xr.open_dataset(r'C:\Users\Jash\Downloads\RCTLS_12NOV2023_211335_L2C_STD.nc')
dwr_lat = dwr['latitude']
dwr_lon = dwr['longitude']

dwr_lat = dwr_lat[:200]
dwr_lon = dwr_lon[:200]
    
print(dwr_lat.values)
print(dwr_lon.values)