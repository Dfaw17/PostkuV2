from xendit.models.qrcode import QRCodeType

from .serializers import *
import requests
from xendit import *
import hashlib
import json
from datetime import *
import base64

from django.http import *
from django.contrib.auth.models import User
from django.db import connection
from django.core.exceptions import *
from django.db.models import Count

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from random import *
from rest_framework.pagination import PageNumberPagination

global xnd_prod, xnd_dev

xnd_prod = "xnd_production_nfjAk6kENINyOobuWaOujS3aqfT4LwqW8rzAsvwBOSqD28tjJGYTsQRTqZakEPT"
xnd_dev = "xnd_development_27A0zquDKjORXcsXvv3XEnX00BBlwVlR97ZFQIfbA8TPNrZDa4VFaSzIDBUeem"


class Register(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        c = connection.cursor()
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')

        serializer = RegisterSerializer(data=request.data)
        serializerextenduser = ExtendsUserSerializer(data=request.data)
        if serializerextenduser.is_valid(raise_exception=True):
            if serializer.is_valid(raise_exception=True):
                serializerextenduser.save()
                serializer.save()

                content_user = User.objects.raw(f'SELECT * FROM auth_user WHERE email="{email}"')
                for i in content_user:
                    id_user = i.id
                c.execute(f'UPDATE webadmin_account SET user_id="{id_user}" WHERE email="{email}"')
                r = requests.post('http://localhost:8000/api/token', data={'username': username, 'password': password})
                token = r.json().get('access')
                detail_user = Account.objects.get(username=username)
                data_detail_akun = ExtendsUserSerializer(detail_user).data

                return JsonResponse({
                    'msg': "Data successfull created",
                    'status_code': '201',
                    'user': data_detail_akun,
                    'token': token,
                })


class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        r = requests.post('http://localhost:8000/api/token', data={'username': username, 'password': password})
        token = r.json().get('access')

        if token != None:
            detail_user = Account.objects.get(username=username)
            data_detail_akun = ExtendsUserSerializer(detail_user).data
            msg = 'Success Login'
            status_code = status.HTTP_200_OK
        else:
            msg = 'Failed Login'
            data_detail_akun = None
            status_code = status.HTTP_404_NOT_FOUND
        return JsonResponse({
            'status_code': status_code,
            'msg': msg,
            'token': token,
            'data_akun': data_detail_akun
        })


class Logout(APIView):

    def post(self, request):

        username = request.data.get('username')
        try:
            detail_user = Account.objects.get(username=username)
            response = ExtendsUserSerializer(detail_user).data
            msg = "success logout"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            status_code = status.HTTP_404_NOT_FOUND
            msg = "failed logout"
            response = "user not found"

        return JsonResponse({
            'status_code': status_code,
            'msg': msg,
            'data': response
        })


class LaporanBisnis(generics.GenericAPIView):

    def get(self, request):

        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            # Penjualan Kotor
            penjualan_kotor = CartItems.objects.filter(toko=id_toko, ordered=1,
                                                       created_at__range=[date1, date2]).aggregate(Sum('price'))
            if penjualan_kotor.get('price__sum') == None:
                data_penjualan_kotor = 0
            else:
                data_penjualan_kotor = penjualan_kotor.get('price__sum')

            # Pajak
            pajak = Cart.objects.filter(toko=id_toko, ordered=1,
                                        created_at__range=[date1, date2]).aggregate(Sum('total_pajak'))
            if pajak.get('total_pajak__sum') == None:
                data_pajak = 0
            else:
                data_pajak = pajak.get('total_pajak__sum')

            # Service Fee
            sf = Cart.objects.filter(toko=id_toko, ordered=1,
                                     created_at__range=[date1, date2]).aggregate(Sum('total_service_fee'))
            if sf.get('total_service_fee__sum') == None:
                data_sf = 0
            else:
                data_sf = sf.get('total_service_fee__sum')

            # Discount
            disc1 = Cart.objects.filter(toko=id_toko, ordered=1,
                                        created_at__range=[date1, date2]).aggregate(Sum('total_disc'))
            if disc1.get('total_disc__sum') == None:
                data_disc1 = 0
            else:
                data_disc1 = disc1.get('total_disc__sum')

            disc2 = CartItems.objects.filter(toko=id_toko, ordered=1,
                                             created_at__range=[date1, date2]).aggregate(Sum('total_disc'))
            if disc2.get('total_disc__sum') == None:
                data_disc2 = 0
            else:
                data_disc2 = disc2.get('total_disc__sum')
            data_disc = float(data_disc1 + data_disc2)

            # Hpp Item
            hpp = CartItems.objects.filter(toko=id_toko, ordered=1,
                                           created_at__range=[date1, date2]).aggregate(Sum('hpp'))
            if hpp.get('hpp__sum') == None:
                data_hpp = 0
            else:
                data_hpp = hpp.get('hpp__sum')

            # Jumlah Item
            total_item = CartItems.objects.filter(toko=id_toko, ordered=1,
                                                  created_at__range=[date1, date2]).aggregate(Sum('qty'))
            if total_item.get('qty__sum') == None:
                data_total_item = 0
            else:
                data_total_item = total_item.get('qty__sum')

            # Cancel Trx
            cancel_trx = CartItems.objects.filter(toko=id_toko, ordered=1, is_canceled=1,
                                                  created_at__range=[date1, date2]).aggregate(Sum('price'))
            if cancel_trx.get('price__sum') == None:
                data_cancel_trx = 0
            else:
                data_cancel_trx = cancel_trx.get('price__sum')

            # Laba rugi
            laba_rugi = float(data_penjualan_kotor + data_pajak + data_sf) - float(
                data_disc + data_cancel_trx + data_hpp)

            msg = 'Success found data'
            status_code = status.HTTP_200_OK
        else:
            msg = 'Masukan tanggal awal dan tanggal akhir terlebih dahulu'
            status_code = status.HTTP_404_NOT_FOUND
            data_penjualan_kotor = None
            data_pajak = None
            data_sf = None
            data_disc = None
            data_hpp = None
            data_total_item = None
            data_cancel_trx = None
            laba_rugi = None

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data_penjualan_kotor': data_penjualan_kotor,
            'data_pajak': data_pajak,
            'data_service_fee': data_sf,
            'data_disc': data_disc,
            'data_hpp': data_hpp,
            'data_total_item': data_total_item,
            'data_cancel_trx': data_cancel_trx,
            'data_laba_rugi': laba_rugi,
        })


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
        if data_rekening == None:
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


class UpdateProfileOwner(generics.GenericAPIView):

    def put(self, request):
        id_user = request.data.get('id_user')

        akun = Account.objects.get(id=id_user)
        akun.phone = request.data.get("phone", akun.phone)
        akun.address = request.data.get("address", akun.address)
        akun.nama = request.data.get("nama", akun.nama)
        akun.no_rekening = request.data.get("no_rekening", akun.no_rekening)
        akun.jenis_bank = request.data.get("jenis_bank", akun.jenis_bank)
        akun.profile_pic = request.data.get("profile_pic", akun.profile_pic)
        akun.rekening_book_pic = request.data.get("rekening_book_pic", akun.rekening_book_pic)
        akun.is_owner = 1

        akun.save()
        serializer = ExtendsUserSerializer(akun)

        # return Response()
        return JsonResponse({
            'msg': 'Data successfull updated',
            'status_code': status.HTTP_200_OK,
            'data': serializer.data,
        })


class UpdateProfilePegawai(generics.GenericAPIView):

    def put(self, request):
        c = connection.cursor()
        id_user = request.data.get('id_user')
        id_toko = request.data.get('id_toko')
        phone = request.data.get('phone')
        address = request.data.get('address')
        nama = request.data.get('nama')

        toko = Toko.objects.get(id=id_toko)
        owner = toko.account_set.get(is_owner=1)
        subs_date = owner.subs_date.strftime('%Y-%m-%d-%H:%M:%S')

        check = c.execute(f'SELECT * FROM webadmin_account_toko WHERE account_id="{id_user}"')
        if check == 1:
            c.execute(f'UPDATE webadmin_account_toko SET toko_id="{id_toko}" WHERE account_id="{id_user}" ')
            c.execute(
                f'UPDATE webadmin_account SET phone="{phone}", address="{address}", nama="{nama}", is_owner="0", is_subs={owner.is_subs}, subs_date="{subs_date}" WHERE id="{id_user}"')
            detail_user = Account.objects.get(id=id_user)
            data_detail_akun = ExtendsUserSerializer(detail_user).data
        else:
            c.execute(f'INSERT INTO webadmin_account_toko (account_id,toko_id) VALUES ("{id_user}","{id_toko}")')
            c.execute(
                f'UPDATE webadmin_account SET phone="{phone}", address="{address}", nama="{nama}", is_owner="0", is_subs={owner.is_subs}, subs_date="{subs_date}" WHERE id="{id_user}"')
            detail_user = Account.objects.get(id=id_user)
            data_detail_akun = ExtendsUserSerializer(detail_user).data

        return JsonResponse({
            'msg': 'Data successfull updated',
            'status_code': status.HTTP_200_OK,
            'data': data_detail_akun,
        })


