from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import views, tokens, decorators

def index(request):
    return render(request, 'skosapp/home.html')


def contact(request):
    return render(request, 'skosapp/basic.html', {'data': ['Email', 'fameri@txstate.edu']})


def about(request):
    return render(request, 'skosapp/basic.html', {'data': ['item1', 'item2']})
