from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def theme_debug(request):
    return render(request, 'theme_debug.html')
