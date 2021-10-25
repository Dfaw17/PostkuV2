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
from .forms import *
from datetime import *
import locale

locale.setlocale(locale.LC_ALL, '')


# Create your views here.

def loginpage(requets):
    if requets.method == "POST":
        username = requets.POST.get('username')
        password = requets.POST.get('password')
        user = authenticate(requets, username=username, password=password)

        if user is not None:
            if user.is_superuser == 1:
                login(requets, user)
                return redirect('home')
            else:
                return redirect('wrong_access')
        else:
            messages.error(requets, 'Username or Password Failed')
    context = {}
    return render(requets, 'webadmin/login.html', context)


def registerpage(requets):
    form = RegisterForm()

    if requets.method == "POST":
        form = RegisterForm(requets.POST)
        if form.is_valid():
            form.save()
            messages.success(requets, 'Register successfully')
            return redirect('login')

    context = {
        'form': form,
    }
    return render(requets, 'webadmin/register.html', context)


def wrong_access(requets):
    context = {
    }
    return render(requets, 'webadmin/404.html', context)


@login_required(login_url='login')
def logoutpage(requets):
    logout(requets)
    return redirect('login')


@login_required(login_url='login')
def home(requets):
    date = requets.POST.get('date')
    date2 = requets.POST.get('date2')
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    today_start = datetime.combine(today, time())
    today_end = datetime.combine(tomorrow, time())

    if date and date2 != None:
        account = Account.objects.filter(is_owner=1, created_at__range=[date, date2])
        total_account = account.count()

        toko = Toko.objects.filter(is_active=1, created_at__range=[date, date2])
        total_toko = toko.count()

        menu = Menu.objects.filter(is_active=1, created_at__range=[date, date2])
        total_menu = menu.count()

        pegawai = Account.objects.filter(is_owner=0, created_at__range=[date, date2])
        total_pegawai = pegawai.count()

        transaction = Transaction.objects.filter(created_at__range=[date, date2]).aggregate(Sum('total'))

        transaction_tunai = Transaction.objects.filter(payment_type_id=1, created_at__range=[date, date2]).aggregate(
            Sum('grand_total'))

        transaction_qris = Transaction.objects.filter(payment_type_id=2, created_at__range=[date, date2]).aggregate(
            Sum('total'))

        revenue_postku = Transaction.objects.filter(created_at__range=[date, date2]).aggregate(Sum('pajak'))

        all_ppob = PPOBPrepaidTransaction.objects.filter(created_at__range=[date, date2]).aggregate(Sum('price_postku'))

        pending_ppob = PPOBPrepaidTransaction.objects.filter(status="Pending",
                                                             created_at__range=[date, date2]).aggregate(
            Sum('price_postku'))

        gagal_ppob = PPOBPrepaidTransaction.objects.filter(status="Gagal", created_at__range=[date, date2]).aggregate(
            Sum('price_postku'))

        sukses_ppob = PPOBPrepaidTransaction.objects.filter(status="Sukses", created_at__range=[date, date2]).aggregate(
            Sum('price_postku'))

        all_topup_wallet = ConfirmWallet.objects.filter(created_at__range=[date, date2]).aggregate(
            Sum('balance'))

        pending_topup_wallet = ConfirmWallet.objects.filter(status_confirm=1,
                                                            created_at__range=[date, date2]).aggregate(
            Sum('balance'))

        gagal_topup_wallet = ConfirmWallet.objects.filter(status_confirm=3,
                                                          created_at__range=[date, date2]).aggregate(
            Sum('balance'))

        sukses_topup_wallet = ConfirmWallet.objects.filter(status_confirm=2,
                                                           created_at__range=[date, date2]).aggregate(
            Sum('balance'))

        difference_ppob = PPOBPrepaidTransaction.objects.filter(created_at__range=[date, date2]).aggregate(
            price_diff=Sum('price_postku') - Sum('price'))

        trx_subs = TrxSubs.objects.filter(created_at__range=[date, date2]).aggregate(Sum('invoice'))

        chart_trx = Transaction.objects.filter(created_at__range=[date, date2]).extra(
            select={'day': 'DATE(created_at)'}).values('day').annotate(
            grand_total=Sum('grand_total'))

        chart_req_topup = ConfirmWallet.objects.filter(created_at__range=[date, date2]).extra(
            select={'day': 'DATE(created_at)'}).values('day').annotate(
            balance=Sum('balance'))

        chart_trx_ppob = PPOBPrepaidTransaction.objects.filter(created_at__range=[date, date2]).extra(
            select={'day': 'DATE(created_at)'}).values('day').annotate(
            price_postku=Sum('price_postku'))

        chart_subs = TrxSubs.objects.filter(created_at__range=[date, date2]).extra(
            select={'day': 'DATE(created_at)'}).values('day').annotate(
            invoice=Sum('invoice'))
    else:
        account = Account.objects.filter(is_owner=1, created_at__range=[today_start, today_end])
        total_account = account.count()

        toko = Toko.objects.filter(is_active=1, created_at__range=[today_start, today_end])
        total_toko = toko.count()

        menu = Menu.objects.filter(is_active=1, created_at__range=[today_start, today_end])
        total_menu = menu.count()

        pegawai = Account.objects.filter(is_owner=0, created_at__range=[today_start, today_end])
        total_pegawai = pegawai.count()

        transaction = Transaction.objects.filter(created_at__range=[today_start, today_end]).aggregate(Sum('total'))

        transaction_tunai = Transaction.objects.filter(payment_type_id=1,
                                                       created_at__range=[today_start, today_end]).aggregate(
            Sum('grand_total'))

        transaction_qris = Transaction.objects.filter(payment_type_id=2,
                                                      created_at__range=[today_start, today_end]).aggregate(
            Sum('total'))

        revenue_postku = Transaction.objects.filter(created_at__range=[today_start, today_end]).aggregate(Sum('pajak'))

        all_ppob = PPOBPrepaidTransaction.objects.filter(created_at__range=[today_start, today_end]).aggregate(
            Sum('price_postku'))

        pending_ppob = PPOBPrepaidTransaction.objects.filter(status="Pending",
                                                             created_at__range=[today_start, today_end]).aggregate(
            Sum('price_postku'))

        gagal_ppob = PPOBPrepaidTransaction.objects.filter(status="Gagal",
                                                           created_at__range=[today_start, today_end]).aggregate(
            Sum('price_postku'))

        sukses_ppob = PPOBPrepaidTransaction.objects.filter(status="Sukses",
                                                            created_at__range=[today_start, today_end]).aggregate(
            Sum('price_postku'))

        all_topup_wallet = ConfirmWallet.objects.filter(created_at__range=[today_start, today_end]).aggregate(
            Sum('balance'))

        pending_topup_wallet = ConfirmWallet.objects.filter(status_confirm=1,
                                                            created_at__range=[today_start, today_end]).aggregate(
            Sum('balance'))

        gagal_topup_wallet = ConfirmWallet.objects.filter(status_confirm=3,
                                                          created_at__range=[today_start, today_end]).aggregate(
            Sum('balance'))

        sukses_topup_wallet = ConfirmWallet.objects.filter(status_confirm=2,
                                                           created_at__range=[today_start, today_end]).aggregate(
            Sum('balance'))

        difference_ppob = PPOBPrepaidTransaction.objects.filter(created_at__range=[today_start, today_end]).aggregate(
            price_diff=Sum('price_postku') - Sum('price'))

        trx_subs = TrxSubs.objects.filter(created_at__range=[today_start, today_end]).aggregate(Sum('invoice'))

        chart_trx = Transaction.objects.filter(created_at__range=[today_start, today_end]).extra(
            select={'day': 'DATE( created_at )'}).values('day').annotate(
            grand_total=Sum('grand_total'))

        chart_req_topup = ConfirmWallet.objects.filter(created_at__range=[today_start, today_end]).extra(
            select={'day': 'DATE(created_at)'}).values('day').annotate(
            balance=Sum('balance'))

        chart_trx_ppob = PPOBPrepaidTransaction.objects.filter(created_at__range=[today_start, today_end]).extra(
            select={'day': 'DATE(created_at)'}).values('day').annotate(
            price_postku=Sum('price_postku'))

        chart_subs = TrxSubs.objects.filter(created_at__range=[today_start, today_end]).extra(
            select={'day': 'DATE(created_at)'}).values('day').annotate(
            invoice=Sum('invoice'))

    if transaction.get('total__sum') is None:
        total_all_transaction = 0
    else:
        total_all_transaction = transaction.get('total__sum')

    if transaction_tunai.get('grand_total__sum') is None:
        total_all_trx_tunai = 0
    else:
        total_all_trx_tunai = transaction_tunai.get('grand_total__sum')

    if transaction_qris.get('total__sum') is None:
        total_all_trx_qris = 0
    else:
        total_all_trx_qris = transaction_qris.get('total__sum')

    if revenue_postku.get('pajak__sum') is None:
        total_revenue_postku = 0
    else:
        total_revenue_postku = revenue_postku.get('pajak__sum')

    if all_ppob.get('price_postku__sum') is None:
        total_all_ppob = 0
    else:
        total_all_ppob = all_ppob.get('price_postku__sum')

    if pending_ppob.get('price_postku__sum') is None:
        total_pending_ppob = 0
    else:
        total_pending_ppob = pending_ppob.get('price_postku__sum')

    if gagal_ppob.get('price_postku__sum') is None:
        total_gagal_ppob = 0
    else:
        total_gagal_ppob = gagal_ppob.get('price_postku__sum')

    if sukses_ppob.get('price_postku__sum') is None:
        total_sukses_ppob = 0
    else:
        total_sukses_ppob = sukses_ppob.get('price_postku__sum')

    if all_topup_wallet.get('balance__sum') is None:
        total_all_topup_wallet = 0
    else:
        total_all_topup_wallet = all_topup_wallet.get('balance__sum')

    if pending_topup_wallet.get('balance__sum') is None:
        total_pending_topup_wallet = 0
    else:
        total_pending_topup_wallet = pending_topup_wallet.get('balance__sum')

    if gagal_topup_wallet.get('balance__sum') is None:
        total_gagal_topup_wallet = 0
    else:
        total_gagal_topup_wallet = gagal_topup_wallet.get('balance__sum')

    if sukses_topup_wallet.get('balance__sum') is None:
        total_sukses_topup_wallet = 0
    else:
        total_sukses_topup_wallet = sukses_topup_wallet.get('balance__sum')

    if difference_ppob.get('price_diff') is None:
        total_difference_ppob = 0
    else:
        total_difference_ppob = difference_ppob.get('price_diff')

    if trx_subs.get('invoice__sum') is None:
        total_trx_subs = 0
    else:
        total_trx_subs = trx_subs.get('invoice__sum')

    context = {
        'total_account': total_account,
        'total_toko': total_toko,
        'total_menu': total_menu,
        'total_pegawai': total_pegawai,
        'total_all_transaction': total_all_transaction,
        'total_all_trx_tunai': total_all_trx_tunai,
        'total_all_trx_qris': total_all_trx_qris,
        'total_revenue_postku': total_revenue_postku,
        'total_all_ppob': total_all_ppob,
        'total_pending_ppob': total_pending_ppob,
        'total_gagal_ppob': total_gagal_ppob,
        'total_sukses_ppob': total_sukses_ppob,
        'total_all_topup_wallet': total_all_topup_wallet,
        'total_pending_topup_wallet': total_pending_topup_wallet,
        'total_gagal_topup_wallet': total_gagal_topup_wallet,
        'total_sukses_topup_wallet': total_sukses_topup_wallet,
        'chart_trx': chart_trx,
        'chart_req_topup': chart_req_topup,
        'chart_trx_ppob': chart_trx_ppob,
        'chart_subs': chart_subs,
        'total_nett_income': total_difference_ppob + total_revenue_postku + total_trx_subs,
    }
    return render(requets, 'webadmin/index.html', context)


