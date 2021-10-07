from ..serializers import *
from django.http import *
from django.db import connection
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics

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

