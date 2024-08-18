import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_plots(file_path):
    # Load the dataset
    dwr = xr.open_dataset(file_path)
    
    # Load the data
    dbz = dwr['DBZ']
    vel = dwr['VEL']
    
    # Prepare the data for plotting
    max_dbz = dbz.max('height')[0, :, :]
    mvh = vel.max('height')[0, :, :]
    
    # Replace non-positive values with NaN
    max_dbz = np.where(max_dbz > 0, max_dbz, np.nan)
    mvh = np.where(np.abs(mvh) > 0, mvh, np.nan)
    
    dwr_lat = dwr['latitude']
    dwr_lon = dwr['longitude']
    dwr_lon_grid, dwr_lat_grid = np.meshgrid(dwr_lon, dwr_lat)
    
    return max_dbz, mvh, dwr_lon_grid, dwr_lat_grid, dwr.time.values

def setup_animation(file_paths):
    fig, axs = plt.subplots(1, 2, figsize=(12, 6), subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Set up axes
    for ax in axs:
        ax.add_feature(cfeature.LAND, edgecolor='black')
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, edgecolor='black')
        ax.gridlines(draw_labels=True)
    
    axs[0].set_title('Maximum DBZ at All Heights', fontsize=12)
    axs[1].set_title('Maximum Radial Velocity at All Heights', fontsize=12)
    
    # Initial empty contours (to be updated in animation)
    max_dbz, mvh, dwr_lon_grid, dwr_lat_grid, _ = create_plots(file_paths[0])
    contour1 = axs[0].contourf(dwr_lon_grid, dwr_lat_grid, max_dbz, cmap='viridis', transform=ccrs.PlateCarree())
    contour2 = axs[1].contourf(dwr_lon_grid, dwr_lat_grid, mvh, cmap='coolwarm', transform=ccrs.PlateCarree())
    
    plt.colorbar(contour1, ax=axs[0], label='DBZ')
    plt.colorbar(contour2, ax=axs[1], label='Radial Velocity (m/s)')
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    return fig, axs, contour1, contour2

def animate(frame, file_paths, axs, contour1, contour2):
    max_dbz, mvh, dwr_lon_grid, dwr_lat_grid, time = create_plots(file_paths[frame])
    
    # Clear the axes
    axs[0].cla()
    axs[1].cla()
    
    # Add features again after clearing the axes
    for ax in axs:
        ax.add_feature(cfeature.LAND, edgecolor='black')
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, edgecolor='black')
        ax.gridlines(draw_labels=True)

    # Replot the contours
    contour1 = axs[0].contourf(dwr_lon_grid, dwr_lat_grid, max_dbz, cmap='viridis', transform=ccrs.PlateCarree())
    contour2 = axs[1].contourf(dwr_lon_grid, dwr_lat_grid, mvh, cmap='coolwarm', transform=ccrs.PlateCarree())
    
    plt.suptitle(f'Reflectivity (DBZ) and Radial Velocity (VEL) at All Heights\nTime: {time[0]}', fontsize=14)
    
    return contour1, contour2

# Main execution
if __name__ == "__main__":
    file_paths = [
        r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_002045_L2C_STD.nc', r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_010951_L2C_STD.nc', r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_014015_L2C_STD.nc', r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_022734_L2C_STD.nc', r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_025754_L2C_STD.nc', r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_031311_L2C_STD.nc', r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_050008_L2C_STD.nc', r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_063207_L2C_STD.nc', r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_064726_L2C_STD.nc', r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_085001_L2C_STD.nc', r'C:\Users\Jash\Downloads\RCTLS_01JUL2024_104437_L2C_STD.nc'
        # Add more file paths as needed
    ]
    
    fig, axs, contour1, contour2 = setup_animation(file_paths)
    
    anim = FuncAnimation(
        fig, animate, frames=len(file_paths), 
        fargs=(file_paths, axs, contour1, contour2),
        interval=500, blit=False
    )
    
    # Save the animation (uncomment to save)
    # anim.save('radar_animation.gif', writer='pillow', fps=1)
    
    plt.show()
