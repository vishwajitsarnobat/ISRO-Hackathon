from tensorflow.keras.models import load_model
import numpy as np
import os
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
import xarray as xr
from math_model import main as radar_nowcast_main
import sys

def preprocess_netcdf(folder_path, list_of_input_files, h_size, lon_size, lat_size):
    combined_data_list = []

    for file_name in list_of_input_files:
        file_path = os.path.join(folder_path, file_name)
        ds = xr.open_dataset(file_path)
        reflectivity = ds['DBZ'].isel(time=0)
        velocity = ds['VEL'].isel(time=0)

        reflectivity = reflectivity.where(~np.isnan(reflectivity), reflectivity.mean())
        velocity = velocity.where(~np.isnan(velocity), velocity.mean())

        ref_grid = reflectivity[16:20, 90:110, 90:110]
        vel_grid = velocity[16:20, 90:110, 90:110]

        combined_data = np.stack([ref_grid, vel_grid], axis=-1)
        combined_data_list.append(combined_data)

    return np.array(combined_data_list)

def true_values_file(folder_path, latest_data):
    sorted_files = sorted(os.listdir(folder_path))
    latest_data_index = sorted_files.index(latest_data)
    file_name = sorted_files[latest_data_index + 3]

    file_path = os.path.join(folder_path, file_name)
    ds = xr.open_dataset(file_path)
    reflectivity = ds['DBZ'].isel(time=0)
    velocity = ds['VEL'].isel(time=0)

    reflectivity = reflectivity.where(~np.isnan(reflectivity), reflectivity.mean())
    velocity = velocity.where(~np.isnan(velocity), velocity.mean())

    # adjust dimensions according to available hardware
    h_size = 4
    lon_size = 20
    lat_size = 20
    
    ref_grid = reflectivity[16:20, 90:110, 90:110]
    vel_grid = velocity[16:20, 90:110, 90:110]

    combined_data = np.stack([ref_grid, vel_grid], axis=-1)
    
    print(combined_data)

    return combined_data

def list_of_files(folder_path, latest_data, n):
    input_files_list = []
    sorted_files = sorted(os.listdir(folder_path))

    latest_data_index = sorted_files.index(latest_data)
    for i in range(n):
        input_files_list.append(sorted_files[latest_data_index - i])
    
    return input_files_list

def create_combined_model(input_shape):
    nn_input = Input(shape=input_shape, name='nn_input')
    math_input = Input(shape=input_shape, name='math_input')
    
    combined = Concatenate()([nn_input, math_input])
    x = Dense(64, activation='relu')(combined)
    x = Dense(32, activation='relu')(x)
    output = Dense(np.prod(input_shape), activation='linear')(x)
    output = tf.reshape(output, (-1, *input_shape))
    
    model = Model(inputs=[nn_input, math_input], outputs=output)
    model.compile(optimizer='adam', loss='mse')
    return model

def update_model(combined_model, new_nn_output, new_math_output, new_true_values):
    combined_model.fit(
        [new_nn_output, new_math_output],
        new_true_values,
        epochs=1,
        batch_size=1
    )

def nn_result(folder_path, list_of_input_files):
    model = load_model('best_model.keras')
    scaler = joblib.load('scaler.pkl')

    # adjust dimensions according to available hardware
    h_size = 4
    lon_size = 20
    lat_size = 20

    input_data = preprocess_netcdf(folder_path, list_of_input_files, h_size, lon_size, lat_size)
    time_diff = np.array([[30]])

    input_sequence = np.array(input_data)
    input_sequence = np.expand_dims(input_sequence, axis=0)

    input_sequence_scaled = scaler.transform(input_sequence.reshape(-1, input_sequence.shape[-1])).reshape(input_sequence.shape)

    # Make predictions
    nn_output_scaled = model.predict({"input_layer": input_sequence_scaled, "input_layer_1": time_diff})

    # Reverse scaling for output
    nn_output_flat = nn_output_scaled.reshape(-1, nn_output_scaled.shape[-1])
    nn_output = scaler.inverse_transform(nn_output_flat).reshape(nn_output_scaled.shape)
    nn_output[nn_output < 0] = 0

    # print("Predicted output shape:", nn_output.shape)
    # print("Predicted output values:", nn_output)
    
    return nn_output

