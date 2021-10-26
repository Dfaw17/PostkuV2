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


@login_required(login_url='login')
def subs(requets):
    account = Account.objects.filter(is_owner=1, is_subs=1)

    context = {
        'account': account,
    }
    return render(requets, 'webadmin/subs/subs_list.html', context)


@login_required(login_url='login')
def absen(requets):
    absen = Absensi.objects.all()

    context = {
        'absen': absen,
    }
    return render(requets, 'webadmin/absen/absen_list.html', context)


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

    if requets.method == 'POST':
        settlement.pic_claim = requets.POST['image']
        settlement.save()
        messages.success(requets, 'Success Upload Image !!!')

    context = {
        'settlement': settlement,
        'data_trx': data_trx,
    }
    return render(requets, 'webadmin/settlement/detail_settlement.html', context)


@login_required(login_url='login')
def request_topup_detail(requets, id):
    rt = ConfirmWallet.objects.get(id=id)
    if requets.method == 'POST':
        rt.reason = requets.POST['reason']
        rt.save()
        messages.success(requets, 'Success Give The Reason !!!')
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
