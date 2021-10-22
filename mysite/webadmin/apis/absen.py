from ..serializers import *
from datetime import *
from django.http import *
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics


class Absen(generics.GenericAPIView):
    def post(self, request):
        user = request.data.get("user")

        check = Absensi.objects.filter(user=user).last()
        data_check = AbsenSerializer(check).data

        if data_check.get("user") == None:
            serializer = AbsenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            absen = Absensi.objects.get(id=serializer.data.get('id'))
            absen.pic1 = request.data.get("foto", absen.pic1)
            absen.time1 = datetime.now()
            absen.save()
            return JsonResponse({
                'msg': "Success Absen",
            })

        if data_check.get("time1") != None and data_check.get("time2") != None:
            serializer = AbsenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            absen = Absensi.objects.get(id=serializer.data.get('id'))
            absen.pic1 = request.data.get("foto", absen.pic1)
            absen.time1 = datetime.now()
            absen.save()
        elif data_check.get("time1") != None and data_check.get("time2") == None:
            absen = Absensi.objects.get(id=data_check.get("id"))
            absen.pic2 = request.data.get("foto", absen.pic1)
            absen.time2 = datetime.now()
            absen.save()

        return JsonResponse({
            'msg': "Data successfull inserted",
            'status_code': status.HTTP_200_OK,
        })

    def get(self, request):
        id = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            absen = Absensi.objects.filter(toko=id, created_at__range=[date1, date2]).order_by('-created_at')
        else:
            absen = Absensi.objects.filter(toko=id).order_by('-created_at')

        data_absensi_toko = CustomAbsenSerializer(absen, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_absensi_toko
        })


class CheckAbsen(generics.GenericAPIView):
    def get(self, request, id):
        absen = Absensi.objects.filter(user_id=id).last()

        try:
            if absen.time2 != None:
                msg = "Absen Masuk"
                status_code = status.HTTP_200_OK
            else:
                msg = "Absen Pulang"
                status_code = status.HTTP_200_OK
        except:
            msg = "Absen Masuk"
            status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
        })


class DetailAbsen(generics.GenericAPIView):
    def get(self, request, id):
        try:
            absen = Absensi.objects.get(id=id)
            data_absen = CustomAbsenSerializer(absen).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Incorrect id"
            data_absen = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_absen
        })