@login_required(login_url='login')
def account(requets):
    account = Account.objects.filter(is_owner=1)

    context = {
        'account': account,
    }
    return render(requets, 'webadmin/account/account_list.html', context)


@login_required(login_url='login')
def subs(requets):
    account = Account.objects.filter(is_owner=1, is_subs=1)

    context = {
        'account': account,
    }
    return render(requets, 'webadmin/subs/subs_list.html', context)


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
def absen(requets):
    absen = Absensi.objects.all()

    context = {
        'absen': absen,
    }
    return render(requets, 'webadmin/absen/absen_list.html', context)


@login_required(login_url='login')
def kategori_menu(requets):
    kategori_menu = KategoriMenu.objects.filter(is_active=1)

    context = {
        'kategori_menu': kategori_menu,
    }
    return render(requets, 'webadmin/addson/kategori_menu_list.html', context)


@login_required(login_url='login')
def transaction(requets):
    date = requets.POST.get('date')
    date2 = requets.POST.get('date2')
    today = datetime.today().date()
    current_month = datetime.now().month

    # LIST TRX
    if date and date2 != "":
        transaction = Transaction.objects.filter(created_at__range=[date, date2]).order_by('created_at')
    else:
        transaction = Transaction.objects.all()

    # DAILY TRX
    daily_trx = Transaction.objects.filter(created_at__date=today).aggregate(Sum('total'))
    if daily_trx.get('total__sum') == None:
        total_daily_trx = 0
    else:
        total_daily_trx = daily_trx.get('total__sum')

    # MOUNTLY TRX
    mountly_trx = Transaction.objects.filter(created_at__month=current_month).aggregate(Sum('total'))
    if mountly_trx.get('total__sum') == None:
        total_mountly_trx = 0
    else:
        total_mountly_trx = mountly_trx.get('total__sum')

    # YEARS TRX
    years_trx = Transaction.objects.filter(created_at__year=today.year).aggregate(Sum('total'))
    if years_trx.get('total__sum') == None:
        total_years_trx = 0
    else:
        total_years_trx = mountly_trx.get('total__sum')

    # ALL TRX
    all_trx = Transaction.objects.all().aggregate(Sum('total'))
    if all_trx.get('total__sum') == None:
        total_all_trx = 0
    else:
        total_all_trx = mountly_trx.get('total__sum')

    context = {
        'transaction': transaction,
        'total_daily_transaction': total_daily_trx,
        'total_mountly_trx': total_mountly_trx,
        'total_years_trx': total_years_trx,
        'total_all_trx': total_all_trx,
    }
    return render(requets, 'webadmin/transaction/transaction_list.html', context)


