from ..serializers import *
from django.http import *
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics
import datetime


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
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

        if date1 and date2 != "":
            transaction = Transaction.objects.filter(toko=id_toko, created_at__range=[date1, date2]).order_by(
                '-created_at')
        else:
            # transaction = Transaction.objects.filter(toko=id_toko).order_by(
            #     '-created_at')
            transaction = Transaction.objects.filter(toko=id_toko, created_at__range=[today_min, today_max]).order_by(
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
