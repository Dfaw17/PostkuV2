from xendit.models.qrcode import QRCodeType

from ..serializers import *
from django.http import *
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics

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