@login_required(login_url='login')
def transaction_tunai(requets):
    transaction = Transaction.objects.filter(payment_type_id=1)

    context = {
        'transaction': transaction
    }
    return render(requets, 'webadmin/transaction/transaction_tunai_list.html', context)


@login_required(login_url='login')
def transaction_qris(requets):
    transaction = Transaction.objects.filter(payment_type_id=2)

    context = {
        'transaction': transaction
    }
    return render(requets, 'webadmin/transaction/transaction_qris_list.html', context)


@login_required(login_url='login')
def transaction_ppob(requets):
    transaction = PPOBPrepaidTransaction.objects.all()

    context = {
        'transaction': transaction
    }
    return render(requets, 'webadmin/transaction/transaction_ppob_list.html', context)


@login_required(login_url='login')
def settlement(requets):
    settlement = Settlement.objects.filter(status_settelement=0)

    context = {
        'settlement': settlement
    }
    return render(requets, 'webadmin/settlement/settlement_list.html', context)


@login_required(login_url='login')
def request_topup(requets):
    rt = ConfirmWallet.objects.filter(status_confirm=1)

    context = {
        'rt': rt
    }
    return render(requets, 'webadmin/wallet/request_topup/request_topup_list.html', context)


@login_required(login_url='login')
def request_topup_approve(requets):
    rt = ConfirmWallet.objects.filter(status_confirm=2)

    context = {
        'rt': rt
    }
    return render(requets, 'webadmin/wallet/request_topup/request_topup_approve.html', context)


