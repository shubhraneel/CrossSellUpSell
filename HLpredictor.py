import pandas as pd
import re
import numpy as np
import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras import backend as K
from tensorflow.keras.optimizers import Adam
import pickle


with open("data/HL_scaler.pkl", "rb") as f:
  scaler = pickle.load(f)

def return_model():
  inputs = Input(shape=(None, 2))
  X = LSTM(10, return_sequences=True)(inputs)
  X = LSTM(10, return_sequences=True)(X)
  outputs = LSTM(1)(X)
  model = Model(inputs=inputs, outputs=outputs)
  return model

model = return_model()
model.load_weights("models/HLpred")

def predict_HL(wholesaler, material):
  data = pd.read_csv("data/HLWholesalerMaterialPair.csv")
  nearest_users = pd.read_csv("data/sorted_user_to_user_distance.csv", index_col=0)
  data_new = data[data["Wholesaler"] == wholesaler]
  row = (data_new[data_new["Material"] == material])
  if len(row) == 0:
    distances = eval(nearest_users.loc[wholesaler]["Distance_in_miles"])
    flag = 0
    for distance, user in distances:
      row = data[(data["Wholesaler"] == user) & (data["Material"] == material)]
      if len(row) > 0 and len(eval(row.iloc[0]["HLs"])) > 1:
        flag = 1
        break
    if flag == 0:
      row = data[data["Material"] == material]
      if len(row) > 0:
        value = np.average(row["HLs"].apply(eval).apply(lambda x:x[0]))
        return (value if value > 0 else 4.2)  
      else:
        return 4.2
    # list_of_HL = list((data[data["Material"] == material]["HLs"]).apply(eval))
    # list_HL = []
    # for list_of in list_of_HL:
    #   list_HL += list_of
    # return np.average(list_HL)
  row = row.iloc[0]
  HLs = eval(row["HLs"])
  date_diffs = eval(row["Date Difference"])
  last_order_date = pd.to_datetime(row["Dates"].split("'")[-2])
  days = (pd.to_datetime('today') - last_order_date).days
  date_diffs[-1] = days
  if len(HLs) > 9:
    HLs = HLs[-9:]
    date_diffs = date_diffs[-9:]
    row = np.concatenate((np.reshape(HLs, (-1, 1)), np.reshape(date_diffs, (-1, 1))), axis=1)
  else:
    row = np.concatenate((np.reshape(HLs, (-1, 1)), np.reshape(date_diffs, (-1, 1))), axis=1)
  row = scaler.transform(row)
  row = np.reshape(row, (1, -1, 2))
  pred = model.predict(row)
  pred = scaler.inverse_transform(np.array([[pred[0][0], 0]]))[0][0]
  return pred
