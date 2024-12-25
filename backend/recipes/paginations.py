from rest_framework.pagination import PageNumberPagination

from .constants import PAGINATION_PAGE_SIZE


class PageLimitPagination(PageNumberPagination):
    """Пагинация с настройкой через параметр limit."""

    page_size = PAGINATION_PAGE_SIZE
    page_size_query_param = 'limit'
