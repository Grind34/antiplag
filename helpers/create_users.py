import sys, os
from django.contrib.auth.models import User

f = open('helpers/users.txt','w')

for item in range(120):
	pas = User.objects.make_random_password(length=5, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
	user = User.objects.create_user('Agent'+str(item),'',pas)
	f.writelines('User: '+'Agent'+str(item)+'\n'+'Password: '+pas+'\n\n')

f.close()