@login_required(login_url='login')
def request_topup_reject(requets):
    rt = ConfirmWallet.objects.filter(status_confirm=3)

    context = {
        'rt': rt
    }
    return render(requets, 'webadmin/wallet/request_topup/request_topup_reject.html', context)


@login_required(login_url='login')
def settlement_detail(requets, id):
    settlement = Settlement.objects.get(id=id)
    data_trx = settlement.data.all()

    context = {
        'settlement': settlement,
        'data_trx': data_trx,
    }
    return render(requets, 'webadmin/settlement/detail_settlement.html', context)


@login_required(login_url='login')
def request_topup_detail(requets, id):
    rt = ConfirmWallet.objects.get(id=id)

    context = {
        'rt': rt
    }
    return render(requets, 'webadmin/wallet/request_topup/detail_request_topup.html', context)


@login_required(login_url='login')
def confirm_settlement(request, id):
    settlement = Settlement.objects.get(id=id)
    settlement.status_settelement = 1
    settlement.save()

    messages.info(request, 'Success Confirm Settlement')
    return HttpResponseRedirect('/transaction/settlement')


@login_required(login_url='login')
def confirm_request_topup_reject(requets, id):
    c = connection.cursor()
    c.execute(f'UPDATE webadmin_confirmwallet SET status_confirm=3 WHERE id="{id}"')

    wallet_id = ConfirmWallet.objects.get(id=id)
    wallet = WalletToko.objects.get(id=wallet_id.wallet_id)
    wallet.status_req_deposit = 0
    wallet.save()

    messages.info(requets, 'Success Reject Topup Wallet')
    return HttpResponseRedirect('/request_topup')


