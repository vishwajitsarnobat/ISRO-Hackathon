#file = r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_104437_L2C_STD.nc'

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cartopy.crs as ccrs

def create_3d_stack_plots(file_path):
    # Load the dataset
    dwr = xr.open_dataset(file_path)
    print(f"DWR: {list(dwr.keys())}")

    # Load the data
    dbz = dwr['DBZ']
    vel = dwr['VEL']
    
    dwr_lat = dwr['latitude']
    dwr_lon = dwr['longitude']
    dwr_lon_grid, dwr_lat_grid = np.meshgrid(dwr_lon, dwr_lat)
    
    # Create 3D figures for DBZ and VEL
    fig_dbz = plt.figure(figsize=(14, 10))
    ax_dbz = fig_dbz.add_subplot(111, projection='3d')
    
    fig_vel = plt.figure(figsize=(14, 10))
    ax_vel = fig_vel.add_subplot(111, projection='3d')
    
    # Loop through each height index to plot and stack the 2D plots
    for height_index in range(80):
        # Prepare the data for plotting
        dbz_at_height = dbz.isel(height=height_index)[0, :, :]
        vel_at_height = vel.isel(height=height_index)[0, :, :]

        # Replace non-positive values with NaN
        dbz_at_height = np.where(dbz_at_height > 0, dbz_at_height, np.nan)
        vel_at_height = np.where(np.abs(vel_at_height) > 0, vel_at_height, np.nan)
        
        # Set the height in meters (index * 250m)
        z_height = height_index * 250
        
        # Plot DBZ contours stacked by height in the first figure
        ax_dbz.contourf(dwr_lon_grid, dwr_lat_grid, dbz_at_height, zdir='z', offset=z_height, cmap='viridis', alpha=0.5)
        
        # Plot VEL contours stacked by height in the second figure
        ax_vel.contourf(dwr_lon_grid, dwr_lat_grid, vel_at_height, zdir='z', offset=z_height, cmap='coolwarm', alpha=0.5)
    
    # Labels and title for DBZ
    ax_dbz.set_xlabel('Longitude')
    ax_dbz.set_ylabel('Latitude')
    ax_dbz.set_zlabel('Height (m)')
    ax_dbz.set_title('3D Stacked Plots of Reflectivity (DBZ) Across Heights', fontsize=14)
    ax_dbz.set_zlim(0, 80 * 250)
    
    # Labels and title for VEL
    ax_vel.set_xlabel('Longitude')
    ax_vel.set_ylabel('Latitude')
    ax_vel.set_zlabel('Height (m)')
    ax_vel.set_title('3D Stacked Plots of Velocity (VEL) Across Heights', fontsize=14)
    ax_vel.set_zlim(0, 80 * 250)
    
    # Show the plots
    
    # Return both figures and axes for further use
    return (fig_dbz, ax_dbz), (fig_vel, ax_vel)

# Example usage

