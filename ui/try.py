import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import RegularGridInterpolator

def create_3d_stack_plots_interpolated(file_path):
    # Load the dataset
    dwr = xr.open_dataset(file_path)
    print(f"DWR: {list(dwr.keys())}")

    # Load the data
    dbz = dwr['DBZ']
    vel = dwr['VEL']
    
    dwr_lat = dwr['latitude']
    dwr_lon = dwr['longitude']
    dwr_height = np.arange(dbz.shape[1]) * 250  # Assuming height levels are 250m apart

    # Create a finer grid for interpolation
    lat_fine = np.linspace(dwr_lat.min(), dwr_lat.max(), 100)
    lon_fine = np.linspace(dwr_lon.min(), dwr_lon.max(), 100)
    height_fine = np.linspace(0, dwr_height.max(), 160)  # Double the height resolution
    
    lon_fine_grid, lat_fine_grid = np.meshgrid(lon_fine, lat_fine)
    
    # Interpolators for DBZ and VEL
    dbz_interpolator = RegularGridInterpolator((dwr_height, dwr_lat, dwr_lon), dbz[0].data, bounds_error=False, fill_value=np.nan)
    vel_interpolator = RegularGridInterpolator((dwr_height, dwr_lat, dwr_lon), vel[0].data, bounds_error=False, fill_value=np.nan)
    
    # Create 3D figures for DBZ and VEL
    fig_dbz = plt.figure(figsize=(14, 10))
    ax_dbz = fig_dbz.add_subplot(111, projection='3d')
    
    fig_vel = plt.figure(figsize=(14, 10))
    ax_vel = fig_vel.add_subplot(111, projection='3d')
    
    # Loop through each interpolated height index to plot and stack the 2D plots
    for z_height in height_fine:
        # Prepare the data for plotting
        dbz_at_height_fine = dbz_interpolator((z_height, lat_fine[:, np.newaxis], lon_fine[np.newaxis, :]))
        vel_at_height_fine = vel_interpolator((z_height, lat_fine[:, np.newaxis], lon_fine[np.newaxis, :]))

        # Replace non-positive values with NaN
        dbz_at_height_fine = np.where(dbz_at_height_fine > 0, dbz_at_height_fine, np.nan)
        vel_at_height_fine = np.where(np.abs(vel_at_height_fine) > 0, vel_at_height_fine, np.nan)
        
        # Plot DBZ contours stacked by height in the first figure
        ax_dbz.contourf(lon_fine_grid, lat_fine_grid, dbz_at_height_fine, zdir='z', offset=z_height, cmap='viridis', alpha=0.5)
        
        # Plot VEL contours stacked by height in the second figure
        ax_vel.contourf(lon_fine_grid, lat_fine_grid, vel_at_height_fine, zdir='z', offset=z_height, cmap='coolwarm', alpha=0.5)
    
    # Labels and title for DBZ
    ax_dbz.set_xlabel('Longitude')
    ax_dbz.set_ylabel('Latitude')
    ax_dbz.set_zlabel('Height (m)')
    ax_dbz.set_title('3D Stacked Plots of Interpolated Reflectivity (DBZ) Across Heights', fontsize=14)
    ax_dbz.set_zlim(0, height_fine[-1])
    
    # Labels and title for VEL
    ax_vel.set_xlabel('Longitude')
    ax_vel.set_ylabel('Latitude')
    ax_vel.set_zlabel('Height (m)')
    ax_vel.set_title('3D Stacked Plots of Interpolated Velocity (VEL) Across Heights', fontsize=14)
    ax_vel.set_zlim(0, height_fine[-1])
    
    # Show the plots
    plt.show()
    
    # Return both figures and axes for further use
    return (fig_dbz, ax_dbz), (fig_vel, ax_vel)

# Call the function with the file path
figure = create_3d_stack_plots_interpolated(r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_064726_L2C_STD.nc')
plt.show()