@login_required(login_url='login')
def confirm_request_topup(requets, id):
    c = connection.cursor()
    c.execute(f'UPDATE webadmin_confirmwallet SET status_confirm=2 WHERE id="{id}"')

    wallet_id = ConfirmWallet.objects.get(id=id)
    wallet = WalletToko.objects.get(id=wallet_id.wallet_id)
    wallet.status_req_deposit = 0
    wallet.save()

    years = datetime.today().strftime('%Y')
    mounth = datetime.today().strftime('%m')
    day = datetime.today().strftime('%d')
    hours = datetime.today().strftime('%H')
    munites = datetime.today().strftime('%M')
    seconds = datetime.today().strftime('%S')
    notes = f'Wallet {wallet.wallet_code} Success Deposit Balance Rp.{wallet.balance_req} at {years}-{mounth}-{day} {hours}:{munites}:{seconds}'

    trx_wallet = TrxWallet(wallet_code=wallet.wallet_code, type=1, adjustment_balance=wallet.balance_req, note=notes,
                           wallet_id=wallet_id.wallet_id)
    trx_wallet.save()

    messages.info(requets, 'Success Approve Topup Wallet')
    return HttpResponseRedirect('/request_topup')


@login_required(login_url='login')
def settlement_done(requets):
    settlement = Settlement.objects.filter(status_settelement=1)

    context = {
        'settlement': settlement
    }
    return render(requets, 'webadmin/settlement/settlement_list_done.html', context)


@login_required(login_url='login')
def settlement_detail_done(requets, id):
    settlement = Settlement.objects.get(id=id)
    data_trx = settlement.data.all()
    print(data_trx)

    context = {
        'settlement': settlement,
        'data_trx': data_trx,
    }
    return render(requets, 'webadmin/settlement/detail_settlement_done.html', context)


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


@login_required(login_url='login')
def discount(requets):
    discount = Discount.objects.filter(is_active=1)

    context = {
        'discount': discount,
    }
    return render(requets, 'webadmin/addson/discount_list.html', context)


@login_required(login_url='login')
def table(requets):
    table = TableManagement.objects.filter(is_active=1)

    context = {
        'table': table,
    }
    return render(requets, 'webadmin/addson/table_list.html', context)


@login_required(login_url='login')
def stock(requets):
    stock = StockMenu.objects.all()

    context = {
        'stock': stock,
    }
    return render(requets, 'webadmin/addson/stock_list.html', context)


@login_required(login_url='login')
def wallets(requets):
    wallets = WalletToko.objects.all()

    context = {
        'wallets': wallets,
    }
    return render(requets, 'webadmin/wallet/wallets/wallets_list.html', context)


