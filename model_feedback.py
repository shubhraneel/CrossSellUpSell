import numpy as np
import pandas as pd
import json
from material_recommender import RecommenderNet
import tensorflow as tf
import re

d1 = pd.read_csv('data/user_mat_rating_modified_all.csv')
d1["Trend"] = d1["Trend"].apply(eval)

d_whole = pd.read_csv('data/WholesalerDatewise.csv')
d_whole["HLs"] = d_whole["HLs"].apply(eval)
d_whole["Materials"] = d_whole["Materials"].apply(eval)
wholesalers = d_whole["Wholesaler"].unique()

d_HL = pd.read_csv('data/HLWholesalerMaterialPair.csv')
d_HL["HLs"] = d_HL["HLs"].apply(eval)

def convert_dates(dates):
    if len(dates) < 4:
        return []
    return [pd.to_datetime(re.search('\'(.*)\'', s)[1]) for s in dates.split(", ")]

d_HL["Dates"] = d_HL["Dates"].apply(convert_dates)
d_HL["Date Difference"] = d_HL["Date Difference"].apply(eval)

def remove_preeciding_zero(l):
  for i in range(len(l)):
    if l[i]==1: return l[i:]
  else: return l

def count1(l):
  return (l.count(1)/len(l))*100

def cont_z(l):
#     for i in range(len(lp)):
#         if lp[i]==1: start=i; break
            
#     l=lp[start:]
  flag=0; c=0; j=[]
  for i in range(len(l)):
    if l[i]==1 and flag==0:j.append(0); continue
    if l[i]==0 and flag==0: flag=1;
    
    if l[i]==1 and flag==1: flag=0; j.append(c); c=0
    if flag==1: c+=1;
    if i==len(l)-1 and flag==1: flag=0; j.append(c)
      
      
  ser = (j[1:])
  if len(ser)==0: return 0.5
  ans = np.mean(ser)

  if ans==0:
    if len(ser)<2: return 0.5
    else: return np.mean(ser+[1])
  
  else: return ans


def model_feedback(wh, materials, HL_ordered):
  global d1
  global d_whole
  global d_HL

  for i in materials:
    xoi=d1[(d1["Wholesaler"]==wh) & (d1["Material"]==i)]
    print(xoi)
    if len(xoi)>0: 
      ind = list(xoi.index)
      d1.at[ind[0], "Trend"] = d1["Trend"][ind[0]] + [1]
      
      d1.at[ind[0], "gaps"] = cont_z(d1["Trend"][ind[0]])
      d1.at[ind[0], "freq"] = count1(d1["Trend"][ind[0]])
      d1.at[ind[0], "rating"] = d1["freq"][ind[0]] / d1["gaps"][ind[0]]
        
    else:  
      ap = {"Wholesaler": wh, "Material": i, "Trend": [1], "gaps": 1, "freq": 50, "rating": 50}

      d1 = d1.append(ap, ignore_index=True)

  material_unique=d1['Material'].unique().tolist()
  wholesaler_unique=d1['Wholesaler'].unique().tolist()

  mudi={}
  c=0
  for i in material_unique:
    mudi[i]=c
    c=c+1
  f = open('data/mudi.json', "w")
  json.dump(mudi, f)
  f.close()

  wudi={}
  c=0
  for i in wholesaler_unique:
    wudi[i]=c
    c=c+1
  f = open('data/wudi.json', "w")
  json.dump(wudi, f)
  f.close()

  d2 = pd.DataFrame()
  d2["Material"] = [mudi[material] for material in d1["Material"]]
  d2["Wholesaler"] = [wudi[wholesaler] for wholesaler in d1["Wholesaler"]]
  d2["rating"] = np.log10(1 + d1["rating"])
  max_HL=max(d2['rating'])
  d2['rating']=d2['rating']/max_HL

  x=d2[['Wholesaler','Material']]
  y=d2[['rating']]

  num_users=len(d1['Wholesaler'].unique())
  num_materials=len(d1['Material'].unique())

  EMBEDDING_SIZE = 50
  model = RecommenderNet(num_users, num_materials, EMBEDDING_SIZE)

  model.compile(
      loss=tf.keras.losses.BinaryCrossentropy(), optimizer=tf.keras.optimizers.Adam(lr=0.001)
  )

  x=np.array(x)
  y=np.array(y)

  train_indices = d1.shape[0]
  x_train, x_val, y_train, y_val = (
      x[:train_indices],
      x[train_indices:],
      y[:train_indices],
      y[train_indices:],
  )

  y_train=y_train.squeeze()

  history = model.fit(
      x=x_train,
      y=y_train,
      batch_size=64,
      epochs=40,
      verbose=1,
  )

  print("Model trained")

  model.save_weights("models/material_rec", save_format="tf")

  d1.to_csv('data/user_mat_rating_modified_all.csv', index=False)


  ### WholesalerDatewise.csv #######
  today = pd.to_datetime("today")
  order_date = str(today).split()[0]

  x = d_whole[(d_whole["Wholesaler"] == wh) & (d_whole["Date"] == order_date)].index
  if len(x) > 0:
    for i, material in enumerate(materials):
      try:
        index = d_whole["Materials"][x[0]].index(material)
        d_whole.at[x[0], "HLs"][index]+=HL_ordered[i]
      except:
        d_whole.at[x[0], "Materials"] = d_whole["Materials"][x[0]] + [material]
        d_whole.at[x[0], "HLs"] = d_whole["HLs"][x[0]] + [HL_ordered[i]]

    # d_whole.at[x[0], "HLs"] = d_whole["HLs"][x[0]] + HL_ordered
    # d_whole.at[x[0], "Materials"] = d_whole["Materials"][x[0]] + materials

  else:
    ap = {"Wholesaler": wh, "Date": order_date,
          "HLs": HL_ordered, "Materials": materials}
    d_whole = d_whole.append(ap, ignore_index=True)
  d_whole.to_csv('data/WholesalerDatewise.csv', index=False)

  ####### HLWholesalerMaterialPair.csv ########
  for i, material in enumerate(materials):
    x = d_HL[(d_whole["Wholesaler"] == wh) & (d_HL["Material"] == material)].index
    if len(x) > 0:
      if d_HL["Dates"][x[0]][-1] == today:
        d_HL.at[x[0], "HLs"] = d_HL["HLs"][x[0]][:-1] + [d_HL["HLs"][x[0]][-1]+HL_ordered[i]]
      else:
        d_HL.at[x[0], "HLs"] = d_HL["HLs"][x[0]] + [HL_ordered[i]]
        d_HL.at[x[0], "Dates"] = d_HL["Dates"][x[0]] + [today]
        # print(f"Today: {today}")
        # print(f"Date: {d_HL['Dates'][x[0]][-1]}")
        d_HL.at[x[0], "Date Difference"] = d_HL["Date Difference"][x[0]][:-1] \
        + [(today - d_HL["Dates"][x[0]][-2]).days, 1]
    else:
      ap = {"Wholesaler": wh, "Material": material, "Dates": [today],
            "HLs": [HL_ordered], "Date Difference": [1]}
      d_HL = d_HL.append(ap, ignore_index=True)
  d_HL.to_csv('data/HLWholesalerMaterialPair.csv', index=False)
