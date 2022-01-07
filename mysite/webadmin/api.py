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
        try:
            if serializerextenduser.is_valid(raise_exception=True):
                if serializer.is_valid(raise_exception=True):
                    serializerextenduser.save()
                    serializer.save()

                    content_user = User.objects.raw(f'SELECT * FROM auth_user WHERE email="{email}"')
                    for i in content_user:
                        id_user = i.id
                    c.execute(f'UPDATE webadmin_account SET user_id="{id_user}" WHERE email="{email}"')
                    r = requests.post('http://localhost:8000/api/token',
                                      data={'username': username, 'password': password})
                    token = r.json().get('access')
                    detail_user = Account.objects.get(username=username)
                    data_detail_akun = ExtendsUserSerializer(detail_user).data

                    msg = "Data successfull created"
                    status_code = status.HTTP_201_CREATED
                    data = data_detail_akun
                    tokens = token
                else:
                    msg = "Username atau email telah digunakan"
                    status_code = status.HTTP_400_BAD_REQUEST
                    data = None
                    tokens = None
            else:
                msg = "Username atau email telah digunakan"
                status_code = status.HTTP_400_BAD_REQUEST
                data = None
                tokens = None
        except:
            msg = "Username atau email telah digunakan"
            status_code = status.HTTP_400_BAD_REQUEST
            data = None
            tokens = None

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'user': data,
            'token': tokens,
        })


class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        r = requests.post('http://localhost:8000/api/token', data={'username': username, 'password': password})
        token = r.json().get('access')

        if token is not None:
            detail_user = Account.objects.get(username=username)

            if detail_user.is_deleted is False:
                data_detail_akun = ExtendsUserSerializer(detail_user).data
                msg = 'Success Login'
                status_code = status.HTTP_200_OK
                tokens = token
            else:
                msg = 'Failed Login User Telah Dihapus'
                data_detail_akun = None
                status_code = status.HTTP_404_NOT_FOUND
                tokens = None
        else:
            msg = 'Failed Login'
            data_detail_akun = None
            status_code = status.HTTP_404_NOT_FOUND
            tokens = None

        print()
        return JsonResponse({
            'status_code': status_code,
            'msg': msg,
            'token': tokens,
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


class DeletedPegawai(generics.GenericAPIView):

    def put(self, request):
        id_user = request.data.get('id_user')
        akun = Account.objects.get(id=id_user)
        akun.is_deleted = True
        akun.save()

        return JsonResponse({
            'msg': 'Data successfull deleted',
            'status_code': status.HTTP_200_OK,
        })


class UpdateProfilePegawai(generics.GenericAPIView):

    def put(self, request):
        id_user = request.data.get('id_user')
        toko = request.data.get('id_toko')

        toko_owner = Toko.objects.get(id=toko)
        owner = toko_owner.account_set.get(is_owner=1)

        akun = Account.objects.get(id=id_user)
        akun.phone = request.data.get("phone", akun.phone)
        akun.toko.clear()
        akun.toko.add(toko)
        akun.is_owner = False
        akun.address = request.data.get("address", akun.address)
        akun.nama = request.data.get("nama", akun.nama)
        akun.profile_pic = request.data.get("profile_pic", akun.profile_pic)
        akun.is_subs = owner.is_subs
        akun.subs_date = owner.subs_date
        akun.save()
        serializer = ExtendsUserSerializer(akun)

        return JsonResponse({
            'msg': 'Data successfull updated',
            'status_code': status.HTTP_200_OK,
            'data': serializer.data,
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
        cart_items = CartItems.objects.filter(cart_id=cart)
        data_menu = request.data.get('menu')

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

        print(cart_items)
        cart_items.delete()
        for i in data_menu:
            cart_item = CartItemsSerializer(data={
                'cart': id_cart,
                'menu': i.get('idmenu'),
                'qty': i.get('qty'),
                'discount': i.get('dics')

            })
            cart_item.is_valid(raise_exception=True)
            cart_item.save()
        print(cart_items)

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
            try:
                table = TableManagement.objects.get(id=cart.table.id)
                table.is_booked = 0
                table.save()
            except:
                print("")
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
            'message': msg,
            'status_code': status_code,
            'data_cart': data_cart,
            'data_cart_items': data_cart_items,
            'data_pajak': data_pajak,
            'data_service_fee': data_sf,
            'data_disc': data_disc,
            'data_tipe_order': data_tipe_order,
            'data_label_order': data_label_order,
            'data_table': data_table,
            'data_pelanggan': data_pelanggan,
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


class DetailTransactionPPOB(generics.GenericAPIView):
    def get(self, request):
        ref_id = request.GET.get('ref_id')

        transaction = PPOBPrepaidTransaction.objects.get(ref_id=ref_id)
        data_trx = PPOBPrepaidTransactionSerializer(transaction).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_trx,
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
            id_cart_item = request.GET.get('id_cart_items')
            print(id_cart_item)
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
            'data': datas.get('data')
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
            'status_code': status_code,
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

        if date_subs == '0':
            status_code = status.HTTP_400_BAD_REQUEST
            msg = 'Request Subs Minimal 1 Hari'
        else:
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


class ContactUsApi(generics.GenericAPIView):
    def get(self, request):
        contact_us = ContactUs.objects.all()

        data_contact_us = ContactUsSerializer(contact_us, many=True).data
        msg = "Success Found Data Contact Us"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_contact_us
        })
