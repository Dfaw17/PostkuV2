from ..serializers import *
from django.http import *
from django.db import connection
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics

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
