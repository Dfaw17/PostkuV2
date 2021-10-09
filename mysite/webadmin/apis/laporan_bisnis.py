from ..serializers import *
from django.http import *
from rest_framework import status
from rest_framework import generics


class LaporanBisnis(generics.GenericAPIView):

    def get(self, request):

        id_toko = request.GET.get('id_toko')
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if date1 and date2 != "":
            # Penjualan Kotor
            penjualan_kotor = CartItems.objects.filter(toko=id_toko, ordered=1,
                                                       created_at__range=[date1, date2]).aggregate(Sum('price'))
            if penjualan_kotor.get('price__sum') == None:
                data_penjualan_kotor = 0
            else:
                data_penjualan_kotor = penjualan_kotor.get('price__sum')

            # Pajak
            pajak = Cart.objects.filter(toko=id_toko, ordered=1,
                                        created_at__range=[date1, date2]).aggregate(Sum('total_pajak'))
            if pajak.get('total_pajak__sum') == None:
                data_pajak = 0
            else:
                data_pajak = pajak.get('total_pajak__sum')

            # Service Fee
            sf = Cart.objects.filter(toko=id_toko, ordered=1,
                                     created_at__range=[date1, date2]).aggregate(Sum('total_service_fee'))
            if sf.get('total_service_fee__sum') == None:
                data_sf = 0
            else:
                data_sf = sf.get('total_service_fee__sum')

            # Discount
            disc1 = Cart.objects.filter(toko=id_toko, ordered=1,
                                        created_at__range=[date1, date2]).aggregate(Sum('total_disc'))
            if disc1.get('total_disc__sum') == None:
                data_disc1 = 0
            else:
                data_disc1 = disc1.get('total_disc__sum')

            disc2 = CartItems.objects.filter(toko=id_toko, ordered=1,
                                             created_at__range=[date1, date2]).aggregate(Sum('total_disc'))
            if disc2.get('total_disc__sum') == None:
                data_disc2 = 0
            else:
                data_disc2 = disc2.get('total_disc__sum')
            data_disc = float(data_disc1 + data_disc2)

            # Hpp Item
            hpp = CartItems.objects.filter(toko=id_toko, ordered=1,
                                           created_at__range=[date1, date2]).aggregate(Sum('hpp'))
            if hpp.get('hpp__sum') == None:
                data_hpp = 0
            else:
                data_hpp = hpp.get('hpp__sum')

            # Jumlah Item
            total_item = CartItems.objects.filter(toko=id_toko, ordered=1,
                                                  created_at__range=[date1, date2]).aggregate(Sum('qty'))
            if total_item.get('qty__sum') == None:
                data_total_item = 0
            else:
                data_total_item = total_item.get('qty__sum')

            # Cancel Trx
            cancel_trx = CartItems.objects.filter(toko=id_toko, ordered=1, is_canceled=1,
                                                  created_at__range=[date1, date2]).aggregate(Sum('price'))
            if cancel_trx.get('price__sum') == None:
                data_cancel_trx = 0
            else:
                data_cancel_trx = cancel_trx.get('price__sum')

            # Laba rugi
            laba_rugi = float(data_penjualan_kotor + data_pajak + data_sf) - float(
                data_disc + data_cancel_trx + data_hpp)

            msg = 'Success found data'
            status_code = status.HTTP_200_OK
        else:
            msg = 'Masukan tanggal awal dan tanggal akhir terlebih dahulu'
            status_code = status.HTTP_404_NOT_FOUND
            data_penjualan_kotor = None
            data_pajak = None
            data_sf = None
            data_disc = None
            data_hpp = None
            data_total_item = None
            data_cancel_trx = None
            laba_rugi = None

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data_penjualan_kotor': data_penjualan_kotor,
            'data_pajak': data_pajak,
            'data_service_fee': data_sf,
            'data_disc': data_disc,
            'data_hpp': data_hpp,
            'data_total_item': data_total_item,
            'data_cancel_trx': data_cancel_trx,
            'data_laba_rugi': laba_rugi,
        })
