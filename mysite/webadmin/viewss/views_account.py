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
def account(requets):
    account = Account.objects.filter(is_owner=1)

    context = {
        'account': account,
    }
    return render(requets, 'webadmin/account/account_list.html', context)

@login_required(login_url='login')
def detail_account(requets, id):
    account = Account.objects.get(id=id)
    toko = account.toko.filter(is_active=1)

    context = {
        'account': account,
        'toko': toko,
    }
    return render(requets, 'webadmin/account/detail_account.html', context)


@login_required(login_url='login')
def pegawai(requets):
    account = Account.objects.filter(is_owner=0)

    context = {
        'account': account,
    }
    return render(requets, 'webadmin/account/pegawai_list.html', context)


@login_required(login_url='login')
def detail_pegawai(requets, id):
    account = Account.objects.get(id=id)
    toko = account.toko.all()

    context = {
        'account': account,
        'toko': toko,
    }
    return render(requets, 'webadmin/account/detail_pegawai.html', context)