@login_required(login_url='login')
def history_stock(requets, id):
    trx_stock = TrxStockMenu.objects.filter(stock_id=id)
    stock = StockMenu.objects.get(id=id)

    context = {
        'trx_stock': trx_stock,
        'stock': stock,
    }

    return render(requets, 'webadmin/addson/history_stock.html', context)


def detail_wallets(requets, id):
    wallet = WalletToko.objects.get(id=id)
    wallet_history = TrxWallet.objects.filter(wallet_id=id)

    context = {
        'wallet': wallet,
        'wallet_history': wallet_history,
    }

    return render(requets, 'webadmin/wallet/wallets/detail_wallet.html', context)


@login_required(login_url='login')
def pelanggan(requets):
    pelanggan = Pelanggan.objects.filter(is_active=1)

    context = {
        'pelanggan': pelanggan,
    }
    return render(requets, 'webadmin/addson/pelanggan_list.html', context)


@login_required(login_url='login')
def tipe_order(requets):
    tipe_order = OrderType.objects.all()

    context = {
        'tipe_order': tipe_order,
    }
    return render(requets, 'webadmin/addson/tipe_order_list.html', context)


@login_required(login_url='login')
def label_order(requets):
    label_order = LabelOrder.objects.all()

    context = {
        'label_order': label_order,
    }
    return render(requets, 'webadmin/addson/label_order_list.html', context)


@login_required(login_url='login')
def detail_transaction(requets, id):
    transaction = Transaction.objects.get(id=id)
    menu = CartItems.objects.filter(cart_id=transaction.cart)

    context = {
        'transaction': transaction,
        'menu': menu
    }
    return render(requets, 'webadmin/transaction/detail_transaction.html', context)


@login_required(login_url='login')
def ppob(requets):
    ppob = ProductPPOB.objects.all()

    context = {
        'ppob': ppob,
    }
    return render(requets, 'webadmin/ppob/ppob_list.html', context)


@login_required(login_url='login')
def ppob_digi(requets):
    ppob = ProductPPOBDigi.objects.all()

    context = {
        'ppob': ppob,
    }

    return render(requets, 'webadmin/ppob/ppob_digi_list.html', context)


@login_required(login_url='login')
def ppob_postpaid(requets):
    ppob = ProductPPOBPostpaid.objects.all()

    context = {
        'ppob': ppob,
    }
    return render(requets, 'webadmin/ppob/ppob_postpaid.html', context)


@login_required(login_url='login')
def sync_ppob(requets):
    ProductPPOB.objects.all().delete()

    c = connection.cursor()
    c.execute(f'ALTER TABLE webadmin_productppob AUTO_INCREMENT = 1')

    username = "081386356616"
    password = "85160baf89f17e45"
    signature = hashlib.md5((username + password + "pl").encode()).hexdigest()

    data = {
        'status': 'all',
        'username': f'{username}',
        'sign': f'{signature}'
    }

    url = "https://prepaid.iak.dev/api/pricelist"
    headers = {'content-type': 'application/json'}

    data = requests.post(url, data=json.dumps(data), headers=headers).json().get('data')['pricelist']
    for data in data:
        product_code = data.get('product_code')
        product_description = data.get('product_description')
        product_nominal = data.get('product_nominal')
        product_details = data.get('product_details')
        product_price = data.get('product_price')
        product_type = data.get('product_type')
        active_period = data.get('active_period')
        status = data.get('status')
        icon_url = data.get('icon_url')
        last_sync_at = datetime.now()

        if product_price > 90000:
            a = product_price + float(600)
        else:
            a = product_price + float(350)

        productppob = ProductPPOB.objects.create(
            product_code=product_code,
            product_description=product_description,
            product_nominal=product_nominal,
            product_details=product_details,
            product_price=product_price,
            product_type=product_type,
            active_period=active_period,
            status=status,
            icon_url=icon_url,
            POSTKU_price=a,
            last_sync_at=last_sync_at
        )
        productppob.save()

    messages.info(requets, 'Success Sinkronisani Product')
    return HttpResponseRedirect('/ppob')


