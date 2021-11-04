from xendit.models.qrcode import QRCodeType
from ..serializers import *
from xendit import *
import base64
from django.http import *
from django.db import connection
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny

global xnd_prod, xnd_dev

xnd_prod = "xnd_production_nfjAk6kENINyOobuWaOujS3aqfT4LwqW8rzAsvwBOSqD28tjJGYTsQRTqZakEPT"
xnd_dev = "xnd_development_27A0zquDKjORXcsXvv3XEnX00BBlwVlR97ZFQIfbA8TPNrZDa4VFaSzIDBUeem"


class XenditQris(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        cart_code = request.data.get('cart_code')
        amount = request.data.get('amount')

        api_key = xnd_prod
        xendit_instance = Xendit(api_key=api_key)
        QRCode = xendit_instance.QRCode

        try:
            qriss = QRCode.create(
                external_id=cart_code,
                type=QRCodeType.DYNAMIC,
                callback_url="http://13.213.192.212:8000/api/qris/callback",
                amount=amount,
            )
            # sample_string = qriss.qr_string
            # sample_string_bytes = sample_string.encode("ascii")
            #
            # base64_bytes = base64.b64encode(sample_string_bytes)
            # base64_string = base64_bytes.decode("ascii")

            datas = {
                "id": qriss.id,
                "external_id": qriss.external_id,
                "amount": qriss.amount,
                "description": "",
                "qr_string": qriss.qr_string,
                "callback_url": qriss.callback_url,
                "type": qriss.type,
                "status": qriss.status,
                "created": qriss.created,
                "updated": qriss.updated,
                "metadata": None
            }
            msg = 'Data successfull created'
            status_code = status.HTTP_201_CREATED
        except:
            msg = 'data duplicated, externa_id must be uniqe'
            status_code = status.HTTP_400_BAD_REQUEST
            datas = None

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            # 'base_64': base64_string,
            'data': datas,
        })

    def get(self, request, id):
        api_key = xnd_prod
        xendit_instance = Xendit(api_key=api_key)
        QRCode = xendit_instance.QRCode

        cart_code = id

        qriss = QRCode.get_by_ext_id(
            external_id=cart_code,
        )
        sample_string = qriss.qr_string
        sample_string_bytes = sample_string.encode("ascii")

        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_string = base64_bytes.decode("ascii")

        # return HttpResponse(qrcode)
        datas = {
            "id": qriss.id,
            "external_id": qriss.external_id,
            "amount": qriss.amount,
            "description": "",
            "qr_string": qriss.qr_string,
            "callback_url": qriss.callback_url,
            "type": qriss.type,
            "status": qriss.status,
            "created": qriss.created,
            "updated": qriss.updated,
            "metadata": None
        }
        return JsonResponse({
            'msg': 'Success found data',
            'status_code': status.HTTP_200_OK,
            'base_64': base64_string,
            'data': datas,
        })


class XenditCallback(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):

        external_id = request.data.get('qr_code')['external_id']
        amount = request.data.get('amount')
        status = request.data.get('status')
        event = request.data.get('event')

        c = connection.cursor()
        c.execute(
            f'INSERT INTO webadmin_callbackxendit (event,amount,external_id,status) VALUES ("{event}","{amount}","{external_id}","{status}")')

        return JsonResponse({
            'msg': "data successfull post",
        })

    def get(self, request):
        cart_code = request.GET.get('cart_code')
        amount = request.GET.get('amount')

        try:
            callback = CallbackXendit.objects.get(external_id=cart_code, amount=amount)
            data = XenditCallbackSerializer(callback).data
            msg = "Success found data"
        except ObjectDoesNotExist:
            data = None
            msg = "Qris Belum Dibayar"

        return JsonResponse({
            'message': msg,
            'status_code': status.HTTP_200_OK,
            'data': data,
        })
