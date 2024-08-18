import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd


# lat = [6.37081, 6.379856, 6.388902, 6.3979483, 6.4069943, 6.4160404, 6.4250865, 6.4341326, 6.4431787, 6.4522247, 6.461271,  6.470317,  6.4793625, 6.4884086, 6.4974546, 6.5065007, 6.515547, 6.524593, 6.533639, 6.5426846 6.5517306
#  6.5607767 6.569823  6.578869  6.5879145 6.5969605 6.6060066 6.6150527
#  6.624099  6.6331444 6.6421905 6.6512365 6.6602826 6.669328  6.6783743
#  6.6874204 6.6964664 6.705512  6.714558  6.723604  6.73265   6.741696
#  6.750742  6.7597876 6.7688336 6.7778797 6.7869253 6.7959714 6.8050175
#  6.814063  6.823109  6.8321548 6.841201  6.850247  6.8592925 6.8683386
#  6.877384  6.8864303 6.8954763 6.904522  6.913568  6.9226136 6.9316597
#  6.9407053 6.9497514 6.958797  6.967843  6.9768887 6.9859347 6.9949803
#  7.0040264 7.013072  7.022118  7.0311637 7.04021   7.0492554 7.058301
#  7.067347  7.0763927 7.0854387 7.0944843 7.1035304 7.112576  7.1216216
#  7.1306677 7.1397133 7.148759  7.157805  7.1668506 7.175896  7.1849422
#  7.193988  7.2030334 7.2120795 7.221125  7.2301707 7.239217  7.2482624
#  7.257308  7.2663536 7.2753997 7.2844453 7.293491  7.3025365 7.3115826
#  7.320628  7.329674  7.3387194 7.347765  7.356811  7.3658566 7.3749022
#  7.383948  7.3929935 7.402039  7.411085  7.4201307 7.4291763 7.438222
#  7.4472675 7.456313  7.4653587 7.4744043 7.48345   7.4924955 7.5015416
#  7.510587  7.519633  7.5286784 7.537724  7.5467696 7.555815  7.564861
#  7.5739064 7.582952  7.5919976 7.601043  7.610089  7.6191344 7.62818
#  7.6372256 7.6462708 7.6553164 7.664362  7.6734076 7.682453  7.6914988
#  7.7005444 7.70959   7.7186356 7.727681  7.7367263 7.745772  7.7548175
#  7.763863  7.7729087 7.7819543 7.7909994 7.800045  7.8090906 7.818136
#  7.8271813 7.836227  7.8452725 7.854318  7.8633637 7.872409  7.8814545
#  7.8905    7.899545  7.908591  7.9176364 7.9266815 7.935727  7.9447727
#  7.953818  7.9628634 7.971909  7.980954  7.99      7.9990454 8.008091
#  8.017136  8.026181  8.035227  8.044272  8.053318  8.062363  8.071408
#  8.080454  8.089499  8.098544  8.10759   8.116635  8.125681  8.134726, 8.143771, 8.152817, 8.161862, 8.170907 ]