class DetailAccount(generics.GenericAPIView):
    def get(self, request):
        try:
            id = request.GET.get('id_user')
            account = Account.objects.get(id=id)
            data_akun = ExtendsUserSerializer(account).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id"
            data_akun = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_akun
        })


class CRUDKategoriMenu(generics.GenericAPIView):

    def get(self, request):
        id_toko = request.GET.get('id_toko')
        kategori_menu = KategoriMenu.objects.filter(toko_id=id_toko, is_active=1)
        data_kategori_menu_toko = KategoriMenuSerializer(kategori_menu, many=True).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_kategori_menu_toko
        })

    def post(self, request):

        serializer = KategoriMenuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({
            'msg': "data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })

    def put(self, request):

        c = connection.cursor()
        id_kategori_menu = request.data.get('id_kategori_menu')

        try:
            c.execute(f'UPDATE webadmin_kategorimenu SET is_active=0 WHERE id="{id_kategori_menu}"')
            msg = "Data successfull deleted"
        except ObjectDoesNotExist:
            msg = "Data Toko Nof Found"

        return JsonResponse({
            'msg': msg,
            'status_code': status.HTTP_200_OK
        })

    def patch(self, request):

        id_kategori_menu = request.data.get('id_kategori_menu')
        kategori_menu = KategoriMenu.objects.get(id=id_kategori_menu)

        kategori_menu.label = request.data.get("label", kategori_menu.label)

        kategori_menu.save()
        serializer = KategoriMenuSerializer(kategori_menu)

        return JsonResponse({
            'msg': "Data successfull updated",
            'status_code': status.HTTP_200_OK,
            'data': serializer.data,
        })


class CreateSaranKritik(generics.GenericAPIView):
    def post(self, request):
        serializer = KritikSaranSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({
            'msg': "Data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })


class DetailKategoriMenu(generics.GenericAPIView):
    def get(self, request, id):
        try:
            kat_menu = KategoriMenu.objects.get(id=id)
            data_kat_menu = KategoriMenuSerializer(kat_menu).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id"
            data_kat_menu = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_kat_menu
        })


class CartAPIV2(generics.GenericAPIView):
    def post(self, request):
        data_menu = request.data.get('menu')

        cart = CartSerializer(data=request.data)
        cart.is_valid(raise_exception=True)
        cart.save()
        for i in data_menu:
            cart_item = CartItemsSerializer(data={
                'cart': cart.data.get('id'),
                'menu': i.get('idmenu'),
                'qty': i.get('qty'),
                'discount': i.get('dics')

            })
            cart_item.is_valid(raise_exception=True)
            cart_item.save()

        print(cart.data.get('id'))

        cart = Cart.objects.get(id=cart.data.get('id'))
        data_cart = CartSerializer(cart).data

        return JsonResponse({
            'msg': "Data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data_cart': data_cart,
        })

    def patch(self, request):
        id_cart = request.data.get('id_cart')
        cart = Cart.objects.get(id=id_cart)

        try:
            discount = Discount.objects.get(id=request.data.get('discount'))
            cart.discount = discount
        except:
            discount = None
            cart.discount = discount
            cart.total_disc = 0

        try:
            table = TableManagement.objects.get(id=request.data.get('table'))
            cart.table = table
        except:
            table = None
            cart.table = table

        try:
            pajak = Pajak.objects.get(id=request.data.get('pajak'))
            cart.pajak = pajak
        except:
            pajak = None
            cart.pajak = pajak
            cart.total_pajak = 0

        try:
            pelanggan = Pelanggan.objects.get(id=request.data.get('pelanggan'))
            cart.pelanggan = pelanggan
        except:
            pelanggan = None
            cart.pelanggan = pelanggan

        try:
            tipe_order = OrderType.objects.get(id=request.data.get('tipe_order'))
            cart.tipe_order = tipe_order
        except:
            tipe_order = None
            cart.tipe_order = tipe_order

        try:
            label_order = LabelOrder.objects.get(id=request.data.get('label_order'))
            cart.label_order = label_order
        except:
            label_order = None
            cart.label_order = label_order

        id_service_fee = request.data.get('service_fee')
        cart.service_fee.clear()
        cart.save()
        for i in id_service_fee:
            cart.service_fee.add(i)
            cart.save()
        cart.save()

        return JsonResponse({
            'msg': "Data successfull updated",
            'status_code': status.HTTP_200_OK,
        })


class CartItemAPIV2(generics.GenericAPIView):
    def patch(self, request):
        id_cart_item = request.data.get('id_cart_item')
        qty = request.data.get('qty')
        cart_item = CartItems.objects.get(id=id_cart_item)

        if qty == 0:
            cart_item.delete()
        else:
            try:
                discount = Discount.objects.get(id=request.data.get('discount'))
                cart_item.discount = discount
            except:
                discount = None
                cart_item.discount = discount
                cart_item.total_disc = 0

            try:
                cart_item.qty = request.data.get('qty')
            except:
                cart_item.qty = 0

            cart_item.save()

        return JsonResponse({
            'msg': "Data successfull updated",
            'status_code': status.HTTP_200_OK,
        })


class CartAPI(generics.GenericAPIView):

    def get(self, request):
        id_toko = request.GET.get('id_toko')
        cart = Cart.objects.filter(toko_id=id_toko, ordered=False, total_item__isnull=False)

        data_cart = CartSerializer(cart, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_cart,
        })

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({
            'msg': "Data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })

    def delete(self, request):

        id_cart = request.GET.get('id_cart')

        try:
            cart = Cart.objects.get(id=id_cart)
            cart.delete()
            msg = "Data successfull deleted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Deleted Failed Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })

    def patch(self, request):

        id_cart = request.data.get('id_cart')
        cart = Cart.objects.get(id=id_cart)

        cart.nama_cart = request.data.get("nama_cart", cart.nama_cart)

        cart.save()
        serializer = CartSerializer(cart)

        return JsonResponse({
            'msg': 'Data successfull saved',
            'status_code': status.HTTP_200_OK,
            'data': serializer.data,
        })


class CartAPIDetail(APIView):

    def get(self, request, id):
        cart = Cart.objects.get(id=id)
        cart_items = CartItems.objects.filter(cart_id=id)

        data_cart = CartSerializer(cart).data
        data_cart_items = CartItemsSerializer(cart_items, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'message': msg,
            'status_code': status_code,
            'data_cart': data_cart,
            'data_cart_items': data_cart_items,
            'jumlah_items': data_cart.get('total_item'),
        })


class CartItem(generics.GenericAPIView):

    def post(self, request):

        id_cart = request.data.get('cart')
        id_menu = request.data.get('menu')

        try:
            cart_items = CartItems.objects.get(cart_id=id_cart, menu_id=id_menu)
            cart_items.qty = float(cart_items.qty) + float(1)
            cart_items.save()
        except ObjectDoesNotExist:
            serializer = CartItemsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return JsonResponse({
            'msg': "Success Insert Menu To Cart",
            'status_code': status.HTTP_201_CREATED,
        })

    def delete(self, request):
        id_cart_item = request.GET.get('id_cart_item')

        try:
            cart_item = CartItems.objects.get(id=id_cart_item)
            cart_item.delete()
            msg = "Data successfull deleted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Deleted Failed Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })

    def patch(self, request):
        id_cart_item = request.data.get('id_cart_item')
        qty = request.data.get('qty')

        try:
            cart_items = CartItems.objects.get(id=id_cart_item)
            cart_items.qty = float(qty)
            cart_items.save()

            if cart_items.qty == 0.0:
                cart_items.delete()
                msg = "Success Updated"
                resp_code = status.HTTP_200_OK
            else:
                msg = "Success Updated"
                resp_code = status.HTTP_200_OK

        except ObjectDoesNotExist:
            msg = "Updated Failed Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })


class Transactions(generics.GenericAPIView):

    def post(self, request):

        try:
            id_cart = request.data.get('cart')
            cart = Cart.objects.get(id=id_cart)
            if cart.ordered == 1:
                data = ""
                status_code = status.HTTP_400_BAD_REQUEST
                msg = "failed cart has been ordered"
            else:
                serializer = TransactionSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                data = serializer.data
                status_code = status.HTTP_201_CREATED
                msg = "Data successfull created"
        except ObjectDoesNotExist:
            data = ""
            status_code = status.HTTP_400_BAD_REQUEST
            msg = "failed cart not found"

        return JsonResponse({
            'message': msg,
            'status_code': status_code,
            'data': data,
        })

    def get(self, request):

        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            transaction = Transaction.objects.filter(toko=id_toko, created_at__range=[date1, date2]).order_by(
                '-created_at')
        else:
            transaction = Transaction.objects.filter(toko=id_toko).order_by(
                '-created_at')

        data_trx = TransactionSerializer(transaction, many=True).data

        total_trx = transaction.aggregate(Sum('grand_total'))
        total_transaction = total_trx.get('grand_total__sum')

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_trx,
            'total': total_transaction,
        })

    def patch(self, request):
        reff_code = request.data.get('reff_code')

        trx = Transaction.objects.get(reff_code=reff_code)
        trx.is_canceled = 1
        trx.save()

        cart = Cart.objects.get(id=trx.cart.id)
        cart.is_canceled = 1
        cart.save()

        cart_item = CartItems.objects.filter(cart_id=trx.cart.id)
        for i in cart_item:
            i.is_canceled = 1
            i.save()

        msg = "Data successfull canceled"

        return JsonResponse({
            'msg': msg,
        })


