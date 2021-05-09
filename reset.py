import pandas as pd
import json
from material_recommender import RecommenderNet
import numpy as np

def reset():

  csv_files = [
    "group_top_materials",
    "group_users",
    "HLWholesalerMaterialPair",
    "sorted_user_to_user_distance",
    "user_mat_rating_modified_all",
    "wholesaler_coordinates",
    "WholesalerDatewise"
  ]

  for file in csv_files:
    d1 = pd.read_csv(f"original_data/{file}.csv")
    d1.to_csv(f"data/{file}.csv", index=False)
  
  json_files = [
    "materials",
    "mudi",
    "wholesalers",
    "wudi"
  ]

  for file in json_files:
    obj = json.load(open(f"original_data/{file}.json"))
    with open(f"data/{file}.json", "w+") as f:
      json.dump(obj, f)
  
  EMBEDDING_SIZE = 50

  f = open('original_data/wudi.json',)
  wudi = json.load(f)
  wudi = {int(k): v for k, v in wudi.items()}
  f.close()

  f = open('original_data/mudi.json',)
  mudi = json.load(f)
  mudi = {int(k): v for k, v in mudi.items()}
  f.close()

  num_wholesalers = len(np.unique(np.array(list(wudi.keys()))))
  num_materials = len(np.unique(np.array(list(mudi.keys()))))

  M = RecommenderNet(num_wholesalers, num_materials, EMBEDDING_SIZE)
  M.load_weights("original_data/material_rec")

  M.save_weights("models/material_rec", save_format="tf")
