from ..serializers import *
from django.http import *
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics
from django.db import connection


class DetailToko(generics.GenericAPIView):
    def get(self, request, id):
        try:
            toko = Toko.objects.get(id=id)
            data_toko_akun = TokoSerializer(toko).data

            pegawai = Account.objects.filter(toko__id=id, is_owner=0, is_deleted = False)
            data_pegawai = ExtendsUserSerializer(pegawai, many=True).data

            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id"
            data_toko_akun = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_toko_akun,
            'pegawai_toko': data_pegawai,
        })

class CRUDToko(generics.GenericAPIView):

    def get(self, request):

        try:
            id_owner = request.GET.get('id_owner')
            account = Account.objects.get(id=id_owner)
            toko = account.toko.filter(is_active=1)
            data_toko_akun = TokoSerializer(toko, many=True).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id_uder"
            data_toko_akun = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_toko_akun
        })

    def post(self, request):
        c = connection.cursor()
        id_user = request.data.get('id_user')

        serializer = TokoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        id_toko = serializer.data.get('id')
        c.execute(f'INSERT INTO webadmin_account_toko (account_id,toko_id) VALUES ("{id_user}","{id_toko}")')

        return JsonResponse({
            'msg': "data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })

    def put(self, request):

        c = connection.cursor()
        id_toko = request.data.get('id_toko')

        try:
            c.execute(f'UPDATE webadmin_toko SET is_active=0 WHERE id="{id_toko}"')
            msg = "Data successfull deleted"
        except ObjectDoesNotExist:
            msg = "Data Toko Nof Found"

        return JsonResponse({
            'msg': msg,
            'status_code': status.HTTP_200_OK,
        })

    def patch(self, request):

        id_toko = request.data.get('id_toko')
        toko = Toko.objects.get(id=id_toko)

        toko.nama = request.data.get("nama", toko.nama)
        toko.alamat = request.data.get("alamat", toko.alamat)
        toko.logo = request.data.get("logo", toko.logo)
        toko.kategori = request.data.get("kategori", toko.kategori)
        toko.add_provinsi = request.data.get("add_provinsi", toko.add_provinsi)
        toko.add_kab_kot = request.data.get("add_kab_kot", toko.add_kab_kot)
        toko.add_kecamatan = request.data.get("add_kecamatan", toko.add_kecamatan)
        toko.add_kel_des = request.data.get("add_kel_des", toko.add_kel_des)
        toko.is_active = request.data.get("is_active", toko.is_active)

        toko.save()
        serializer = TokoSerializer(toko)

        return JsonResponse({
            'msg': 'Data successfull updated',
            'status_code': status.HTTP_200_OK,
            'data': serializer.data,
        })
