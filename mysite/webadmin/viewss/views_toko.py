from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from ..forms import *
import locale

locale.setlocale(locale.LC_ALL, '')

@login_required(login_url='login')
def toko(requets):
    toko = Toko.objects.filter(is_active=1)

    context = {
        'toko': toko,
    }
    return render(requets, 'webadmin/toko/toko_list.html', context)


@login_required(login_url='login')
def detail_toko(requets, id):
    toko = Toko.objects.get(id=1)
    menu = Menu.objects.filter(toko_id=id, is_active=1)
    owner = toko.account_set.get(is_owner=1)
    pegawai = toko.account_set.filter(is_owner=0)
    kategori_menu = KategoriMenu.objects.filter(toko_id=id, is_active=1)

    context = {
        'toko': toko,
        'menu': menu,
        'owner': owner,
        'pegawai': pegawai,
        'kategori_menu': kategori_menu,

    }
    return render(requets, 'webadmin/toko/detail_toko.html', context)