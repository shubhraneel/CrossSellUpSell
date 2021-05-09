import pandas as pd
import numpy as np
import bisect
import json

from geopy.distance import great_circle

dloc = pd.read_csv("data/wholesaler_coordinates.csv")

d2 = pd.read_csv("data/sorted_user_to_user_distance.csv")

d2["Distance_in_miles"] = d2["Distance_in_miles"].apply(eval)

d3 = pd.read_csv("data/group_users.csv")

with open("data/wholesalers.json") as f:
  wholesalers = json.load(f)


def add_new(data):
  global dloc
  global d2
  global d3
  global wholesalers
  
  wh = int(data["wholesaler"])
  groupment = data["groupment"]
  Lat = float(data["latitude"])
  Long = float(data["longitude"])

  if wh not in dloc["Wholesaler"].tolist():
    ap_loc ={"Wholesaler": int(wh), "Latitude": Lat, "Longitude": Long}
    dloc = dloc.append(ap_loc, ignore_index=True)

    
  l=[]
  for i in range(len(dloc)):
    l1 = (Lat, Long)
    l2 = (dloc["Latitude"][i], dloc["Longitude"][i])
    jw = dloc["Wholesaler"][i]

    try:
      dy = (great_circle(l1, l2).miles)
      l.append((dy, jw))
    except:
      pass
        
        
  if wh not in d2["Wholesaler"].tolist():
    d2 = d2.set_index("Wholesaler")
    for i in l:
      if i[1]!= wh:
        bisect.insort(d2.loc[i[1]].at['Distance_in_miles'], (i[0], wh))

    d2 = d2.reset_index()

    ap2 = {"Wholesaler": wh, "Distance_in_miles": sorted(l)}
    d2 = d2.append(ap2, ignore_index=True)

  dloc.to_csv("data/wholesaler_coordinates.csv", index=False)
  d2.to_csv("data/sorted_user_to_user_distance.csv", index=False)

  d3.insert(len(d3.columns), str(wh), [groupment])
  d3.to_csv("data/group_users.csv", index=False)

  bisect.insort(wholesalers, str(wh))
  print(wholesalers)
  with open("data/wholesalers.json", "w+") as f:
    json.dump(wholesalers, f)
