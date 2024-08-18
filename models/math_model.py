import xarray as xr
import os
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.animation as animation
from pysteps import nowcasts, motion
import pandas as pd
from pysteps.motion.lucaskanade import dense_lucaskanade
import cv2

def load_and_preprocess_data(folder_path, file_path):
    data_reflex = []
    data_velocity = []

    sorted_files = sorted(os.listdir(folder_path))

    latest_data_index = sorted_files.index(file_path)
    for i in range(6): 
        file_name = sorted_files[latest_data_index - i]
        if file_name.endswith('.nc'):
            file_path = os.path.join(folder_path, file_name)
            with xr.open_dataset(file_path) as ds:
                lat = ds.variables['latitude'][:]
                lon = ds.variables['longitude'][:]

                reflectivity = ds['DBZ'].values[0]
                velocity = ds['VEL'].values[0]

                reflectivity = np.nan_to_num(reflectivity, nan=np.nanmean(reflectivity))
                velocity = np.nan_to_num(velocity, nan=np.nanmean(velocity))

                ref_grid = reflectivity[:81, :481, :481]
                vel_grid = velocity[:81, :481, :481]

                data_reflex.append(ref_grid)
                data_velocity.append(vel_grid)

    return np.array(data_reflex), np.array(data_velocity), np.array(lat), np.array(lon)

def generate_nc(radar_data, latitude, longitude, n_leadtimes=6):
    extrapolate = nowcasts.get_method('steps')
    oflow_method = motion.get_method('LK')
    train_data = np.array(radar_data)

    if train_data.size == 0:
        raise ValueError("Train data is empty. Cannot proceed with nowcasting.")

    radar_forecast_array = []
    for j in range(1): # adjust height dimension according to available hardware
        print("==================================>" + str(j))
        train_data_array = []
        for i in train_data:
            train_data_array.append(i[j])
        reshaped_data = np.mean(train_data, axis=1)
        
        motion_field = oflow_method(reshaped_data)

        R_f = extrapolate(
            reshaped_data,
            motion_field,
            n_leadtimes,
            n_ens_members=5,
            n_cascade_levels=6,
            precip_thr=1.0,
            kmperpixel=2.0,
            timestep=15,
            noise_method="nonparametric",
            vel_pert_method="bps",
            mask_method="incremental",
            seed=1,
        )

        radar_forecast = np.mean(R_f[:, :, :, :], axis=0)
        radar_forecast_array.append(radar_forecast)

    return radar_forecast_array

def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.nan_to_num(y_true), np.nan_to_num(y_pred)
    dif_array = abs(np.subtract(y_true, y_pred))
    return (np.mean(dif_array) / np.mean(y_true)) * 100

def generate_radar_nowcast(folder_path, file_path):
    reflectivity, velocity, latitude, longitude = load_and_preprocess_data(folder_path, file_path)

    if len(reflectivity) == 0:
        raise ValueError("No radar data found. Cannot proceed with nowcasting.")

    radar_forecast_dbz = generate_nc(reflectivity, latitude, longitude)
    radar_forecast_vel = generate_nc(velocity, latitude, longitude)

    return radar_forecast_dbz, radar_forecast_vel, reflectivity, velocity

def compute_gradients_lk_reflectivity(global_max_dbz):
    global_dbz = [np.nan_to_num(frame) for frame in global_max_dbz]
    dbz_stacked = np.stack(global_dbz, axis=0)
    
    assert dbz_stacked.ndim == 3, "Input array must have 3 dimensions: (t, x, y)"
    
    dbz = dense_lucaskanade(dbz_stacked, fd_method='shitomasi')
    
    return dbz

def compute_gradients_lk_radialvelocity(mvh_arr):
    global_mvh = [np.nan_to_num(frame) for frame in mvh_arr]
    mvh_arr_stacked = np.stack(global_mvh, axis=0)
    
    assert mvh_arr_stacked.ndim == 3, "Input array must have 3 dimensions: (t, x, y)"
    
    vel = dense_lucaskanade(mvh_arr_stacked, fd_method='shitomasi')
    
    return vel

def predict_future_reflectivity(global_max_dbz, gradient_dbz, time_interval=12, predict_ahead=10):
    h, w = global_max_dbz[0].shape
    frames_to_predict = 3
    
    flow_dbz = np.dstack(gradient_dbz)
    grid_indices = np.indices((h, w), dtype=np.float32).transpose(1, 2, 0)
    
    map_x_dbz = (grid_indices[:, :, 0] + frames_to_predict * flow_dbz[:, :, 0]).astype(np.float32)
    map_y_dbz = (grid_indices[:, :, 1] + frames_to_predict * flow_dbz[:, :, 1]).astype(np.float32)

    map_x_dbz = np.clip(map_x_dbz, 0, w - 1)
    map_y_dbz = np.clip(map_y_dbz, 0, h - 1)
    df = pd.DataFrame(map_x_dbz)
    df.to_csv('data3.csv', index=False)

    predicted_dbz = cv2.remap(global_max_dbz[-1], map_x_dbz, map_y_dbz, interpolation=cv2.INTER_LINEAR)
    
    return predicted_dbz

def predict_future_velocity(global_max_mvh, gradient_array_vel, time_interval=12, predict_ahead=10):
    h, w = global_max_mvh[0].shape
    frames_to_predict = int(predict_ahead / time_interval)
    
    flow_vel = np.dstack(gradient_array_vel)
    grid_indices = np.indices((h, w)).astype(np.float32).transpose(1, 2, 0)
    
    map_x_vel = (grid_indices[:, :, 0] + frames_to_predict * flow_vel[:, :, 0]).astype(np.float32)
    map_y_vel = (grid_indices[:, :, 1] + frames_to_predict * flow_vel[:, :, 1]).astype(np.float32)
    
    predicted_vel = cv2.remap(global_max_mvh[-1], map_x_vel, map_y_vel, cv2.INTER_LINEAR)
    
    return predicted_vel

def main(folder_path, file_path):
    radar_forecast_dbz, radar_forecast_vel, reflectivity, velocity = generate_radar_nowcast(folder_path, file_path)

    data = []

    for i in range(len(radar_forecast_dbz)):
        gradient_array_dbz = compute_gradients_lk_reflectivity(radar_forecast_dbz[i])
        result_mat = np.add(reflectivity[5], gradient_array_dbz[0])
        data.append(mean_absolute_percentage_error(reflectivity[6][i], result_mat))

    print("The absolute percentage error is: ")
    print(data)
    
    return data

if __name__ == "__main__":
    main()