class TransactionPPOB(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        transaction = PPOBPrepaidTransaction.objects.filter(toko=id_toko, is_refunded=None,
                                                            created_at__range=[date1, date2]).order_by('-created_at')
        data_trx = PPOBPrepaidTransactionSerializer(transaction, many=True).data

        transaction_total = PPOBPrepaidTransaction.objects.filter(toko=id_toko, is_refunded=None,
                                                                  created_at__range=[date1, date2]).order_by(
            '-created_at').aggregate(Sum('price_postku'))
        data_transaction_jumlah = transaction_total.get('price_postku__sum')

        transaction_count = PPOBPrepaidTransaction.objects.filter(toko=id_toko, is_refunded=None,
                                                                  created_at__range=[date1, date2]).aggregate(
            Count('id'))
        data_transaction_count = transaction_count.get('id__count')

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'total_transaksi': data_transaction_jumlah,
            'jumlah_transaksi': data_transaction_count,
            'data': data_trx,
        })

    def put(self, request):
        ref_id = request.data.get('ref_id')
        wallet_id = request.data.get('wallet_id')

        transaction = PPOBPrepaidTransaction.objects.get(ref_id=ref_id)
        wallet = WalletToko.objects.get(id=wallet_id)

        if transaction.status == 'Gagal' and transaction.is_refunded != 1:
            transaction.is_refunded = 1
            transaction.save()

            # create wallet trx
            years = datetime.today().strftime('%Y')
            mounth = datetime.today().strftime('%m')
            day = datetime.today().strftime('%d')
            hours = datetime.today().strftime('%H')
            munites = datetime.today().strftime('%M')
            seconds = datetime.today().strftime('%S')
            notes = f'Wallet {wallet.wallet_code} Success Refund Balance Rp.{transaction.price_postku} For PPOB Product {transaction.desc} at {years}-{mounth}-{day} {hours}:{munites}:{seconds}'

            trx_wallet = TrxWallet(wallet_code=wallet.wallet_code, type=3, adjustment_balance=transaction.price_postku,
                                   note=notes,
                                   wallet_id=wallet_id)
            trx_wallet.save()

            msg = "Data successfull refunded"
            status_code = status.HTTP_200_OK
        else:
            msg = "Failed Refund Transaksi (Bukan transaksi gagal / transaksi sudah di refund)"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
        })


class DetailTransactions(generics.GenericAPIView):

    def get(self, request, id):
        transaction = Transaction.objects.get(reff_code=id)
        data_trx = TransactionSerializer(transaction).data

        id_cart = transaction.cart.id
        cart = Cart.objects.get(id=id_cart)
        data_cart = CartSerializer(cart).data

        cart_items = CartItems.objects.filter(cart_id=id_cart)
        data_cart_items = CartItemsSerializer(cart_items, many=True).data

        id_pegawai = transaction.pegawai.id
        pegawai = Account.objects.get(id=id_pegawai)
        data_pegawai = ExtendsUserSerializer(pegawai).data

        id_toko = transaction.toko.id
        toko = Toko.objects.get(id=id_toko)
        data_toko = TokoSerializer(toko).data

        if cart.pajak != None:
            pajak = Pajak.objects.get(id=cart.pajak.id)
            data_pajak = PajakSerializer(pajak).data
        else:
            data_pajak = None

        if cart.service_fee != None:
            service_fee = cart.service_fee.all()
            data_sf = ServiceFeeSerializer(service_fee, many=True).data
        else:
            data_sf = None

        if cart.discount != None:
            disc = Discount.objects.get(id=cart.discount.id)
            data_disc = DiscountSerializer(disc).data
        else:
            data_disc = None

        if cart.tipe_order != None:
            tipe_order = OrderType.objects.get(id=cart.tipe_order.id)
            data_tipe_order = TipeOrderSerializer(tipe_order).data
        else:
            data_tipe_order = None

        if cart.label_order != None:
            label_order = LabelOrder.objects.get(id=cart.label_order.id)
            data_label_order = LabelOrderSerializer(label_order).data
        else:
            data_label_order = None

        if cart.table != None:
            table = TableManagement.objects.get(id=cart.table.id)
            data_table = TableManagementSerializer(table).data
        else:
            data_table = None

        if cart.pelanggan != None:
            pelanggan = Pelanggan.objects.get(id=cart.pelanggan.id)
            data_pelanggan = PelangganSerializer(pelanggan).data
        else:
            data_pelanggan = None

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data_transaksi': data_trx,
            'data_cart': data_cart,
            'data_cart_items': data_cart_items,
            'data_pegawai': data_pegawai,
            'data_toko': data_toko,
            'data_pajak': data_pajak,
            'data_service_fee': data_sf,
            'data_disc': data_disc,
            'data_tipe_order': data_tipe_order,
            'data_label_order': data_label_order,
            'data_table': data_table,
            'data_pelanggan': data_pelanggan,
        })


class ReportByMenu(generics.GenericAPIView):
    def post(self, request):
        id_toko = request.data.get('id_toko')
        date1 = request.data.get('date1')
        date2 = request.data.get('date2')

        if date1 and date2 != "":
            report_menu = CartItems.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2]).values(
                'menu__nama').annotate(
                qty=Sum('qty'), price=Sum('price')).order_by('-qty')
        else:
            report_menu = CartItems.objects.filter(toko_id=id_toko, ordered=1).values('menu__nama').annotate(
                qty=Sum('qty'), price=Sum('price')).order_by('-qty')

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_menu),
        })


class ReportByMenuKategori(generics.GenericAPIView):
    def post(self, request):
        id_toko = request.data.get('id_toko')
        date1 = request.data.get('date1')
        date2 = request.data.get('date2')

        if date1 and date2 != "":
            report_menu_kategori = CartItems.objects.filter(toko_id=id_toko, ordered=1,
                                                            created_at__range=[date1, date2]).values(
                'menu_kategori__label').annotate(qty=Sum('qty'), price=Sum('price')).order_by('-qty')
        else:
            report_menu_kategori = CartItems.objects.filter(toko_id=id_toko, ordered=1).values(
                'menu_kategori__label').annotate(qty=Sum('qty'), price=Sum('price')).order_by('-qty')

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_menu_kategori),
        })


class ReportByEmployee(generics.GenericAPIView):
    def post(self, request):
        id_toko = request.data.get('id_toko')
        date1 = request.data.get('date1')
        date2 = request.data.get('date2')

        if date1 and date2 != "":
            report_employee = Transaction.objects.filter(toko_id=id_toko, created_at__range=[date1, date2]).values(
                'pegawai__nama').annotate(jumlah_trx=Count('id'), nominal_trx=Sum('grand_total'))
        else:
            report_employee = Transaction.objects.filter(toko_id=id_toko).values('pegawai__nama').annotate(
                jumlah_trx=Count('id'), nominal_trx=Sum('grand_total'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_employee),
        })


