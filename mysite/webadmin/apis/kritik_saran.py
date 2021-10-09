from ..serializers import *
from django.http import *
from rest_framework import status
from rest_framework import generics

class CreateSaranKritik(generics.GenericAPIView):
    def post(self, request):
        serializer = KritikSaranSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({
            'msg': "Data successfull created",
            'status_code': status.HTTP_201_CREATED,
            'data': serializer.data,
        })
