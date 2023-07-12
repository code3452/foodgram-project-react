from rest_framework.pagination import PageNumberPagination


class SimplePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6