class ReportByDisc(generics.GenericAPIView):
    def post(self, request):
        id_toko = request.data.get('id_toko')
        date1 = request.data.get('date1')
        date2 = request.data.get('date2')

        if date1 and date2 != "":
            report_disc = Cart.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                              discount_id__isnull=False).values(
                'discount__nama').annotate(jumlah_trx=Count('id'))
        else:
            report_disc = Cart.objects.filter(toko_id=id_toko, ordered=1, discount_id__isnull=False).values(
                'discount__nama').annotate(jumlah_trx=Count('id'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_disc),
        })


class ReportByTable(generics.GenericAPIView):
    def post(self, request):
        id_toko = request.data.get('id_toko')
        date1 = request.data.get('date1')
        date2 = request.data.get('date2')

        if date1 and date2 != "":
            report_table = Cart.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                               table_id__isnull=False).values(
                'table__nama').annotate(jumlah_trx=Count('id'))
        else:
            report_table = Cart.objects.filter(toko_id=id_toko, ordered=1, table_id__isnull=False).values(
                'table__nama').annotate(jumlah_trx=Count('id'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_table),
        })


class ReportByPelanggan(generics.GenericAPIView):
    def post(self, request):
        id_toko = request.data.get('id_toko')
        date1 = request.data.get('date1')
        date2 = request.data.get('date2')

        if date1 and date2 != "":
            report_pelanggan = Cart.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                                   pelanggan_id__isnull=False).values(
                'pelanggan__nama').annotate(jumlah_trx=Count('id'))
        else:
            report_pelanggan = Cart.objects.filter(toko_id=id_toko, ordered=1, pelanggan_id__isnull=False).values(
                'pelanggan__nama').annotate(jumlah_trx=Count('id'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_pelanggan),
        })


class ReportByOrderType(generics.GenericAPIView):
    def post(self, request):
        id_toko = request.data.get('id_toko')
        date1 = request.data.get('date1')
        date2 = request.data.get('date2')

        if date1 and date2 != "":
            report_order_tipe = Cart.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                                    tipe_order_id__isnull=False).values(
                'tipe_order__nama').annotate(jumlah_trx=Count('id'))
        else:
            report_order_tipe = Cart.objects.filter(toko_id=id_toko, ordered=1, tipe_order_id__isnull=False).values(
                'tipe_order__nama').annotate(jumlah_trx=Count('id'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_order_tipe),
        })


class ReportByLabelOrder(generics.GenericAPIView):
    def post(self, request):
        id_toko = request.data.get('id_toko')
        date1 = request.data.get('date1')
        date2 = request.data.get('date2')

        if date1 and date2 != "":
            report_order_label = Cart.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                                     label_order_id__isnull=False).values(
                'label_order__nama').annotate(jumlah_trx=Count('id'))
        else:
            report_order_label = Cart.objects.filter(toko_id=id_toko, ordered=1, label_order_id__isnull=False).values(
                'label_order__nama').annotate(jumlah_trx=Count('id'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_order_label),
        })


class XenditQris(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        cart_code = request.data.get('cart_code')
        amount = request.data.get('amount')

        api_key = xnd_prod
        xendit_instance = Xendit(api_key=api_key)
        QRCode = xendit_instance.QRCode

        qriss = QRCode.create(
            external_id=cart_code,
            type=QRCodeType.DYNAMIC,
            callback_url="http://13.213.192.212:8000/api/qris/callback",
            amount=amount,
        )

        sample_string = qriss.qr_string
        sample_string_bytes = sample_string.encode("ascii")

        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_string = base64_bytes.decode("ascii")

        datas = {
            "id": qriss.id,
            "external_id": qriss.external_id,
            "amount": qriss.amount,
            "description": "",
            "qr_string": qriss.qr_string,
            "callback_url": qriss.callback_url,
            "type": qriss.type,
            "status": qriss.status,
            "created": qriss.created,
            "updated": qriss.updated,
            "metadata": None
        }

        return JsonResponse({
            'msg': 'Data successfull created',
            'status_code': status.HTTP_201_CREATED,
            'base_64': base64_string,
            'data': datas,
        })

    def get(self, request, id):
        api_key = xnd_prod
        xendit_instance = Xendit(api_key=api_key)
        QRCode = xendit_instance.QRCode

        cart_code = id

        qriss = QRCode.get_by_ext_id(
            external_id=cart_code,
        )
        sample_string = qriss.qr_string
        sample_string_bytes = sample_string.encode("ascii")

        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_string = base64_bytes.decode("ascii")

        # return HttpResponse(qrcode)
        datas = {
            "id": qriss.id,
            "external_id": qriss.external_id,
            "amount": qriss.amount,
            "description": "",
            "qr_string": qriss.qr_string,
            "callback_url": qriss.callback_url,
            "type": qriss.type,
            "status": qriss.status,
            "created": qriss.created,
            "updated": qriss.updated,
            "metadata": None
        }
        return JsonResponse({
            'msg': 'Success found data',
            'status_code': status.HTTP_200_OK,
            'base_64': base64_string,
            'data': datas,
        })


class XenditCallback(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):

        external_id = request.data.get('qr_code')['external_id']
        amount = request.data.get('amount')
        status = request.data.get('status')
        event = request.data.get('event')

        c = connection.cursor()
        c.execute(
            f'INSERT INTO webadmin_callbackxendit (event,amount,external_id,status) VALUES ("{event}","{amount}","{external_id}","{status}")')

        return JsonResponse({
            'msg': "data successfull post",
        })

    def get(self, request):
        cart_code = request.GET.get('cart_code')
        amount = request.GET.get('amount')

        try:
            callback = CallbackXendit.objects.get(external_id=cart_code, amount=amount)
            data = XenditCallbackSerializer(callback).data
            msg = "Success found data"
        except ObjectDoesNotExist:
            data = None
            msg = "Qris Belum Dibayar"

        return JsonResponse({
            'message': msg,
            'status_code': status.HTTP_200_OK,
            'data': data,
        })


class CreateSettlement(generics.GenericAPIView):
    def post(self, request):
        serializer = SettlementnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data_settelemnt = serializer.data.get('data')
        for i in data_settelemnt:
            data_trx = Transaction.objects.get(id=i)
            data_trx.is_settelement = 1
            data_trx.save()

        return JsonResponse({
            'msg': "Data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })

    def get(self, request):
        id_toko = request.GET.get('id_toko')

        settlement = Transaction.objects.filter(toko=id_toko, is_settelement=0, payment_type_id=2)
        data_settlement = TransactionSerializer(settlement, many=True).data

        total_settlement = settlement.aggregate(Sum('grand_total'))
        total_data_settlement = total_settlement.get('grand_total__sum')

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_settlement,
            'total': total_data_settlement,
        })


class Historyettlement(generics.GenericAPIView):

    def get(self, request):
        id_toko = request.GET.get('id_toko')
        status_trx = request.GET.get('status_trx')
        print(status_trx)

        if status_trx == '1':
            settlement = Settlement.objects.filter(toko=id_toko, status_settelement=1)
            data_settlement = SettlementnSerializer(settlement, many=True).data
        else:
            settlement = Settlement.objects.filter(toko=id_toko, status_settelement=0)
            data_settlement = SettlementnSerializer(settlement, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_settlement
        })


class DetailHistoryettlement(generics.GenericAPIView):
    def get(self, request, id):
        settlement = Settlement.objects.get(id=id)
        data_settlement = SettlementnSerializer(settlement).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_settlement
        })


class InsertPajak(generics.GenericAPIView):
    def patch(self, request):
        try:
            id_cart = request.data.get('id_cart')
            id_pajak = request.data.get('id_pajak')

            cart = Cart.objects.get(id=id_cart)
            cart.pajak_id = id_pajak
            cart.save()

            msg = "Data successfull inserted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Insert Pajak Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })

    def delete(self, request):
        try:
            id_cart = request.GET.get('id_cart')
            cart = Cart.objects.get(id=id_cart)
            cart.pajak_id = None
            cart.total_pajak = 0
            cart.save()

            msg = "Data successfull deleted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Delete Pajak Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })


