###   RECALL @ K  ###
def rk(relevance_list,no_of_relevant):
   rel_in_list=sum(relevance_list)
   return rel_in_list/no_of_relevant


###   AVERAGE RECALL @ K  ###
def ark(relevance_list,no_of_relevant):
   ark_val=0
   for i in range(len(relevance_list)):
     ark_val=ark_val+rk(relevance_list[:(i+1)],min(i+1,no_of_relevant))*relevance_list[i]
   return ark_val/len(relevance_list)


###   AVERAGE RECALL@K FOR 1 USER ###
def calc_ark_one_user(rec_list,order_list):
   relevance_list=[]
   for i in rec_list:
     if i in order_list:
       relevance_list.append(1)
     else:
       relevance_list.append(0)
   no_of_relevant = len(order_list)
   return ark(relevance_list,no_of_relevant)


###   AVERAGE RECALL@K FOR ALL USERS  ###
def calc_mark_all_users(user_list,all_user_rec_list,all_user_order_list):
  ark_list=[]
  for i in range(len(user_list)):
     x=calc_ark_one_user(all_user_rec_list[i],all_user_order_list[i])
     ark_list.append(x)
  return mark(len(user_list),ark_list)


###   MEAN AVERAGE RECALL@K  ###
def mark(no_of_users, ar_list):
   return sum(ar_list)/no_of_users