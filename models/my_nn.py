import dask.array as da
import xarray as xr
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv3D, LSTM, Dense, Flatten, Concatenate, TimeDistributed
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib

def load_and_preprocess_data(folder_path, h_size, lon_size, lat_size):
    data_list = []
    timestamps = []

    for file_name in sorted(os.listdir(folder_path)):
        if file_name.endswith('.nc'):
            file_path = os.path.join(folder_path, file_name)
            print('Path: ', file_path)
            ds = xr.open_dataset(file_path, chunks={'time': 1})
            
            timestamp = ds['time'].values[0]
            timestamps.append(timestamp)

            reflectivity = ds['DBZ'].isel(time=0)
            velocity = ds['VEL'].isel(time=0)

            reflectivity = reflectivity.where(~np.isnan(reflectivity), reflectivity.mean())
            velocity = velocity.where(~np.isnan(velocity), velocity.mean())

            # Extract the chunk from the middle
            ref_grid = reflectivity[16:20, 90:110, 90:110] # adjust dimensions according to available hardware
            vel_grid = velocity[16:20, 90:110, 90:110]

            combined_data = da.stack([ref_grid, vel_grid], axis=-1)
            data_list.append(combined_data)

    data = da.stack(data_list, axis=0)
    return data, np.array(timestamps)

def create_sequences(data, timestamps, input_seq_length=3, forecast_horizon=3):
    X, y, time_diffs = [], [], []
    
    for i in range(len(data) - input_seq_length - forecast_horizon + 1):
        X.append(data[i:i+input_seq_length])
        y.append(data[i+input_seq_length+forecast_horizon-1])
        time_diff = (timestamps[i+input_seq_length+forecast_horizon-1] - timestamps[i]).astype('timedelta64[m]').astype(int)
        time_diffs.append(time_diff)

    return da.stack(X), da.stack(y), np.array(time_diffs)

def build_model(input_shape, output_shape):
    inputs = Input(shape=input_shape, name="input_layer")
    
    x = TimeDistributed(Conv3D(32, (3, 3, 3), activation='relu', padding='same'))(inputs)
    x = TimeDistributed(Conv3D(64, (3, 3, 3), activation='relu', padding='same'))(x)
    
    x = TimeDistributed(Flatten())(x)
    
    x = LSTM(128, return_sequences=False)(x)
    
    time_input = Input(shape=(1,), name="input_layer_1")
    
    x = Concatenate()([x, time_input])
    
    x = Dense(64, activation='relu')(x)
    x = Dense(32, activation='relu')(x)
    
    output = Dense(np.prod(output_shape), activation='linear')(x)
    output = tf.keras.layers.Reshape(output_shape)(output)
    
    model = Model(inputs=[inputs, time_input], outputs=output)
    return model

def main():
    folder_path = '/home/vishwajitsarnobat/Downloads/Aug24_105937' # change folder_path accordingly
    # adjust dimensions according to available hardware
    h_size = 4
    lon_size = 20
    lat_size = 20
    input_seq_length = 3
    forecast_horizon = 3

    data, timestamps = load_and_preprocess_data(folder_path, h_size, lon_size, lat_size)
    X, y, time_diffs = create_sequences(data, timestamps, input_seq_length, forecast_horizon)

    # Convert Dask arrays to NumPy arrays
    X_np = X.compute()
    Y_np = y.compute()

    # Ensure all arrays have the same shape
    min_samples = min(len(X_np), len(Y_np), len(time_diffs))
    X_np = X_np[:min_samples]
    Y_np = Y_np[:min_samples]
    time_diffs = time_diffs[:min_samples]

    # print('X_np: ', X_np, 'Y_np: ', Y_np, 'time_diffs: ', time_diffs)

    X_train, X_test, y_train, y_test, time_diffs_train, time_diffs_test = train_test_split(
        X_np, Y_np, time_diffs, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
    X_test_scaled = scaler.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)
    y_train_scaled = scaler.transform(y_train.reshape(-1, y_train.shape[-1])).reshape(y_train.shape)
    y_test_scaled = scaler.transform(y_test.reshape(-1, y_test.shape[-1])).reshape(y_test.shape)

    joblib.dump(scaler, 'scaler.pkl')

    input_shape = (input_seq_length, h_size, lon_size, lat_size, 2)
    output_shape = (h_size, lon_size, lat_size, 2)
    model = build_model(input_shape, output_shape)
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])

    # Create tf.data.Dataset objects
    train_dataset = tf.data.Dataset.from_tensor_slices((
        {"input_layer": X_train_scaled, "input_layer_1": time_diffs_train.reshape(-1, 1)},
        y_train_scaled
    )).batch(32).prefetch(tf.data.AUTOTUNE)

    validation_dataset = tf.data.Dataset.from_tensor_slices((
        {"input_layer": X_test_scaled, "input_layer_1": time_diffs_test.reshape(-1, 1)},
        y_test_scaled
    )).batch(32).prefetch(tf.data.AUTOTUNE)

    model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=50,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint('best_model.keras', save_best_only=True)
        ]
    )

    test_loss, test_mae = model.evaluate([X_test_scaled, time_diffs_test], y_test_scaled)
    print(f"Test Loss: {test_loss}, Test MAE: {test_mae}")

    predictions = model.predict([X_test_scaled, time_diffs_test])
    predictions = scaler.inverse_transform(predictions.reshape(-1, predictions.shape[-1])).reshape(predictions.shape)
    predictions[predictions < 0] = 0

    reflectivity_true = y_test[..., 0].flatten()
    velocity_true = y_test[..., 1].flatten()
    reflectivity_pred = predictions[..., 0].flatten()
    velocity_pred = predictions[..., 1].flatten()

    mse_reflectivity = mean_squared_error(reflectivity_true, reflectivity_pred)
    mse_velocity = mean_squared_error(velocity_true, velocity_pred)
    mse_total = mean_squared_error(y_test.flatten(), predictions.flatten())
    
    rmse_reflectivity = np.sqrt(mse_reflectivity)
    rmse_velocity = np.sqrt(mse_velocity)
    rmse_total = np.sqrt(mse_total)
    
    mae_reflectivity = mean_absolute_error(reflectivity_true, reflectivity_pred)
    mae_velocity = mean_absolute_error(velocity_true, velocity_pred)
    mae_total = mean_absolute_error(y_test.flatten(), predictions.flatten())
    
    overall_error_percentage = (rmse_total / np.mean(y_test.flatten())) * 100

    print(f"Reflectivity RMSE: {rmse_reflectivity:.2f}, MAE: {mae_reflectivity:.2f}")
    print(f"Velocity RMSE: {rmse_velocity:.2f}, MAE: {mae_velocity:.2f}")
    print(f"Total RMSE: {rmse_total:.2f}, MAE: {mae_total:.2f}")

    print(f"Reflectivity MAE: {mae_reflectivity}")
    print(f"Velocity MAE: {mae_velocity}")
    print(f"Total MAE: {mae_total}")
    
    print(f"Overall Model Error: {overall_error_percentage:.2f}%")

    model.save('precipitation_model.keras')

if __name__ == "__main__":
    main()