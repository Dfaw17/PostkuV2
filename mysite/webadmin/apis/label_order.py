from ..serializers import *
from django.http import *
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics

class LabelsOrder(generics.GenericAPIView):
    def get(self, request):
        label_order = LabelOrder.objects.all()
        data_label_order = LabelOrderSerializer(label_order, many=True).data

        msg = "Success found data"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_label_order
        })

    def patch(self, request):
        try:
            id_cart = request.data.get('id_cart')
            label_order = request.data.get('label_order')

            cart = Cart.objects.get(id=id_cart)
            label_order = LabelOrder.objects.get(id=label_order)

            cart.label_order = label_order
            cart.save()

            msg = "Data successfull inserted"
            resp_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            msg = "Failed Insert Label Order Not Found"
            resp_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': resp_code,
        })
