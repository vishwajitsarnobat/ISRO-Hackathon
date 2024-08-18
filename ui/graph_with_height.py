import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def create_plots(file_path, height_index):
    # Load the dataset
    dwr = xr.open_dataset(file_path)
    print(f" DWR: {list(dwr.keys())}")

    # Load the data
    dbz = dwr['DBZ']
    vel = dwr['VEL']

    # Prepare the data for plotting
    dbz_at_height = dbz.isel(height=height_index)[0, :, :]
    vel_at_height = vel.isel(height=height_index)[0, :, :]

    # Replace non-positive values with NaN
    dbz_at_height = np.where(dbz_at_height > 0, dbz_at_height, np.nan)
    vel_at_height = np.where(np.abs(vel_at_height) > 0, vel_at_height, np.nan)

    dwr_lat = dwr['latitude']
    dwr_lon = dwr['longitude']
    dwr_lon_grid, dwr_lat_grid = np.meshgrid(dwr_lon, dwr_lat)

    # Plotting
    fig, axs = plt.subplots(1, 2, figsize=(14, 7), subplot_kw={'projection': ccrs.PlateCarree()})

    # Plot DBZ
    ax1 = axs[0]
    ax1.set_title('DBZ at Selected Height', fontsize=12)
    ax1.add_feature(cfeature.LAND, edgecolor='black')
    ax1.add_feature(cfeature.OCEAN)
    ax1.add_feature(cfeature.COASTLINE)
    ax1.add_feature(cfeature.BORDERS, linestyle=':')
    ax1.add_feature(cfeature.LAKES, edgecolor='black')
    ax1.set_xticks(np.arange(dwr_lon_grid.min(), dwr_lon_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax1.set_yticks(np.arange(dwr_lat_grid.min(), dwr_lat_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax1.xaxis.set_tick_params(width=0.5)
    ax1.yaxis.set_tick_params(width=0.5)
    ax1.gridlines(draw_labels=True)
    contour1 = ax1.contourf(dwr_lon_grid, dwr_lat_grid, dbz_at_height, cmap='viridis', transform=ccrs.PlateCarree())

    # Adjust the colorbar for DBZ
    cbar1 = plt.colorbar(contour1, ax=ax1, orientation='horizontal', pad=0.1, fraction=0.046)
    cbar1.set_label('Reflectivity (DBZ)')

    # Plot VEL
    ax2 = axs[1]
    ax2.set_title('Radial Velocity at Selected Height', fontsize=12)
    ax2.add_feature(cfeature.LAND, edgecolor='black')
    ax2.add_feature(cfeature.OCEAN)
    ax2.add_feature(cfeature.COASTLINE)
    ax2.add_feature(cfeature.BORDERS, linestyle=':')
    ax2.add_feature(cfeature.LAKES, edgecolor='black')
    ax2.set_xticks(np.arange(dwr_lon_grid.min(), dwr_lon_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax2.set_yticks(np.arange(dwr_lat_grid.min(), dwr_lat_grid.max(), 1.), crs=ccrs.PlateCarree())
    ax2.xaxis.set_tick_params(width=0.5)
    ax2.yaxis.set_tick_params(width=0.5)
    ax2.gridlines(draw_labels=True)
    contour2 = ax2.contourf(dwr_lon_grid, dwr_lat_grid, vel_at_height, cmap='coolwarm', transform=ccrs.PlateCarree())

    # Adjust the colorbar for VEL
    cbar2 = plt.colorbar(contour2, ax=ax2, orientation='horizontal', pad=0.1, fraction=0.046)
    cbar2.set_label('Radial Velocity (m/s)')

    # Title and layout adjustment
    fig.suptitle(f'Reflectivity (DBZ) and Radial Velocity (VEL) at Height Index {height_index}', fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust space for suptitle

    # Return the figure
    return fig