class InsertServiceFee(generics.GenericAPIView):
    def patch(self, request):
        try:
            id_cart = request.data.get('id_cart')
            id_service_fee = request.data.get('id_service_fee')

            cart = Cart.objects.get(id=id_cart)

            cart.service_fee.clear()
            cart.save()

            for i in id_service_fee:
                cart.service_fee.add(i)
                cart.save()

            msg = "Data successfull inserted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Insert Service Fee Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })

    # def delete(self, request):
    #     try:
    #         id_cart = request.data.get('id_cart')
    #         cart = Cart.objects.get(id=id_cart)
    #         cart.pajak_id = None
    #         cart.total_pajak = 0
    #         cart.save()
    #
    #         msg = "Success Delete Pajak"
    #         resp_code = status.HTTP_200_OK
    #     except ObjectDoesNotExist:
    #         msg = "Failed Delete Pajak Not Found"
    #         resp_code = status.HTTP_404_NOT_FOUND
    #
    #     return JsonResponse({
    #         'msg': msg,
    #         'status_code': resp_code,
    #     })


class InsertDiscount(generics.GenericAPIView):
    def patch(self, request):
        try:
            id_cart = request.data.get('id_cart')
            discount = request.data.get('discount')
            cart = Cart.objects.get(id=id_cart)

            cart.discount_id = discount
            cart.save()

            msg = "Data successfull inserted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Insert Voucher Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })

    def delete(self, request):
        try:
            id_cart = request.GET.get('id_cart')
            cart = Cart.objects.get(id=id_cart)
            cart.discount_id = None
            cart.total_disc = 0
            cart.save()

            msg = "Data successfull deleted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Delete Voucher Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })


class InsertDiscountCartItem(generics.GenericAPIView):
    def patch(self, request):
        try:
            id_cart_item = request.data.get('id_cart_item')
            discount = request.data.get('discount')
            cart_item = CartItems.objects.get(id=id_cart_item)

            cart_item.discount_id = discount
            cart_item.save()

            msg = "Data successfull inserted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Insert Voucher Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })

    def delete(self, request):
        try:
            id_cart_item = request.GET.get('id_cart_item')
            cart_item = CartItems.objects.get(id=id_cart_item)
            cart_item.discount_id = None
            cart_item.total_disc = 0
            cart_item.save()

            msg = "Data successfull deleted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Delete Voucher Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })


class CRUDDiscount(generics.GenericAPIView):
    def get(self, request):
        id = request.GET.get('id_toko')
        discount = Discount.objects.filter(toko=id, is_active=1)
        data_discount_toko = DiscountSerializer(discount, many=True).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_discount_toko
        })

    def post(self, request):

        serializer = DiscountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({
            'msg': "Data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })

    def put(self, request):

        c = connection.cursor()
        id_discount = request.data.get('id_discount')

        try:
            c.execute(f'UPDATE webadmin_discount SET is_active=0 WHERE id="{id_discount}"')
            msg = "Data successfull deleted"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Data Toko Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'status_code': status_code,
            'msg': msg,
        })

    def patch(self, request):

        id_discount = request.data.get('id_discount')
        disc = Discount.objects.get(id=id_discount)

        disc.nama = request.data.get("nama", disc.nama)
        disc.type = request.data.get("type", disc.type)
        disc.nominal = request.data.get("nominal", disc.nominal)

        disc.save()
        serializer = DiscountSerializer(disc).data
        msg = "Data successfull updated"

        return JsonResponse({
            'msg': msg,
            'status_code': status.HTTP_200_OK,
            'data': serializer,
        })


class CRUDPajak(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        pajak = Pajak.objects.filter(toko=id_toko, is_active=1)
        data_pajak_toko = PajakSerializer(pajak, many=True).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_pajak_toko
        })

    def post(self, request):

        serializer = PajakSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({
            'msg': "Data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })

    def put(self, request):

        c = connection.cursor()
        id_pajak = request.data.get('id_pajak')

        try:
            c.execute(f'UPDATE webadmin_pajak SET is_active=0 WHERE id="{id_pajak}"')
            msg = "Data successfull deleted"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Data Toko Nof Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
        })

    def patch(self, request):

        id_pajak = request.data.get('id_pajak')
        pajak = Pajak.objects.get(id=id_pajak)

        pajak.nama = request.data.get("nama", pajak.nama)
        pajak.type = request.data.get("type", pajak.type)
        pajak.nominal = request.data.get("nominal", pajak.nominal)

        pajak.save()
        serializer = PajakSerializer(pajak).data
        msg = "Data successfull updated"

        return JsonResponse({
            'msg': msg,
            'status_code': status.HTTP_200_OK,
            'data': serializer,
        })


class CRUDServiceFee(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        sf = ServiceFee.objects.filter(toko=id_toko, is_active=1)
        data_sf_toko = ServiceFeeSerializer(sf, many=True).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_sf_toko
        })

    def post(self, request):

        serializer = ServiceFeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({
            'msg': "Data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })

    def put(self, request):

        c = connection.cursor()
        id_service_fee = request.data.get('id_service_fee')

        try:
            c.execute(f'UPDATE webadmin_servicefee SET is_active=0 WHERE id="{id_service_fee}"')
            msg = "Data successfull deleted"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Data Toko Nof Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
        })

    def patch(self, request):

        id_sf = request.data.get('id_service_fee')
        sf = ServiceFee.objects.get(id=id_sf)

        sf.nama = request.data.get("nama", sf.nama)
        sf.nominal = request.data.get("nominal", sf.nominal)

        sf.save()
        serializer = ServiceFeeSerializer(sf).data
        msg = "Success Update Pajak"

        return JsonResponse({
            'msg': msg,
            'data': serializer,
        })


class DetailDiscount(generics.GenericAPIView):
    def get(self, request, id):
        try:
            disc = Discount.objects.get(id=id)
            data_disc = DiscountSerializer(disc).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id"
            data_disc = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_disc
        })


class DetailPajak(generics.GenericAPIView):
    def get(self, request, id):
        try:
            pajak = Pajak.objects.get(id=id)
            data_pajak = PajakSerializer(pajak).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id"
            data_pajak = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_pajak
        })


class DetailServiceFee(generics.GenericAPIView):
    def get(self, request, id):
        try:
            sf = ServiceFee.objects.get(id=id)
            data_sf = ServiceFeeSerializer(sf).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id"
            data_sf = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_sf
        })


class CRUDTableManagement(generics.GenericAPIView):
    def get(self, request, ):
        id = request.GET.get('id_toko')
        table = TableManagement.objects.filter(toko=id, is_active=1)
        data_table_toko = TableManagementSerializer(table, many=True).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_table_toko
        })

    def post(self, request):

        serializer = TableManagementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({
            'msg': "Data successfull created",
            'status': status.HTTP_201_CREATED,
            'data': serializer.data,
        })

    def put(self, request):

        c = connection.cursor()
        id_table = request.data.get('id_table')

        try:
            c.execute(f'UPDATE webadmin_tablemanagement SET is_active=0 WHERE id="{id_table}"')
            msg = "Data successfull deleted"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Data Table Nof Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
        })

    def patch(self, request):

        id_table = request.data.get('id_table')
        table = TableManagement.objects.get(id=id_table)

        table.nama = request.data.get("nama", table.nama)
        table.note = request.data.get("note", table.note)

        table.save()
        serializer = TableManagementSerializer(table)

        return JsonResponse({
            'msg': 'Data successfull updated',
            'status_code': status.HTTP_200_OK,
            'data': serializer.data,
        })


class DetailTableManagement(generics.GenericAPIView):
    def get(self, request, id):
        try:
            table = TableManagement.objects.get(id=id)
            data_table = TableManagementSerializer(table).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id"
            data_table = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_table
        })


class InsertTable(generics.GenericAPIView):
    def patch(self, request):
        try:
            id_cart = request.data.get('id_cart')
            table = request.data.get('table')
            cart = Cart.objects.get(id=id_cart)
            meja = TableManagement.objects.get(id=table)

            cart.table = meja
            cart.save()

            msg = "Data successfull booked"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Booked Table Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })

    def delete(self, request):
        try:
            id_cart = request.GET.get('id_cart')
            cart = Cart.objects.get(id=id_cart)
            cart.table_id = None
            cart.save()

            msg = "Data successfull deleted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Delete Table Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })


