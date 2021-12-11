from ..serializers import *
from django.http import *
from django.db import connection
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics


class CRUDMenu(generics.GenericAPIView):

    def get(self, request):
        id_toko = request.GET.get('id_toko')
        id_kategori = request.GET.get('id_kategori')

        if id_kategori == None:
            menu = Menu.objects.filter(toko=id_toko, is_active=True)
            data_menu_toko = CustomMenuSerializer(menu, many=True).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        else:
            menu = Menu.objects.filter(toko=id_toko, kategori=id_kategori, is_active=True)
            data_menu_toko = CustomMenuSerializer(menu, many=True).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_menu_toko
        })

    def put(self, request):
        c = connection.cursor()
        id_menu = request.data.get('id_menu')

        try:
            c.execute(f'UPDATE webadmin_menu SET is_active=0 WHERE id="{id_menu}"')
            msg = "Data successfull deleted"
        except ObjectDoesNotExist:
            msg = "Data Menu Nof Found"

        return JsonResponse({
            'msg': msg,
            'status_code': status.HTTP_200_OK,
        })

    def post(self, request):

        serializer = MenuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({
            'msg': "data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })

    def patch(self, request):

        id_menu = request.data.get('id_menu')
        menu = Menu.objects.get(id=id_menu)

        menu.nama = request.data.get("nama", menu.nama)
        menu.harga = request.data.get("harga", menu.harga)
        menu.harga_modal = request.data.get("harga_modal", menu.harga_modal)
        menu.desc = request.data.get("desc", menu.desc)
        menu.menu_pic = request.data.get("menu_pic", menu.menu_pic)
        menu.kategori_id = request.data.get("kategori_id", menu.kategori_id)

        menu.save()
        serializer = MenuSerializer(menu)

        return JsonResponse({
            'msg': "data successfull updated",
            'status_code': status.HTTP_200_OK,
            'data': serializer.data,
        })


class DetailMenu(generics.GenericAPIView):
    def get(self, request, id):
        try:
            menu = Menu.objects.get(id=id)
            data_menu = CustomMenuSerializer(menu).data

            try:
                check_stock = StockMenu.objects.get(menu_id=menu)
                check_stock = StockMenuSerializer(check_stock).data
            except:
                check_stock = None

            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            check_stock = None
            msg = "Incorrect id"
            data_menu = "Data Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_menu,
            'check_stock': check_stock
        })
