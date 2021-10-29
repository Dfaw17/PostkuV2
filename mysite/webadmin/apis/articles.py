from ..serializers import *
from django.http import *
from django.core.exceptions import *
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination


class Articles(generics.GenericAPIView):

    def get(self, request):
        paginator = PageNumberPagination()
        per_page = paginator.page_size = 10

        article = Article.objects.filter(is_active=1).order_by('id')
        jumlah_article = Article.objects.filter(is_active=1).count()
        result_page = paginator.paginate_queryset(article, request)
        data_article = ListArticleSerializer(result_page, many=True, ).data

        pembagian = jumlah_article/per_page
        mod = jumlah_article%per_page
        if pembagian < 1:
            a = 1
        else:
            a = round(pembagian)
            last_digit = int(repr(pembagian)[-1])
            if last_digit < 5:
                a = a
            else:
                a = a - 1
            if mod == 0:
                a = a
            else:
                a = a + 1

        msg = "Success Found Data Article"
        status_code = status.HTTP_200_OK

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'max_page': a,
            'total_data_article': jumlah_article,
            'data_per_page': per_page,
            'next_link': paginator.get_next_link(),
            'previous__link': paginator.get_previous_link(),
            'data': data_article,
        })


class DetailArticles(generics.GenericAPIView):
    def get(self, request, id):
        try:
            article = Article.objects.get(id=id)
            article.count_seen = article.count_seen + 1
            article.save()

            data_article = DetailArticleSerializer(article).data
            msg = "Success found data"
            status_code = status.HTTP_200_OK
        except ObjectDoesNotExist:
            data_article = ""
            msg = "Article Not Found"
            status_code = status.HTTP_404_NOT_FOUND

        return JsonResponse({
            'msg': msg,
            'status_code': status_code,
            'data': data_article
        })
