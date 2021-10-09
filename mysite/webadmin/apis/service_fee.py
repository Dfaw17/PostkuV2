from ..serializers import *
from django.http import *
from django.db import connection
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics

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
