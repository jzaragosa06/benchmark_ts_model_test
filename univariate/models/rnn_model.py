
import pandas as pd
import numpy as np
import math
import itertools
from keras.models import Sequential
from keras.layers import Dense, SimpleRNN
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Function to split data into X (inputs) and Y (targets)
def get_XY(data, time_steps):
    Y_ind = np.arange(time_steps, len(data), time_steps)
    Y = data[Y_ind]
    rows_x = len(Y)
    X = data[range(time_steps * rows_x)]
    X = np.reshape(X, (rows_x, time_steps, 1))    
    return X, Y



# Function to build and compile the RNN model
def build_rnn(time_steps=12, units=3, dense_units=1, activation=['tanh', 'tanh']):
    model = Sequential()
    model.add(SimpleRNN(units, input_shape=(time_steps, 1), activation=activation[0], return_sequences=False))
    model.add(Dense(dense_units, activation=activation[1]))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model

# Function to train the RNN model
def train_rnn(train_data, time_steps=12, units=3, epochs=10, batch_size=1):
    scaler = MinMaxScaler(feature_range=(0, 1))
    data = scaler.fit_transform(np.array(train_data).astype('float32')).flatten()
    
    trainX, trainY = get_XY(data, time_steps)
    
    model = build_rnn(time_steps, units)
    model.fit(trainX, trainY, epochs=epochs, batch_size=batch_size, verbose=0)
    
    return model, scaler

def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


# Function to evaluate the trained RNN model
def evaluate_rnn(model, test_data, scaler, time_steps=12):
    test_data = scaler.transform(np.array(test_data).astype('float32')).flatten()
    testX, testY = get_XY(test_data, time_steps)
    
    test_predict = model.predict(testX)
    
    test_predict = test_predict.reshape(-1)
    testY = testY.reshape(-1)
    
    # test_rmse = math.sqrt(mean_squared_error(testY, test_predict))
    test_mape = mean_absolute_percentage_error(testY, test_predict)
    return test_mape

def evaluate_final_model(model, test_data, scaler, time_steps=12):
    test_data = scaler.transform(np.array(test_data).astype('float32')).flatten()
    testX, testY = get_XY(test_data, time_steps)
    
    test_predict = model.predict(testX)
    
    test_predict = test_predict.reshape(-1)
    testY = testY.reshape(-1)
    
    mae = mean_absolute_error(testY, test_predict)
    mse = mean_squared_error(testY, test_predict)
    rmse = math.sqrt(mean_squared_error(testY, test_predict))
    mape = mean_absolute_percentage_error(testY, test_predict)
    return mae, mape, mse, rmse


# Function to perform grid search for the number of units
def grid_search(df, units_list, epoch_list, time_steps=12):

    split_percent = 0.8
    split = int(len(df) * split_percent)
    train_data = df[:split]
    test_data = df[split:]

    best_mape = float('inf')
    best_units = None
    best_model = None
    best_scaler = None

    for units, epochs in itertools.product(units_list, epoch_list):
        print(f"Training with units={units}...")
        model, scaler = train_rnn(train_data=train_data,time_steps= time_steps,units= units, epochs=epochs)
        test_mape = evaluate_rnn(model, test_data, scaler, time_steps)
        print(f"Test mape with units={units}: {test_mape:.3f}")
        
        if test_mape < best_mape:
            best_rmse = test_mape
            best_units = units
            best_model = model
            best_scaler = scaler

    print(f"Best mape: {best_rmse:.3f}")
    print(f"Best units: {best_units}")


    mae, mape, mse, rmse = evaluate_final_model(best_model, test_data, best_scaler)

    return mae, mape, mse, rmse




def main():
    # Load data
    sunspots_url = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-sunspots.csv'
    df = pd.read_csv(sunspots_url, usecols=[1], engine='python')
    
    # Define list of units to search
    units_list = [3, 4, 5]
    epoch_list = [3, 4, 5, 10]

    # Perform grid search to find the best number of units
    mae, mape, mse, rmse = grid_search(df, units_list, epoch_list=epoch_list)

    print(f"mae: {mae}")
    print(f"mae: {mape}")
    print(f"mae: {mse}")
    print(f"mae: {rmse}")
if __name__ == "__main__":
    main()

