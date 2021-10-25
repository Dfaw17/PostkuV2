from django.db.models import Count
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from ..forms import *
from datetime import *
import locale

locale.setlocale(locale.LC_ALL, '')

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

        chart_type_trx = Transaction.objects.filter(created_at__range=[date, date2]).values(
            'payment_type__paymnet').annotate(jumlah_trx=Count('id'))

        chart_brand_ppob = PPOBPrepaidTransaction.objects.filter(created_at__range=[date, date2]).values(
            'brand').annotate(jumlah_trx=Count('id'))
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

        chart_type_trx = Transaction.objects.filter(created_at__range=[today_start, today_end]).values(
            'payment_type__paymnet').annotate(jumlah_trx=Count('id'))

        chart_brand_ppob = PPOBPrepaidTransaction.objects.filter(created_at__range=[today_start, today_end]).values(
            'brand').annotate(jumlah_trx=Count('id'))

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
        'chart_type_trx': chart_type_trx,
        'chart_brand_ppob': chart_brand_ppob,
        'total_nett_income': total_difference_ppob + total_revenue_postku + total_trx_subs,
    }
    return render(requets, 'webadmin/index.html', context)