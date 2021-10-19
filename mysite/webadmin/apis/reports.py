from xendit.models.qrcode import QRCodeType

from ..serializers import *
import requests
from xendit import *
import hashlib
import json
from datetime import *
import base64

from django.http import *
from django.contrib.auth.models import User
from django.db import connection
from django.core.exceptions import *
from django.db.models import Count

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from random import *
from rest_framework.pagination import PageNumberPagination


class ReportByMenu(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            report_menu = CartItems.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2]).values(
                'menu__nama').annotate(
                qty=Sum('qty'), price=Sum('price')).order_by('-qty')
        else:
            report_menu = CartItems.objects.filter(toko_id=id_toko, ordered=1).values('menu__nama').annotate(
                qty=Sum('qty'), price=Sum('price')).order_by('-qty')

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_menu),
        })


class ReportByEmployee(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            report_employee = Transaction.objects.filter(toko_id=id_toko, created_at__range=[date1, date2]).values(
                'pegawai__nama').annotate(jumlah_trx=Count('id'), nominal_trx=Sum('grand_total'))
        else:
            report_employee = Transaction.objects.filter(toko_id=id_toko).values('pegawai__nama').annotate(
                jumlah_trx=Count('id'), nominal_trx=Sum('grand_total'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_employee),
        })


class ReportByMenuKategori(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            report_menu_kategori = CartItems.objects.filter(toko_id=id_toko, ordered=1,
                                                            created_at__range=[date1, date2]).values(
                'menu_kategori__label').annotate(qty=Sum('qty'), price=Sum('price')).order_by('-qty')
        else:
            report_menu_kategori = CartItems.objects.filter(toko_id=id_toko, ordered=1).values(
                'menu_kategori__label').annotate(qty=Sum('qty'), price=Sum('price')).order_by('-qty')

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_menu_kategori),
        })


class ReportByDisc(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            report_disc = Cart.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                              discount_id__isnull=False).values('discount__nama').annotate(
                total_trx=Count('id'), total_disc=Sum('total_disc'))
            report_disc2 = CartItems.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                                    discount_id__isnull=False).values('discount__nama').annotate(
                total_trx=Count('id'), total_disc=Sum('total_disc'))
        else:
            report_disc = Cart.objects.filter(toko_id=id_toko, ordered=1, discount_id__isnull=False).values(
                'discount__nama').annotate(
                total_trx=Count('id'), total_disc=Sum('total_disc'))
            report_disc2 = CartItems.objects.filter(toko_id=id_toko, ordered=1, discount_id__isnull=False).values(
                'discount__nama').annotate(
                total_trx=Count('id'), total_disc=Sum('total_disc'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': {
                'discount_transaksi': list(report_disc),
                'discount_item': list(report_disc2),
            }
        })


class ReportByTable(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            report_table = Cart.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                               table_id__isnull=False).values(
                'table__nama').annotate(jumlah_trx=Count('id'))
        else:
            report_table = Cart.objects.filter(toko_id=id_toko, ordered=1, table_id__isnull=False).values(
                'table__nama').annotate(jumlah_trx=Count('id'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_table),
        })


class ReportByPelanggan(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            report_pelanggan = Cart.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                                   pelanggan_id__isnull=False).values(
                'pelanggan__nama').annotate(jumlah_trx=Count('id'))
        else:
            report_pelanggan = Cart.objects.filter(toko_id=id_toko, ordered=1, pelanggan_id__isnull=False).values(
                'pelanggan__nama').annotate(jumlah_trx=Count('id'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_pelanggan),
        })


class ReportByOrderType(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            report_order_tipe = Cart.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                                    tipe_order_id__isnull=False).values(
                'tipe_order__nama').annotate(jumlah_trx=Count('id'))
        else:
            report_order_tipe = Cart.objects.filter(toko_id=id_toko, ordered=1, tipe_order_id__isnull=False).values(
                'tipe_order__nama').annotate(jumlah_trx=Count('id'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_order_tipe),
        })


class ReportByLabelOrder(generics.GenericAPIView):
    def get(self, request):
        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            report_order_label = Cart.objects.filter(toko_id=id_toko, ordered=1, created_at__range=[date1, date2],
                                                     label_order_id__isnull=False).values(
                'label_order__nama').annotate(jumlah_trx=Count('id'))
        else:
            report_order_label = Cart.objects.filter(toko_id=id_toko, ordered=1, label_order_id__isnull=False).values(
                'label_order__nama').annotate(jumlah_trx=Count('id'))

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': list(report_order_label),
        })
