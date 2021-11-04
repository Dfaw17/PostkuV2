from ..serializers import *
from datetime import *
from django.http import *
from django.core.exceptions import *
from django.db.models import Count
from rest_framework import status
from rest_framework import generics


class Beranda(generics.GenericAPIView):

    def get(self, request, id):
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())

        try:
            toko = Toko.objects.get(id=id)
            check_toko = WalletToko.objects.get(toko_id=id)
            wallets = WalletToko.objects.get(toko_id=id)
            wallet_balance = WalletTokoSerializer(wallets).data
            data_wallet = wallet_balance.get('balance')
        except ObjectDoesNotExist:
            data_wallet = "Wallet Belum Aktif"

        try:
            settlement = Transaction.objects.filter(toko=id, is_settelement=0, payment_type_id=2)
            data_settlement = TransactionSerializer(settlement, many=True).data
            total_settlement = settlement.aggregate(Sum('grand_total'))
            total_data_settlement = total_settlement.get('grand_total__sum')
        except ObjectDoesNotExist:
            total_data_settlement = 0

        transaction = Transaction.objects.filter(toko=id, created_at__range=[today_start, today_end])
        total_trx = transaction.aggregate(Sum('total'))
        total_transaction = total_trx.get('total__sum')
        count_trx = transaction.aggregate(Count('total'))
        cont_transaction = count_trx.get('total__count')

        cart_items = CartItems.objects.filter(toko=id, ordered=1, ordered_at__range=[today_start, today_end])
        sum_menu = cart_items.aggregate(Sum('qty'))
        sum_menu_terjual = sum_menu.get('qty__sum')

        transaction_tunai = Transaction.objects.filter(toko=id, payment_type_id=1,
                                                       created_at__range=[today_start, today_end])
        total_trx_tunai = transaction_tunai.aggregate(Sum('total'))
        total_transaction_tunai = total_trx_tunai.get('total__sum')

        transaction_qris = Transaction.objects.filter(toko=id, payment_type_id=2,
                                                      created_at__range=[today_start, today_end])
        total_trx_qris = transaction_qris.aggregate(Sum('total'))
        total_transaction_qris = total_trx_qris.get('total__sum')

        try:
            report_menu = CartItems.objects.filter(toko_id=id, ordered=1,
                                                   created_at__range=[today_start, today_end]).values(
                'menu__nama').annotate(qty=Sum('qty'), price=Sum('price')).order_by('-qty')
            menu_terlaris = report_menu[0].get('menu__nama')
        except:
            menu_terlaris = ""

        owner_toko = toko.account_set.get(is_owner=1)
        status_subs = owner_toko.is_subs

        data_rekening = owner_toko.no_rekening
        if data_rekening is None:
            status_rekening = False
        else:
            status_rekening = True

        banner = Banner.objects.filter(is_active=1)
        data_banner = ListBannerSerializer(banner, many=True).data

        article = Article.objects.filter(is_active=1).order_by('-id')[:3]
        data_article = ListArticleSerializer(article, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK
        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'wallet': data_wallet,
            'qris': total_data_settlement,
            'total_trx': cont_transaction,
            'pendapatan': total_transaction,
            'trx_tunai': total_transaction_tunai,
            'trx_qris': total_transaction_qris,
            'menu_terjual': sum_menu_terjual,
            'menu_terlaris': menu_terlaris,
            'status_subs': status_subs,
            'status_rekening': status_rekening,
            'data_banner': data_banner,
            'data_article': data_article,
        })


class DetailBanner(generics.GenericAPIView):
    def get(self, request, id):
        banner = Banner.objects.get(id=id)
        data_banner = DetailBannerSerializer(banner).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_banner
        })


class CheckSubs(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')

        toko = Toko.objects.get(id=id_toko)
        owner_toko = toko.account_set.get(is_owner=1)
        subs_date = owner_toko.subs_date
        status_subs = subs_date.date()
        today = datetime.now().date()

        if status_subs is None:
            status_subs = False
            active_untill = None
            msg = "Success found data"
            status_code = status.HTTP_404_NOT_FOUND
        else:
            try:
                if status_subs < today:
                    status_subs = False
                    active_untill = None
                    msg = "Success found data"
                    status_code = status.HTTP_404_NOT_FOUND
                else:
                    status_subs = True
                    active_untill = owner_toko.subs_date
                    msg = "Success found data"
                    status_code = status.HTTP_200_OK
            except:
                status_subs = True
                active_untill = owner_toko.subs_date
                msg = "Success found data"
                status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'status_subs': status_subs,
            'active_untill': active_untill,
        })
