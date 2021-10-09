from ..serializers import *
from django.http import *
from django.db import connection
from django.core.exceptions import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics

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
