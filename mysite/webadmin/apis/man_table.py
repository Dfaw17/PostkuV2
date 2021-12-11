from ..serializers import *
from django.http import *
from django.db import connection
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics


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
            'status_code': status.HTTP_201_CREATED,
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