class CRUDPelanggan(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        pelanggan = Pelanggan.objects.filter(toko_id=id_toko, is_active=1)
        data_pelangaan_toko = PelangganSerializer(pelanggan, many=True).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_pelangaan_toko
        })

    def post(self, request):

        serializer = PelangganSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({
            'msg': "Data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })

    def put(self, request):

        c = connection.cursor()
        id_pelanggan = request.data.get('id_pelanggan')

        try:
            c.execute(f'UPDATE webadmin_pelanggan SET is_active=0 WHERE id="{id_pelanggan}"')
            msg = "Success Deleted Pelanggan"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Data Table Nof Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
        })

    def patch(self, request):

        id_pelanggan = request.data.get('id_pelanggan')
        pelanggan = Pelanggan.objects.get(id=id_pelanggan)

        pelanggan.nama = request.data.get("nama", pelanggan.nama)
        pelanggan.phone = request.data.get("phone", pelanggan.phone)
        pelanggan.email = request.data.get("email", pelanggan.email)
        pelanggan.is_active = 1

        pelanggan.save()
        serializer = PelangganSerializer(pelanggan)

        return Response(serializer.data)


class DetailPelanggan(generics.GenericAPIView):
    def get(self, request, id):
        try:
            pelanggan = Pelanggan.objects.get(id=id)
            data_pelanggan = PelangganSerializer(pelanggan).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id"
            data_pelanggan = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_pelanggan
        })


class InsertPelanggan(generics.GenericAPIView):
    def patch(self, request):
        try:
            id_cart = request.data.get('id_cart')
            cust = request.data.get('pelanggan')

            cart = Cart.objects.get(id=id_cart)
            pelanggan = Pelanggan.objects.get(id=cust)

            cart.pelanggan = pelanggan
            cart.save()

            msg = "Data successfull inserted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Insert Customer Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })

    def delete(self, request):
        try:
            id_cart = request.GET.get('id_cart')
            cart = Cart.objects.get(id=id_cart)
            cart.pelanggan_id = None
            cart.save()

            msg = "Data successfull deleted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Delete Table Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })


class Absen(generics.GenericAPIView):
    def post(self, request):
        user = request.data.get("user")

        check = Absensi.objects.filter(user=user).last()
        data_check = AbsenSerializer(check).data

        if data_check.get("user") == None:
            serializer = AbsenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            absen = Absensi.objects.get(id=serializer.data.get('id'))
            absen.pic1 = request.data.get("foto", absen.pic1)
            absen.time1 = datetime.now()
            absen.save()
            return JsonResponse({
                'msg': "Success Absen",
            })

        if data_check.get("time1") != None and data_check.get("time2") != None:
            serializer = AbsenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            absen = Absensi.objects.get(id=serializer.data.get('id'))
            absen.pic1 = request.data.get("foto", absen.pic1)
            absen.time1 = datetime.now()
            absen.save()
        elif data_check.get("time1") != None and data_check.get("time2") == None:
            absen = Absensi.objects.get(id=data_check.get("id"))
            absen.pic2 = request.data.get("foto", absen.pic1)
            absen.time2 = datetime.now()
            absen.save()

        return JsonResponse({
            'msg': "Data successfull inserted",
            'status_code': status.HTTP_200_OK,
        })

    def get(self, request):
        id = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            absen = Absensi.objects.filter(toko=id, created_at__range=[date1, date2]).order_by(
                '-created_at')
        else:
            absen = Absensi.objects.filter(toko=id).order_by(
                '-created_at')

        data_absensi_toko = AbsenSerializer(absen, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_absensi_toko
        })


class CheckAbsen(generics.GenericAPIView):
    def get(self, request, id):
        absen = Absensi.objects.filter(user_id=id).last()

        try:
            if absen.time2 != None:
                msg = "Absen Masuk"
                status_code = status.HTTP_200_OK
            else:
                msg = "Absen Pulang"
                status_code = status.HTTP_200_OK
        except:
            msg = "Absen Masuk"
            status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
        })


class DetailAbsen(generics.GenericAPIView):
    def get(self, request, id):
        try:
            absen = Absensi.objects.get(id=id)
            data_absen = AbsenSerializer(absen).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id"
            data_absen = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_absen
        })


class TipeOrders(generics.GenericAPIView):
    def get(self, request):

        tipe_order = OrderType.objects.all()
        data_tipe_order = TipeOrderSerializer(tipe_order, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_tipe_order
        })

    def patch(self, request):
        try:
            id_cart = request.data.get('id_cart')
            tipe_order = request.data.get('tipe_order')

            cart = Cart.objects.get(id=id_cart)
            tipe_order = OrderType.objects.get(id=tipe_order)

            cart.tipe_order = tipe_order
            cart.save()

            msg = "Data successfull inserted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Insert Type Order Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })

    def delete(self, request):
        try:
            id_cart = request.GET.get('id_cart')
            cart = Cart.objects.get(id=id_cart)
            cart.tipe_order_id = None
            cart.save()

            msg = "Data successfull deleted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Delete Type Order Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })


class ChannelPayments(generics.GenericAPIView):
    def get(self, request):
        channel_peyment = ChanelPayment.objects.all()
        data_channel_peyment = ChannelPaymentSerializer(channel_peyment, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_channel_peyment
        })


class LabelsOrder(generics.GenericAPIView):
    def get(self, request):
        label_order = LabelOrder.objects.all()
        data_label_order = LabelOrderSerializer(label_order, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_label_order
        })

    def patch(self, request):
        try:
            id_cart = request.data.get('id_cart')
            label_order = request.data.get('label_order')

            cart = Cart.objects.get(id=id_cart)
            label_order = LabelOrder.objects.get(id=label_order)

            cart.label_order = label_order
            cart.save()

            msg = "Data successfull inserted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Insert Label Order Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })


class Banks(generics.GenericAPIView):
    def get(self, request):
        bank = Bank.objects.all()
        data_bank = BankSerializer(bank, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_bank
        })


class Prepaid(generics.GenericAPIView):

    def get(self, request):
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
                a = product_price + float(300)

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
        return JsonResponse({
            'msg': 'Sukses Sinkronisasi Product',
        })

    def post(self, request):
        customer_id = request.data.get('customer_id')
        product_code = request.data.get('product_code')

        username = "081386356616"
        password = "85160baf89f17e45"
        reff_id = 'PKU-PPOB-' + datetime.today().strftime('%Y%m%d%H%M%S')
        signature = hashlib.md5((username + password + reff_id).encode()).hexdigest()

        data = {
            'customer_id': f'{customer_id}',
            'product_code': f'{product_code}',
            'ref_id': f'{reff_id}',
            'username': f'{username}',
            'sign': f'{signature}'
        }

        url = "https://prepaid.iak.dev/api/top-up"
        headers = {'content-type': 'application/json'}

        data = requests.post(url, data=json.dumps(data), headers=headers).json()

        return JsonResponse({
            'msg': 'Sukses Create Transaction',
            'status_code': status.HTTP_201_CREATED,
            'data': data
        })

    def patch(self, request):

        customer_id = request.data.get('customer_id')
        username = "081386356616"
        password = "85160baf89f17e45"
        signature = hashlib.md5((username + password + customer_id).encode()).hexdigest()

        data = {
            'customer_id': f'{customer_id}',
            'username': f'{username}',
            'sign': f'{signature}'
        }

        url = "https://prepaid.iak.dev/api/inquiry-pln"
        headers = {'content-type': 'application/json'}

        data = requests.post(url, data=json.dumps(data), headers=headers).json()

        return JsonResponse({
            'msg': 'Sukses Get Data PLN',
            'status_code': status.HTTP_201_CREATED,
            'data': data
        })


