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

# model
class RecommenderNet(keras.Model):
  def __init__(self, num_users, num_movies, embedding_size, **kwargs):
    super(RecommenderNet, self).__init__(**kwargs)
    self.num_users = num_users
    self.num_movies = num_movies
    self.embedding_size = embedding_size
    self.user_embedding = layers.Embedding(
        num_users,
        embedding_size,
        embeddings_initializer="he_normal",
        embeddings_regularizer=keras.regularizers.l2(1e-6),
    )
    self.user_bias = layers.Embedding(num_users, 1)
    self.movie_embedding = layers.Embedding(
        num_movies,
        embedding_size,
        embeddings_initializer="he_normal",
        embeddings_regularizer=keras.regularizers.l2(1e-6),
    )
    self.movie_bias = layers.Embedding(num_movies, 1)

  def call(self, inputs):
    user_vector = self.user_embedding(inputs[:, 0])
    user_bias = self.user_bias(inputs[:, 0])
    movie_vector = self.movie_embedding(inputs[:, 1])
    movie_bias = self.movie_bias(inputs[:, 1])
    dot_user_movie = tf.tensordot(user_vector, movie_vector, 2)
    # Add all the components (including bias)
    x = dot_user_movie + user_bias + movie_bias
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
M.load_weights("models/material_recommed")

def predict(wholesaler_id, k=5):

  one_user_wholesaler=[]
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
  top_k = [key_list_1[val_list_1.index(x)] for x in np.argsort(preds)[-k:][::-1]]

  return top_k
