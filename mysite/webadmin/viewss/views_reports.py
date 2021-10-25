from django.db.models import Count
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from ..forms import *
import locale

locale.setlocale(locale.LC_ALL, '')

@login_required(login_url='login')
def report_merchant(requets):
    report_merchant = Transaction.objects.all().values('toko__nama').annotate(jumlah_trx=Count('id'),
                                                                              nominal_trx=Sum('total'))

    context = {
        'report_merchant': report_merchant,
    }
    return render(requets, 'webadmin/report/report_merchant_list.html', context)


@login_required(login_url='login')
def report_menu(requets):
    report_menu = CartItems.objects.all().values('menu__menu_pic', 'menu__nama', 'toko__nama').annotate(qty=Sum('qty'),
                                                                                                        price=Sum(
                                                                                                            'price'))

    context = {
        'report_menu': report_menu,
    }
    return render(requets, 'webadmin/report/report_menu_list.html', context)


@login_required(login_url='login')
def report_pegawai(requets):
    report_employee = Transaction.objects.all().values('pegawai__nama', 'toko__nama').annotate(jumlah_trx=Count('id'),
                                                                                               nominal_trx=Sum(
                                                                                                   'grand_total'))

    context = {
        'report_employee': report_employee,
    }
    return render(requets, 'webadmin/report/report_pegawai_list.html', context)


@login_required(login_url='login')
def report_disc(requets):
    report_disc = Cart.objects.filter(ordered=1, discount_id__isnull=False).values('discount__nama',
                                                                                   'discount__toko__nama').annotate(
        jumlah_trx=Count('id'))

    context = {
        'report_disc': report_disc,
    }
    return render(requets, 'webadmin/report/report_disc_list.html', context)


@login_required(login_url='login')
def report_table(requets):
    report_table = Cart.objects.filter(ordered=1, table_id__isnull=False).values('table__nama',
                                                                                 'table__toko__nama').annotate(
        jumlah_trx=Count('id'))

    context = {
        'report_table': report_table,
    }
    return render(requets, 'webadmin/report/report_table_list.html', context)


@login_required(login_url='login')
def report_pelanggan(requets):
    report_pelanggan = Cart.objects.filter(ordered=1, pelanggan_id__isnull=False).values('pelanggan__nama',
                                                                                         'pelanggan__toko__nama').annotate(
        jumlah_trx=Count('id'))

    context = {
        'report_pelanggan': report_pelanggan,
    }
    return render(requets, 'webadmin/report/report_pelanggan_list.html', context)