# lon = [74.68674  74.69578  74.70482  74.71386  74.72291  74.73195  74.74099
#  74.75003  74.75907  74.76811  74.77716  74.7862   74.79524  74.80428
#  74.813324 74.82237  74.83141  74.840454 74.849495 74.858536 74.86758
#  74.876625 74.885666 74.89471  74.90375  74.91279  74.92183  74.93088
#  74.93992  74.94896  74.958    74.96704  74.97609  74.98513  74.99417
#  75.00321  75.01225  75.02129  75.03034  75.03938  75.04842  75.057465
#  75.066505 75.075554 75.084595 75.093636 75.10268  75.11172  75.12076
#  75.12981  75.13885  75.14789  75.15693  75.16597  75.17502  75.18406
#  75.1931   75.20214  75.21118  75.22022  75.22927  75.23831  75.24735
#  75.25639  75.265434 75.274475 75.28352  75.292564 75.301605 75.310646
#  75.31969  75.32873  75.337776 75.34682  75.35586  75.3649   75.37394
#  75.38298  75.39203  75.40107  75.41011  75.41915  75.42819  75.43723
#  75.44627  75.45532  75.46436  75.473404 75.482445 75.491486 75.50053
#  75.50957  75.518616 75.52766  75.5367   75.54574  75.55478  75.56382
#  75.57286  75.5819   75.59095  75.59999  75.60903  75.61807  75.62711
#  75.636154 75.645195 75.654236 75.66328  75.672325 75.681366 75.69041
#  75.69945  75.70849  75.71753  75.72657  75.73561  75.74465  75.75369
#  75.76273  75.771774 75.78082  75.78986  75.798904 75.807945 75.816986
#  75.82603  75.83507  75.84411  75.85315  75.86219  75.87123  75.88027
#  75.88931  75.89835  75.907394 75.916435 75.925476 75.93452  75.94356
#  75.9526   75.96164  75.97068  75.97972  75.98876  75.9978   76.00684
#  76.015884 76.024925 76.033966 76.04301  76.05205  76.06109  76.07013
#  76.07917  76.08821  76.09725  76.10629  76.11533  76.124374 76.133415
#  76.142456 76.1515   76.16054  76.16958  76.17862  76.18766  76.19669
#  76.205734 76.214775 76.223816 76.23286  76.2419   76.25094  76.25998
#  76.26902  76.27806  76.287094 76.296135 76.305176 76.31422  76.32326
#  76.3323   76.34134  76.35037  76.35941  76.368454 76.377495 76.386536
#  76.39558  76.40461  76.41365  76.42269  76.43173  76.44077  76.449814
#  76.45885  76.46789  76.47693  76.48597 ]  



