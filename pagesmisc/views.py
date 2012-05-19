# Create your views here.

from django.contrib.auth import authenticate, login, logout
from lib.decorators import render_to
from django.shortcuts import redirect

@render_to('index.html')
def main(request):
    return {}

def exit(request):
    logout(request)
    return redirect('main')

@render_to('registration/login.html')
def enter(request):
    if request.POST:
        user = authenticate(username = request.POST['login'], password = request.POST['pswd'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('main')
            else:
                return redirect('main')
        else:
            #logger.info('Login Fail Login: %s Password: %s' % (request.POST['login'],request.POST['pswd']))
            return redirect('main')
    else:
        return {}
