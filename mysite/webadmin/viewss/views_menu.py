import requests
import json
import hashlib

from django.db.models import Count
from django.db import connection
from django.db.models.functions import ExtractDay, TruncDate, TruncDay
from django.http import JsonResponse
from django.shortcuts import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ..forms import *
from datetime import *
import locale

locale.setlocale(locale.LC_ALL, '')

@login_required(login_url='login')
def menu(requets):
    menu = Menu.objects.filter(is_active=1)

    context = {
        'menu': menu,
    }
    return render(requets, 'webadmin/menu/menu_list.html', context)

@login_required(login_url='login')
def detail_menu(requets, id):
    menu = Menu.objects.get(id=id)

    context = {
        'menu': menu,
    }
    return render(requets, 'webadmin/menu/detail_menu.html', context)

@login_required(login_url='login')
def kategori_menu(requets):
    kategori_menu = KategoriMenu.objects.filter(is_active=1)

    context = {
        'kategori_menu': kategori_menu,
    }
    return render(requets, 'webadmin/addson/kategori_menu_list.html', context)