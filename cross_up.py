import pandas as pd
import numpy as np
from collections import Counter
import json
from MAR import calc_ark_one_user

def cross_up(ordered_materials, preds, material_pred_dict, wh):

  total_HL_ordered=0
  for i in ordered_materials:
    total_HL_ordered = total_HL_ordered + ordered_materials[i]
  
  c=0
  cross_sell={}
  for i in preds:
    if i not in ordered_materials:
      cross_sell[i]=preds[i]
      c=c+1
    if c==5:
      break

  ###   FIND RECOMMENDED QUANTITIES FOR CROSS SELL MATERIALS    ###
  cross_sell_dict={}
  for i in cross_sell:
    cross_sell_dict[i]=material_pred_dict[i]   ###   ENTER PREDICTED QUANTITIES FROM MODEL    ###
    if(cross_sell_dict[i]>0.1*total_HL_ordered):
      cross_sell_dict[i]=round(0.1*total_HL_ordered, 2)

  max_HL_per_day=500
  min_HL_per_day=50

  ###   UPSELL    ###
  upsell_quantities={}
  tot_upsell_quanity=0
  for i in ordered_materials:
    upsell_quantities[i]=round(0.1*ordered_materials[i], 2)
    tot_upsell_quanity=tot_upsell_quanity+upsell_quantities[i]

  HL_plus_upsell=total_HL_ordered + tot_upsell_quanity

  ###   UPSELL DISCOUNT  ###
  dis=0
  if HL_plus_upsell>max_HL_per_day:
    dis=15.0
  elif (HL_plus_upsell>min_HL_per_day) & (HL_plus_upsell<=max_HL_per_day):
    dis=5.0+ (15-5)*HL_plus_upsell/(500-50)

  dis = round(dis, 2)
  
  ###   CROSS SELL DISCOUNT  ###
  base_dis=2.5
  cross_sell_discounts=[]
  for i in range(len(cross_sell_dict)):
    cross_sell_discounts.append(round(base_dis+i*base_dis, 2))
  
  ### PEOPLE NEAR YOU ALSO BOUGHT ###
  latest_date = None
  wh = int(wh)

  dist = pd.read_csv("data/sorted_user_to_user_distance.csv")
  dist["Distance_in_miles"] = dist["Distance_in_miles"].apply(eval)
  dist = dist.set_index("Wholesaler")

  dfg = pd.read_csv("data/WholesalerDatewise.csv")
  dfg["HLs"] = dfg["HLs"].apply(eval)
  dfg["Materials"] = dfg["Materials"].apply(eval)

  u = (np.array(dist.loc[wh][0])).astype(int)
  L = len(u[u<30]) #change 30 here for 

  if latest_date is None:
    #Can change it to today
    latest_date = sorted(dfg[dfg['Wholesaler'] == wh]["Date"].unique())[-1]

  valid_date = str(np.datetime64(latest_date) - 60) #change 60 here for time period in days


  materials_bought=[]
  for nearby_users in u[1:L]:
    print(nearby_users[1])
    d = dfg[dfg['Wholesaler'] == nearby_users[1]]

    x = d[(d["Date"]<latest_date) & (d["Date"]>valid_date)]

    for i in range(len(x)):
      materials_bought+=x['Materials'].iloc[i]
  
  if len(materials_bought) > 0:
    a = dict(Counter(materials_bought))
    tp = [(a[i], i) for i in a]
    tp = sorted(tp, reverse=True)
    out = (tp)
  else:
    out = []


  ############## GROUPMENT BASED PREDICTIONS ###############
  group_users=pd.read_csv('data/group_users.csv')
  group_top_materials=pd.read_csv('data/group_top_materials.csv')

  grp_of_user=group_users[str(wh)][0]
  top_materials_of_grp=group_top_materials[grp_of_user][:5]
  
  return cross_sell_dict, cross_sell_discounts, upsell_quantities, dis, out[:5], list(top_materials_of_grp)