class DIGI(generics.GenericAPIView):

    def post(self, request):
        customer_no = request.data.get('customer_no')
        buyer_sku_code = request.data.get('buyer_sku_code')
        wallet = request.data.get('wallet')
        message = request.data.get('message')

        get_product = ProductPPOBDigi.objects.get(buyer_sku_code=buyer_sku_code)
        get_product_price = get_product.price_postku
        get_product_name = get_product.product_name
        get_product_brand = get_product.brand
        get_product_category = get_product.category
        get_product_desc = get_product.desc

        get_wallet = WalletToko.objects.get(id=wallet)
        get_wallet_balance = get_wallet.balance
        get_wallet_toko = get_wallet.toko.id

        if float(get_wallet_balance) < float(get_product_price):
            msg = 'Balance Wallet Kurang Dari Harga Product'
            status_code = status.HTTP_400_BAD_REQUEST
            datas = ""
        else:
            msg = 'Success Create PPOB Transaction'
            status_code = status.HTTP_201_CREATED

            # create wallet trx
            years = datetime.today().strftime('%Y')
            mounth = datetime.today().strftime('%m')
            day = datetime.today().strftime('%d')
            hours = datetime.today().strftime('%H')
            munites = datetime.today().strftime('%M')
            seconds = datetime.today().strftime('%S')
            notes = f'Wallet {get_wallet.wallet_code} Success Credit Balance Rp.{get_product_price} For PPOB Product {get_product_name} at {years}-{mounth}-{day} {hours}:{munites}:{seconds}'

            trx_wallet = TrxWallet(wallet_code=get_wallet.wallet_code, type=2, adjustment_balance=get_product_price,
                                   note=notes,
                                   wallet_id=get_wallet.id)
            trx_wallet.save()

            # Hit Third Party
            username = "mefeyeorX4yW"
            password = "85597426-90a0-50cb-85d0-a82bd1f64bdd"
            # password = "dev-4e801df0-dc82-11eb-a6f7-09f0542ad268"
            ref_id = 'TRX-PPOB-' + datetime.today().strftime('%Y%m%d%H%M%S')
            signature = hashlib.md5((username + password + ref_id).encode()).hexdigest()

            data = {
                'username': f'{username}',
                'buyer_sku_code': f'{buyer_sku_code}',
                'customer_no': f'{customer_no}',
                'ref_id': f'{ref_id}',
                'sign': f'{signature}'
            }

            url = "https://api.digiflazz.com/v1/transaction"
            headers = {'content-type': 'application/json'}

            datas = requests.post(url, data=json.dumps(data), headers=headers).json()
            print(datas)

            # create ppob trx
            stat = datas.get('data')['status']
            ref_id = datas.get('data')['ref_id']
            buyer_last_saldo = datas.get('data')['buyer_last_saldo']
            price = datas.get('data')['price']
            trx_ppob = PPOBPrepaidTransaction(ref_id=ref_id, customer_no=customer_no, buyer_sku_code=buyer_sku_code,
                                              message=message,
                                              status=stat, price=price, buyer_last_saldo=buyer_last_saldo,
                                              price_postku=get_product_price, toko_id=get_wallet_toko, wallet_id=wallet,
                                              product_name=get_product_name, category=get_product_category,
                                              brand=get_product_brand, desc=get_product_desc)
            trx_ppob.save()

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': datas
        })

    def get(self, request):
        category = request.GET.get('category')
        brand = request.GET.get('brand')

        if category == None and brand == None:
            product = ProductPPOBDigi.objects.all()
        elif brand == None:
            product = ProductPPOBDigi.objects.filter(category=category)
        elif category == None:
            product = ProductPPOBDigi.objects.filter(brand=brand)
        else:
            product = ProductPPOBDigi.objects.filter(category=category, brand=brand)

        data_product = ProductDIGISerializer(product, many=True).data
        msg = "Success Found Data Product PPOB"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_product
        })


class KategoriPPOB(generics.GenericAPIView):

    def get(self, request):
        kat_ppob_product = CategoryPPOB.objects.all()

        data_kat_ppob_product = KatPPOBProductSerializer(kat_ppob_product, many=True).data
        msg = "Success Found Data Kategori PPOB"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_kat_ppob_product
        })


class MerekPPOB(generics.GenericAPIView):

    def get(self, request):
        category = request.GET.get('category')
        kat = CategoryPPOB.objects.get(category_ppob_key=category)

        if category == None:
            merekppob = BrandPPOB.objects.all()
        else:
            merekppob = BrandPPOB.objects.filter(category_ppob=kat.id)

        data_brand = BrandPPOBProductSerializer(merekppob, many=True).data
        msg = "Success Found Data Brand PPOB"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_brand
        })


class MobileDataPrice(generics.GenericAPIView):

    def get(self, request):

        try:
            ppob_product = ProductPPOB.objects.all()
            data_product = PPOBProductSerializer(ppob_product, many=True).data
            msg = "Success Found Data product"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect Something Went Wrong"
            data_product = "Incorrect Something Went Wrong"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_product
        })

    def post(self, request):
        type = request.data.get('type')
        operator = request.data.get('operator')

        try:
            if operator == None or operator == "":
                ppob_product = ProductPPOB.objects.filter(product_type=type)
            else:
                ppob_product = ProductPPOB.objects.filter(product_type=type, product_description=operator)
            data_product = PPOBProductSerializer(ppob_product, many=True).data
            msg = "Success Found Data product"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect Something Went Wrong"
            data_product = "Incorrect Something Went Wrong"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_product
        })


class MobileDataCallback(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ref_id = request.data.get('ref_id')
        status = request.data.get('status')
        product_code = request.data.get('product_code')
        customer_id = request.data.get('customer_id')
        price = request.data.get('price')
        message = request.data.get('message')
        sn = request.data.get('sn')
        pin = request.data.get('pin')
        balance = request.data.get('balance')
        tr_id = request.data.get('tr_id')
        rc = request.data.get('rc')
        sign = request.data.get('sign')

        c = connection.cursor()
        c.execute(
            f'INSERT INTO webadmin_callbackmobiledata (ref_id,status,product_code,customer_id,price,message,sn,pin,balance,tr_id,rc,sign) VALUES ("{ref_id}","{status}","{product_code}","{customer_id}","{price}","{message}","{sn}","{pin}","{balance}","{tr_id}","{rc}","{sign}")')

        return JsonResponse({
            'msg': "data successfull post",
        })


class Postpaid(generics.GenericAPIView):

    def get(self, request):

        type = request.data.get('type')

        try:
            ppob_product = ProductPPOBPostpaid.objects.filter(type=type)
            data_product = PPOBProducPostpaidtSerializer(ppob_product, many=True).data
            msg = "Success Found Data product"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect Something Went Wrong"
            data_product = "Incorrect Something Went Wrong"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_product
        })

    def put(self, request):
        hp = request.data.get('hp')
        month = request.data.get('month')
        code = request.data.get('code')
        username = "081386356616"
        password = "85160baf89f17e45"
        ref_id = 'PKU-PPOB-' + datetime.today().strftime('%Y%m%d%H%M%S')
        sign = hashlib.md5((username + password + ref_id).encode()).hexdigest()

        data = {
            "commands": 'inq-pasca',
            "username": f'{username}',
            "code": f'{code}',
            "hp": f'{hp}',
            "ref_id": f'{ref_id}',
            "sign": f'{sign}',
            "month": f'{month}'
        }

        url = "https://testpostpaid.mobilepulsa.net/api/v1/bill/check"
        headers = {'content-type': 'application/json'}

        data = requests.post(url, data=json.dumps(data), headers=headers).json()

        return JsonResponse({
            'msg': 'Sukses Get Data Customer',
            'status_code': status.HTTP_201_CREATED,
            'data': data
        })


class StockMenus(generics.GenericAPIView):
    def post(self, request):
        menu = request.data.get('menu')

        try:
            check_menu = Menu.objects.get(id=menu)
            check_stock = StockMenu.objects.get(menu_id=menu)
            status_code = status.HTTP_400_BAD_REQUEST
            msg = "Stock menu Sudah Aktif"
            data = ""
        except ObjectDoesNotExist:
            serializer = StockMenuSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            status_code = status.HTTP_200_OK
            msg = "Data successfull created"
            data = serializer.data

        return JsonResponse({
            'msg': msg,
            'status': status_code,
            'data': data,
        })

    def get(self, request):
        id_toko = request.GET.get('id_toko')
        stock = StockMenu.objects.filter(toko_id=id_toko)
        data_stock = StockMenuSerializer(stock, many=True).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_stock
        })

    def delete(self, request):
        id_stock = request.GET.get('id_stock')
        stock = StockMenu.objects.get(id=id_stock)
        stock.delete()

        msg = "Success Inactive Stock"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
        })


class TrxStock(generics.GenericAPIView):
    def post(self, request):

        try:
            serializer = TrxStockSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            status_code = status.HTTP_200_OK
            msg = "Data successfull created"
            data = serializer.data
        except ObjectDoesNotExist:
            status_code = status.HTTP_400_BAD_REQUEST
            msg = "Stock Id Not Found"
            data = ""

        return JsonResponse({
            'msg': msg,
            'status': status_code,
            'data': data,
        })

    def get(self, request):
        id_menu = request.GET.get('id_menu')
        stock = TrxStockMenu.objects.filter(stock_id=id_menu)
        data_stock = TrxStockSerializer(stock, many=True).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_stock
        })


