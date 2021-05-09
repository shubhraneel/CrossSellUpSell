import pandas as pd
import numpy as np
from zipfile import ZipFile
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from pathlib import Path
import operator
import json

# constants
EMBEDDING_SIZE = 50
POPULAR_BRANDS = {
  11574: 1.0, 
  10946: 1.0, 
  3372: 1.0, 
  9974: 1.0, 
  19898: 1.0, 
  3410: 1.0, 
  10965: 1.0, 
  59848: 1.0, 
  11766: 1.0, 
  20614: 1.0
  }

# model
class RecommenderNet(keras.Model):
  def __init__(self, num_users, num_materials, embedding_size, **kwargs):
    super(RecommenderNet, self).__init__(**kwargs)
    self.num_users = num_users
    self.num_materials = num_materials
    self.embedding_size = embedding_size
    self.user_embedding = layers.Embedding(
        num_users,
        embedding_size,
        embeddings_initializer="he_normal",
        embeddings_regularizer=keras.regularizers.l2(1e-6),
    )
    self.user_bias = layers.Embedding(num_users, 1)
    self.material_embedding = layers.Embedding(
        num_materials,
        embedding_size,
        embeddings_initializer="he_normal",
        embeddings_regularizer=keras.regularizers.l2(1e-6),
    )
    self.material_bias = layers.Embedding(num_materials, 1)

  def call(self, inputs):
    user_vector = self.user_embedding(inputs[:, 0])
    user_bias = self.user_bias(inputs[:, 0])
    material_vector = self.material_embedding(inputs[:, 1])
    material_bias = self.material_bias(inputs[:, 1])
    dot_user_material = tf.tensordot(user_vector, material_vector, 2)
    # Add all the components (including bias)
    x = dot_user_material + user_bias + material_bias
    # The sigmoid activation forces the rating to between 0 and 1
    return tf.nn.sigmoid(x)

# initial execution

# reading id dictionaries
f = open('data/wudi.json',)
wudi = json.load(f)
wudi = {int(k): v for k, v in wudi.items()}
f.close()

f = open('data/mudi.json',)
mudi = json.load(f)
mudi = {int(k): v for k, v in mudi.items()}
f.close()

num_wholesalers = len(np.unique(np.array(list(wudi.keys()))))
num_materials = len(np.unique(np.array(list(mudi.keys()))))

# loading pretrained model weights for prediction
M = RecommenderNet(num_wholesalers, num_materials, EMBEDDING_SIZE)
M.load_weights("models/material_rec")

def predict_material(wholesaler_id, k=10):

  one_user_wholesaler=[]
  if wholesaler_id not in wudi:
    return POPULAR_BRANDS.keys(), POPULAR_BRANDS

  wholesaler_id_transformed = wudi[wholesaler_id]
  for i in range(num_materials):
      one_user_wholesaler.append(wholesaler_id_transformed)
  one_user_material=[]
  for i in range(num_materials):
      one_user_material.append(i)

  one_user = pd.DataFrame({'wholesaler':one_user_wholesaler})
  one_user['material'] = one_user_material
  one_user["wholesaler"] = one_user_wholesaler

  key_list_1 = list(mudi.keys())
  val_list_1 = list(mudi.values())

  preds = M.predict(np.array(one_user))
  preds = np.squeeze(preds)
  sort_ids = np.argsort(preds)[-k:][::-1]
  top_k = [key_list_1[val_list_1.index(x)] for x in sort_ids]
  preds = {key_list_1[val_list_1.index(x)]: float(preds[x]) for x in sort_ids}

  return top_k, preds
