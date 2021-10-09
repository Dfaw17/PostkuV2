from ..serializers import *
from django.http import *
from django.db import connection
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics

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