class DetailStockMenus(generics.GenericAPIView):
    def get(self, request, id):
        stock = StockMenu.objects.get(id=id)
        data_stock = StockMenuSerializer(stock).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_stock
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


class TrxStockDetail(generics.GenericAPIView):
    def get(self, request, id):
        trx_stock = TrxStockMenu.objects.get(id=id)
        data_trx_stock = TrxStockSerializer(trx_stock).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_trx_stock
        })


class DIGICallback(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        trx_id = request.data.get('data')['trx_id']
        ref_id = request.data.get('data')['ref_id']
        customer_no = request.data.get('data')['customer_no']
        buyer_sku_code = request.data.get('data')['buyer_sku_code']
        message = request.data.get('data')['message']
        status = request.data.get('data')['status']
        rc = request.data.get('data')['rc']
        buyer_last_saldo = request.data.get('data')['buyer_last_saldo']
        sn = request.data.get('data')['sn']
        price = request.data.get('data')['price']

        c = connection.cursor()
        c.execute(
            f'INSERT INTO webadmin_calldigi (trx_id,ref_id,customer_no,buyer_sku_code,message,status,rc,buyer_last_saldo,sn,price) VALUES ("{trx_id}","{ref_id}","{customer_no}","{buyer_sku_code}","{message}","{status}","{rc}","{buyer_last_saldo}","{sn}","{price}")')

        return JsonResponse({
            'msg': "data successfull post",
        })

    def get(self, request):
        ref_id = request.GET.get('ref_id')

        callback = CallDIGI.objects.filter(ref_id=ref_id).last()
        data = DIGICallbackSerializer(callback, many=False).data

        trx_ppob = PPOBPrepaidTransaction.objects.get(ref_id=ref_id)
        trx_ppob.status = callback.status
        trx_ppob.message = callback.message
        trx_ppob.save()

        print(callback.status)

        return JsonResponse({
            'message': "Success found data",
            'status_code': status.HTTP_200_OK,
            'data': data,
        })


class WalletsToko(generics.GenericAPIView):
    def post(self, request):
        toko = request.data.get('toko')

        try:
            toko = Toko.objects.get(id=toko)
            check_toko = WalletToko.objects.get(toko_id=toko)
            status_code = status.HTTP_400_BAD_REQUEST
            msg = "Wallet Sudah Aktif"
            data = ""
        except ObjectDoesNotExist:
            serializer = WalletTokoSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            status_code = status.HTTP_200_OK
            msg = "Data successfull created"
            data = serializer.data

        return JsonResponse({
            'msg': msg,
            'status': status_code,
            'data': data,
        })

    def get(self, request):
        toko = request.GET.get('toko')

        try:
            wallets = WalletToko.objects.get(toko_id=toko)
            data_wallet = WalletTokoSerializer(wallets).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Wallet toko belum aktif, silahkan aktifkan wallet toko"
            status_code = status.HTTP_404_NOT_FOUND
            data_wallet = None

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_wallet
        })


class TrxWallets(generics.GenericAPIView):

    def post(self, request):
        wallet_id = request.data.get('wallet')
        adjustment_balance = request.data.get('adjustment_balance')

        wallet = WalletToko.objects.get(id=wallet_id)

        if wallet.status_req_deposit == 1:

            data = wallet.balance_req
            msg = 'Lanjutkan Transaksi Topup Sebelumnya'
            status_code = status.HTTP_400_BAD_REQUEST

        elif wallet.status_req_deposit == 2:

            data = wallet.balance_req
            msg = 'Transksi Sedand Dicek Oleh Admin'
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            wallet.status_req_deposit = 1
            wallet.balance_req = int(adjustment_balance) + randrange(101, 999)
            wallet.save()

            msg = 'Success Created Unik Code'
            wallet = WalletToko.objects.get(id=wallet_id)
            data = wallet.balance_req
            status_code = status.HTTP_200_OK

        return JsonResponse({
            'status_code': status_code,
            'msg': msg,
            'data': data,
        })

    def get(self, request):
        wallet_id = request.GET.get('wallet_id')

        try:
            history_wallets = TrxWallet.objects.filter(wallet_id=wallet_id).order_by('-id')
            data_history_wallets = TrxWalletSerializer(history_wallets, many=True).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Wallet toko belum aktif, silahkan aktifkan wallet toko"
            status_code = status.HTTP_404_NOT_FOUND
            data_history_wallets = None

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_history_wallets
        })


class HistoryTopupWallets(generics.GenericAPIView):
    def get(self, request):
        wallet_id = request.GET.get('wallet_id')
        status_confirm = request.GET.get('status_confirm')

        if status_confirm == '1':
            confirm_topup = ConfirmWallet.objects.filter(wallet_id=wallet_id, status_confirm=1)
            data_confirm_topup = ConfirmWalletSerializer(confirm_topup, many=True).data
        elif status_confirm == '2':
            confirm_topup = ConfirmWallet.objects.filter(wallet_id=wallet_id, status_confirm=2)
            data_confirm_topup = ConfirmWalletSerializer(confirm_topup, many=True).data
        else:
            confirm_topup = ConfirmWallet.objects.filter(wallet_id=wallet_id, status_confirm=3)
            data_confirm_topup = ConfirmWalletSerializer(confirm_topup, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_confirm_topup
        })


class KonfirmasiWallets(generics.GenericAPIView):

    def post(self, request):
        wallet_id = request.data.get('wallet')

        try:
            wallet = ConfirmWallet.objects.filter(wallet_id=wallet_id).last()
            # check_data = ConfirmWallet.objects.get(wallet_id=wallet_id)
            if wallet == None:
                serializer = ConfirmWalletSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                msg = 'Success Konfirmasi Topup, Harap Tunggu Admin Sedang Check Request Topupmu'
                status_code = status.HTTP_200_OK
            elif wallet.status_confirm == 1:
                msg = 'Data Konfirmasi Sedang Di Cek Oleh Admin'
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                serializer = ConfirmWalletSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                msg = 'Success Konfirmasi Topup, Harap Tunggu Admin Sedang Check Request Topupmu'
                status_code = status.HTTP_200_OK

        except ObjectDoesNotExist:
            serializer = ConfirmWalletSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            msg = 'Success Konfirmasi Topup, Harap Tunggu Admin Sedang Check Request Topupmu'
            status_code = status.HTTP_200_OK

        return JsonResponse({
            'status_code': status_code,
            'msg': msg,
        })


class Subs(generics.GenericAPIView):
    def post(self, request):

        account_id = request.data.get('account_id')
        wallet_id = request.data.get('wallet_id')
        date_subs = request.data.get('date_subs')

        get_wallet = WalletToko.objects.get(id=wallet_id)
        get_wallet_balance = get_wallet.balance

        subs_price = int(date_subs) * 1000

        data_account = Account.objects.get(id=account_id)
        check_sub = data_account.is_subs

        if check_sub == 1:
            status_code = status.HTTP_400_BAD_REQUEST
            msg = 'Kamu Sedang Dalam Masa Subscribtion'
        else:
            if float(get_wallet_balance) < subs_price:
                status_code = status.HTTP_400_BAD_REQUEST
                msg = 'Wallet Balance Tidak Mencukupi'
            else:
                # create wallet trx
                years = datetime.today().strftime('%Y')
                mounth = datetime.today().strftime('%m')
                day = datetime.today().strftime('%d')
                hours = datetime.today().strftime('%H')
                munites = datetime.today().strftime('%M')
                seconds = datetime.today().strftime('%S')
                notes = f'Wallet {get_wallet.wallet_code} Success Credit Balance Rp.{subs_price} For Subs POSTKU For {date_subs} Days at {years}-{mounth}-{day} {hours}:{munites}:{seconds}'

                trx_wallet = TrxWallet(wallet_code=get_wallet.wallet_code, type=2, adjustment_balance=subs_price,
                                       note=notes,
                                       wallet_id=get_wallet.id)
                trx_wallet.save()

                # create SUBS trx
                trx_subs = TrxSubs(date_subs=date_subs, account_id=account_id, invoice=subs_price)
                trx_subs.save()

                a = data_account.toko.all()
                for i in a:
                    data_accounts = i.account_set.all()
                    data_accounts.update(is_subs=1)
                    data_accounts.update(subs_date=datetime.today() + timedelta(days=int(date_subs)))

                status_code = status.HTTP_200_OK
                msg = 'Success Created Subs Trx'

        return JsonResponse({
            'status_code': status_code,
            'msg': msg,
        })

