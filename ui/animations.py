import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_plots(file_path):
    dwr = xr.open_dataset(file_path)
    dbz = dwr['DBZ']
    vel = dwr['VEL']
    max_dbz = dbz.max('height')[0, :, :]
    mvh = vel.max('height')[0, :, :]
    max_dbz = np.where(max_dbz > 0, max_dbz, np.nan)
    mvh = np.where(np.abs(mvh) > 0, mvh, np.nan)
    dwr_lat = dwr['latitude']
    dwr_lon = dwr['longitude']
    dwr_lon_grid, dwr_lat_grid = np.meshgrid(dwr_lon, dwr_lat)
    return max_dbz, mvh, dwr_lon_grid, dwr_lat_grid, dwr.time.values

def setup_animation(file_paths):
    fig, axs = plt.subplots(1, 2, figsize=(8, 6), subplot_kw={'projection': ccrs.PlateCarree()})
    for ax in axs:
        ax.add_feature(cfeature.LAND, edgecolor='black')
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, edgecolor='black')
        ax.gridlines(draw_labels=True)
    axs[0].set_title('Maximum DBZ at All Heights', fontsize=12)
    axs[1].set_title('Maximum Radial Velocity at All Heights', fontsize=12)
    max_dbz, mvh, dwr_lon_grid, dwr_lat_grid, _ = create_plots(file_paths[0])
    contour1 = axs[0].contourf(dwr_lon_grid, dwr_lat_grid, max_dbz, cmap='viridis', transform=ccrs.PlateCarree())
    contour2 = axs[1].contourf(dwr_lon_grid, dwr_lat_grid, mvh, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.colorbar(contour1, ax=axs[0], label='DBZ')
    plt.colorbar(contour2, ax=axs[1], label='Radial Velocity (m/s)')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return fig, axs, contour1, contour2

def animate(frame, file_paths, axs, contour1, contour2):
    max_dbz, mvh, dwr_lon_grid, dwr_lat_grid, time = create_plots(file_paths[frame])
    axs[0].cla()
    axs[1].cla()
    for ax in axs:
        ax.add_feature(cfeature.LAND, edgecolor='black')
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, edgecolor='black')
        ax.gridlines(draw_labels=True)
    contour1 = axs[0].contourf(dwr_lon_grid, dwr_lat_grid, max_dbz, cmap='viridis', transform=ccrs.PlateCarree())
    contour2 = axs[1].contourf(dwr_lon_grid, dwr_lat_grid, mvh, cmap='coolwarm', transform=ccrs.PlateCarree())
    plt.suptitle(f'Reflectivity (DBZ) and Radial Velocity (VEL) at All Heights\nTime: {time[0]}', fontsize=14)
    return contour1, contour2

def get_animation(file_paths):
    fig, axs, contour1, contour2 = setup_animation(file_paths)
    anim = FuncAnimation(
        fig, animate, frames=len(file_paths), 
        fargs=(file_paths, axs, contour1, contour2),
        interval=100, blit=False
    )
    return fig, anim