def math_result(folder_path, latest_data):
    nowcast_data = radar_nowcast_main(folder_path, latest_data)
    return nowcast_data

def train_or_predict_model(nn_output, math_output, true_values=None, model_path='best_combined_model.keras'):
    if os.path.exists(model_path):
        print(f"Loading existing model from {model_path}...")
        combined_model = load_model(model_path)
    else:
        print(f"Creating a new combined model...")
        combined_model = create_combined_model(nn_output.shape[1:])
    
    predicted_values = combined_model.predict([nn_output, math_output])

    if true_values is not None:
        # Calculate metrics only in training mode
        initial_metrics = calculate_metrics(true_values, predicted_values)
        print("Initial metrics before updating:", initial_metrics)

        # Update model with new data
        update_model(combined_model, nn_output, math_output, true_values)
        
        # Save the updated model
        combined_model.save(model_path)
    
    return combined_model, predicted_values

def calculate_metrics(true_values, predicted_values):
    mse_reflectivity = mean_squared_error(true_values[..., 0].flatten(), predicted_values[..., 0].flatten())
    mse_velocity = mean_squared_error(true_values[..., 1].flatten(), predicted_values[..., 1].flatten())

    mae_reflectivity = mean_absolute_error(true_values[..., 0].flatten(), predicted_values[..., 0].flatten())
    mae_velocity = mean_absolute_error(true_values[..., 1].flatten(), predicted_values[..., 1].flatten())

    rmse_reflectivity = np.sqrt(mse_reflectivity)
    rmse_velocity = np.sqrt(mse_velocity)

    mean_true_reflectivity = np.mean(true_values[..., 0].flatten())
    mean_true_velocity = np.mean(true_values[..., 1].flatten())

    overall_rmse = np.sqrt((mse_reflectivity + mse_velocity) / 2)
    overall_mae = (mae_reflectivity + mae_velocity) / 2

    overall_percentage_error_rmse = (overall_rmse / (mean_true_reflectivity + mean_true_velocity)) * 100
    overall_percentage_error_mae = (overall_mae / (mean_true_reflectivity + mean_true_velocity)) * 100

    return {
        'rmse_reflectivity': rmse_reflectivity,
        'rmse_velocity': rmse_velocity,
        'mae_reflectivity': mae_reflectivity,
        'mae_velocity': mae_velocity,
        'overall_rmse': overall_rmse,
        'overall_mae': overall_mae,
        'PERCENTAGE RMSE ERROR': overall_percentage_error_rmse,
        'PERCENTAGE MAE ERROR': overall_percentage_error_mae
    }

# change folder path and file path accordingly
folder_path = '/home/vishwajitsarnobat/Downloads/testing_data'
latest_data = 'RCTLS_19MAY2024_212249_L2C_STD.nc'
n = 3  # files list for nn
m = 6  # files list for math
list_of_input_files_nn = list_of_files(folder_path, latest_data, n)
print(list_of_input_files_nn)
list_of_input_files_math = list_of_files(folder_path, latest_data, m)
print(list_of_input_files_math)

# Get true values
true_values = true_values_file(folder_path, latest_data)

nn_output = nn_result(folder_path, list_of_input_files_nn)
final_metrics = calculate_metrics(true_values, nn_output)
print('Inaccuracies: ', final_metrics)


# math_output = math_result(folder_path, latest_data)
# # Train or predict using the combined model
# combined_model, predicted_values = train_or_predict_model(nn_output, math_output, true_values)

# math_output = math_result(folder_path, latest_data)
# print('math_output: ', math_output)

# # Set true_values only during training. Leave it as None during live prediction.
# true_values = true_values_file(folder_path, latest_data)

# # Train or predict based on the presence of true_values
# combined_model, final_predictions = train_or_predict_model(nn_output, math_output, true_values=true_values)
# final_metrics = calculate_metrics(true_values, final_predictions)

# if true_values is not None:
#     # Calculate and print final metrics after updating during training
#     final_metrics = calculate_metrics(true_values, final_predictions)
#     print("Final metrics after updating:", final_metrics)
# else:
#     print("Live prediction completed. Final predictions:", final_predictions)