@login_required(login_url='login')
def sync_ppob_digi(requets):
    ProductPPOBDigi.objects.all().delete()

    c = connection.cursor()
    c.execute(f'ALTER TABLE webadmin_productppobdigi AUTO_INCREMENT = 1')

    username = "mefeyeorX4yW"
    password = "85597426-90a0-50cb-85d0-a82bd1f64bdd"
    signature = hashlib.md5((username + password + "pricelist").encode()).hexdigest()

    data = {
        'cmd': 'prepaid',
        'username': f'{username}',
        'sign': f'{signature}'
    }

    url = "https://api.digiflazz.com/v1/price-list"
    headers = {'content-type': 'application/json'}

    data = requests.post(url, data=json.dumps(data), headers=headers).json().get('data')
    for data in data:
        product_name = data.get('product_name')
        category = data.get('category')
        brand = data.get('brand')
        type = data.get('type')
        seller_name = data.get('seller_name')
        price = data.get('price')
        buyer_sku_code = data.get('buyer_sku_code')
        buyer_product_status = data.get('buyer_product_status')
        seller_product_status = data.get('seller_product_status')
        unlimited_stock = data.get('unlimited_stock')
        stock = data.get('stock')
        multi = data.get('multi')
        start_cut_off = data.get('start_cut_off')
        end_cut_off = data.get('end_cut_off')
        desc = data.get('desc')
        last_sync_at = datetime.now()

        if price > 90000:
            a = price + float(250)
        else:
            a = price + float(150)

        productppobdigi = ProductPPOBDigi.objects.create(
            product_name=product_name,
            category=category,
            brand=brand,
            type=type,
            seller_name=seller_name,
            price=price,
            price_postku=a,
            buyer_sku_code=buyer_sku_code,
            buyer_product_status=buyer_product_status,
            seller_product_status=seller_product_status,
            unlimited_stock=unlimited_stock,
            stock=stock,
            multi=multi,
            start_cut_off=start_cut_off,
            end_cut_off=end_cut_off,
            desc=desc,
            last_sync_at=last_sync_at
        )
        productppobdigi.save()

    messages.info(requets, 'Success Sinkronisani Product')
    return HttpResponseRedirect('/ppob_digi')


@login_required(login_url='login')
def sync_ppob_postpaid(requets):
    ProductPPOBPostpaid.objects.all().delete()

    c = connection.cursor()
    c.execute(f'ALTER TABLE webadmin_productppobpostpaid AUTO_INCREMENT = 1')

    username = "081386356616"
    password = "85160baf89f17e45"
    signature = hashlib.md5((username + password + "pl").encode()).hexdigest()

    data = {
        'commands': 'pricelist-pasca',
        'status': 'all',
        'username': f'{username}',
        'sign': f'{signature}'
    }

    url = "https://testpostpaid.mobilepulsa.net/api/v1/bill/check/"
    headers = {'content-type': 'application/json'}

    data = requests.post(url, data=json.dumps(data), headers=headers).json().get('data')['pasca']
    for data in data:
        code = data.get('code')
        name = data.get('name')
        status = data.get('status')
        fee = data.get('fee')
        komisi = data.get('komisi')
        type = data.get('type')
        last_sync_at = datetime.now()
        a = komisi * float(70) / float(100)
        b = komisi * float(30) / float(100)

        productppob = ProductPPOBPostpaid.objects.create(
            code=code,
            name=name,
            fee=fee,
            komisi=komisi,
            type=type,
            status=status,
            komisi_merchant=a,
            komisi_postku=b,
            last_sync_at=last_sync_at
        )
        productppob.save()

    messages.info(requets, 'Success Sinkronisani Product')
    return HttpResponseRedirect('/ppob_postpaid')


@login_required(login_url='login')
def sync_subs(requets):
    today = datetime.today()
    data = Account.objects.all()

    for a in data:
        active_date = a.subs_date

        try:
            if active_date < today:
                a.is_subs = 0
                a.save()
            else:
                a.is_subs = 1
                a.save()
        except:
            print("")

    messages.info(requets, 'Success Sinkronisani Data Subs')
    return HttpResponseRedirect('/subs')
