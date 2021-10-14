from ..serializers import *
from django.http import *
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics

class StockMenus(generics.GenericAPIView):
    def post(self, request):
        menu = request.data.get('menu')

        try:
            check_menu = Menu.objects.get(id=menu)
            check_stock = StockMenu.objects.get(menu_id=menu)
            status_code = status.HTTP_400_BAD_REQUEST
            msg = "Stock menu Sudah Aktif"
            data = ""
        except ObjectDoesNotExist:
            serializer = StockMenuSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            status_code = status.HTTP_200_OK
            msg = "Data successfull created"
            data = serializer.data

        return JsonResponse({
            'msg': msg,
            'status': status_code,
            'data': data,
        })

    def get(self, request):
        id_toko = request.GET.get('id_toko')
        stock = StockMenu.objects.filter(toko_id=id_toko)
        data_stock = StockMenuSerializer(stock, many=True).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_stock
        })

    def delete(self, request):
        id_menu = request.objects.get('menu')
        stock = StockMenu.objects.get(menu_id=id_menu)
        stock.delete()

        msg = "Success Inactive Stock"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
        })

class TrxStock(generics.GenericAPIView):
    def post(self, request):

        try:
            serializer = TrxStockSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            status_code = status.HTTP_200_OK
            msg = "Data successfull created"
            data = serializer.data
        except ObjectDoesNotExist:
            status_code = status.HTTP_400_BAD_REQUEST
            msg = "Stock Id Not Found"
            data = ""

        return JsonResponse({
            'msg': msg,
            'status': status_code,
            'data': data,
        })

    def get(self, request):
        id_menu = request.GET.get('id_menu')
        stock = TrxStockMenu.objects.filter(stock_id=id_menu)
        data_stock = TrxStockSerializer(stock, many=True).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_stock
        })

class DetailStockMenus(generics.GenericAPIView):
    def get(self, request, id):
        stock = StockMenu.objects.get(id=id)
        data_stock = StockMenuSerializer(stock).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_stock
        })

class TrxStockDetail(generics.GenericAPIView):
    def get(self, request, id):
        trx_stock = TrxStockMenu.objects.get(id=id)
        data_trx_stock = TrxStockSerializer(trx_stock).data
        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_trx_stock
        })
