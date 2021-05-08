def cross_up(ordered_materials, preds, material_pred_dict):
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
      cross_sell_dict[i]=0.1*total_HL_ordered

  max_HL_per_day=500
  min_HL_per_day=50

  ###   UPSELL    ###
  upsell_quantities={}
  tot_upsell_quanity=0
  for i in ordered_materials:
    upsell_quantities[i]=0.1*ordered_materials[i]
    tot_upsell_quanity=tot_upsell_quanity+upsell_quantities[i]

  HL_plus_upsell=total_HL_ordered + tot_upsell_quanity

  ###   UPSELL DISCOUNT  ###
  dis=0
  if HL_plus_upsell>max_HL_per_day:
    dis=15.0
  elif (HL_plus_upsell>min_HL_per_day) & (HL_plus_upsell<=max_HL_per_day):
    dis=5.0+ (15-5)*HL_plus_upsell/(500-50)
  
  ###   CROSS SELL DISCOUNT  ###
  base_dis=2.5
  cross_sell_discounts=[]
  for i in range(len(cross_sell_dict)):
    cross_sell_discounts.append(base_dis+i*base_dis)
  
  return cross_sell_dict, cross_sell_discounts, upsell_quantities, dis