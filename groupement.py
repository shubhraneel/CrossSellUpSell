###    USER INPUT ID    ###
user_id='40016990'

group_users=pd.read_csv('group_users.csv')
group_top_materials=pd.read_csv('group_top_materials.csv')

grp_of_user=group_users[user_id][0]
top_materials_of_grp=group_top_materials[grp_of_user][:5]

###    RECOMMENDATIONS    ###
print("PEOPLE IN YOUR GROUPEMENT ALSO BOUGHT: ")
for i in top_materials_of_grp:
  print(i)