def create_plots_dbz(file_path, height_index):
    # Load the dataset
    dwr = xr.open_dataset(file_path)
    print(f" DWR: {list(dwr.keys())}")

    # Load the reflectivity data (DBZ)
    dbz = dwr['DBZ']

    # Extract the data for the specified height index
    dbz_at_height = dbz.isel(height=height_index)[0, :, :]

    # Replace non-positive values with NaN to avoid plotting them
    dbz_at_height = np.where(dbz_at_height > 0, dbz_at_height, np.nan)

    # Extract latitude and longitude
    dwr_lat = dwr['latitude']
    dwr_lon = dwr['longitude']

    dwr_lat = dwr_lat[:200]
    dwr_lon = dwr_lon[:200]

    dwr_lon_grid, dwr_lat_grid = np.meshgrid(dwr_lon, dwr_lat)

    time = pd.to_datetime(dwr['time'].values[0]).strftime('%Y-%m-%d %H:%M:%S')

    # Plotting
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': ccrs.PlateCarree()})

    # Plot DBZ
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAKES, edgecolor='black')
    ax.set_xticks(np.arange(dwr_lon_grid.min(), dwr_lon_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(dwr_lat_grid.min(), dwr_lat_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax.xaxis.set_tick_params(width=0.5)
    ax.yaxis.set_tick_params(width=0.5)
    ax.gridlines(draw_labels=True)

    # Contour plot for DBZ
    contour = ax.contourf(dwr_lon_grid, dwr_lat_grid, dbz_at_height, cmap='viridis', transform=ccrs.PlateCarree())

    # Adjust the colorbar for DBZ
    cbar = plt.colorbar(contour, ax=ax, orientation='horizontal', pad=0.1, fraction=0.046)
    cbar.set_label(f'Reflectivity (DBZ) at time: {time}')

    # Layout adjustment to fit the page well
    plt.tight_layout()

    # Return the figure
    return fig

def create_plots_vel(file_path, height_index):
    # Load the dataset
    dwr = xr.open_dataset(file_path)
    print(f"DWR: {list(dwr.keys())}")

    # Load the data
    vel = dwr['VEL']

    # Prepare the data for plotting
    vel_at_height = vel.isel(height=height_index)[0, :, :]

    # Replace non-positive values with NaN
    vel_at_height = np.where(np.abs(vel_at_height) > 0, vel_at_height, np.nan)

    # Extract latitude and longitude
    dwr_lat = dwr['latitude']
    dwr_lon = dwr['longitude']

    dwr_lat = dwr_lat[:200]
    dwr_lon = dwr_lon[:200]

    dwr_lon_grid, dwr_lat_grid = np.meshgrid(dwr_lon, dwr_lat)

    time = pd.to_datetime(dwr['time'].values[0]).strftime('%Y-%m-%d %H:%M:%S')

    # Plotting
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': ccrs.PlateCarree()})

    # Plot VEL
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAKES, edgecolor='black')
    ax.set_xticks(np.arange(dwr_lon_grid.min(), dwr_lon_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(dwr_lat_grid.min(), dwr_lat_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax.xaxis.set_tick_params(width=0.5)
    ax.yaxis.set_tick_params(width=0.5)
    ax.gridlines(draw_labels=True)
    contour = ax.contourf(dwr_lon_grid, dwr_lat_grid, vel_at_height, cmap='coolwarm', transform=ccrs.PlateCarree())

    # Adjust the colorbar for VEL
    cbar = plt.colorbar(contour, ax=ax, orientation='horizontal', pad=0.1, fraction=0.046)
    cbar.set_label(f'Radial Velocity (m/s) at time: {time}')

    # Layout adjustment to fit the page well
    plt.tight_layout()

    # Return the figure
    return fig

def longlat():
    dwr = xr.open_dataset(r'C:\Users\Jash\Downloads\RCTLS_12NOV2023_211335_L2C_STD.nc')
    print(f" DWR: {list(dwr.keys())}")
    dwr_lat = dwr['latitude']
    dwr_lon = dwr['longitude']

    dwr_lat = dwr_lat[:200]
    dwr_lon = dwr_lon[:200]
    
    return dwr_lat, dwr_lon

def prediction_plot_dbz(dbz_values, height_index):

    dwr_lat, dwr_lon = longlat()

    # Extract the data for the specified height index for both DBZ and VEL
    dbz_at_height = dbz_values[height_index, :, :]

    # Replace non-positive values with NaN to avoid plotting them
    dbz_at_height = np.where(dbz_at_height > 0, dbz_at_height, np.nan)

    # Create the longitude and latitude grid
    dwr_lon_grid, dwr_lat_grid = np.meshgrid(dwr_lon, dwr_lat)

    # Time placeholder (you may replace this with actual time information if available)
    time = "Time Placeholder"

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})

    # Plot DBZ
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAKES, edgecolor='black')
    ax.set_xticks(np.arange(dwr_lon_grid.min(), dwr_lon_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(dwr_lat_grid.min(), dwr_lat_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax.xaxis.set_tick_params(width=0.5)
    ax.yaxis.set_tick_params(width=0.5)
    ax.gridlines(draw_labels=True)

    # Contour plot for DBZ
    contour = ax.contourf(dwr_lon_grid, dwr_lat_grid, dbz_at_height, cmap='viridis', transform=ccrs.PlateCarree())

    # Adjust the colorbar for DBZ
    cbar = plt.colorbar(contour, ax=ax, orientation='horizontal', pad=0.05, fraction=0.046)
    cbar.set_label(f'Reflectivity (DBZ) at time: {time}')

    # Layout adjustment to fit the page well
    plt.tight_layout()

    # Return the figure
    return fig

def prediction_plot_vel(vel_values, height_index):

    dwr_lat, dwr_lon = longlat()

    # Extract the data for the specified height index for VEL
    vel_at_height = vel_values[height_index, :, :]

    # Replace non-positive values with NaN
    vel_at_height = np.where(np.abs(vel_at_height) > 0, vel_at_height, np.nan)

    # Create the longitude and latitude grid
    dwr_lon_grid, dwr_lat_grid = np.meshgrid(dwr_lon, dwr_lat)

    # Time placeholder (you may replace this with actual time information if available)
    time = "Time Placeholder"

    # Plotting
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': ccrs.PlateCarree()})

    # Plot VEL
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAKES, edgecolor='black')
    ax.set_xticks(np.arange(dwr_lon_grid.min(), dwr_lon_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(dwr_lat_grid.min(), dwr_lat_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax.xaxis.set_tick_params(width=0.5)
    ax.yaxis.set_tick_params(width=0.5)
    ax.gridlines(draw_labels=True)
    
    # Contour plot for VEL
    contour = ax.contourf(dwr_lon_grid, dwr_lat_grid, vel_at_height, cmap='coolwarm', transform=ccrs.PlateCarree())

    # Adjust the colorbar for VEL
    cbar = plt.colorbar(contour, ax=ax, orientation='horizontal', pad=0.1, fraction=0.046)
    cbar.set_label(f'Radial Velocity (m/s) at time: {time}')

    # Layout adjustment to fit the page well
    plt.tight_layout()

    # Return the figure
    return fig

