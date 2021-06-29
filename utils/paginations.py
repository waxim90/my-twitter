from rest_framework.pagination import PageNumberPagination, BasePagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):
    # 默认的 page size，也就是 page 没有在 url 参数里的时候
    page_size = 20
    # 默认的 page_size_query_param 是 None 表示不允许客户端指定每一页的大小
    # 如果加上这个配置，就表示客户端可以通过 size=10 来指定一个特定的大小用于不同的场景
    # 比如手机端和web端访问同一个API但是需要的 size 大小是不同的。
    # 例如：https://.../api/friendships/1/followers/?page=3&size=10
    page_size_query_param = 'size'
    # 允许客户端指定的最大 page_size 是多少
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })


class EndlessPagination(BasePagination):
    page_size = 20

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False

    def paginate_queryset(self, queryset, request, view=None):
        # created_at__gt 用于下拉刷新的时候加载最新的内容进来
        # 为了简便起见，下拉刷新不做翻页机制，直接加载所有更新的数据
        # 因为如果数据很久没有更新的话，不会采用下拉刷新的方式进行更新，而是重新加载最新的数据
        if 'created_at__gt' in request.query_params:
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt)
            self.has_next_page = False
            return queryset.order_by('-created_at')

        # created_at__lt 用于向上滚屏（往下翻页）的时候加载下一页的数据
        # 寻找 created_at < created_at__lt 的 objects 里按照 created_at 倒序的前
        # page_size + 1 个 objects
        # 比如目前的 created_at 列表是 [10, 9, 8, 7 .. 1] 如果 created_at__lt=10
        # page_size = 2 则应该返回 [9, 8, 7]，多返回一个 object 的原因是为了判断是否
        # 还有下一页从而减少一次空加载。
        if 'created_at__lt' in request.query_params:
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt)

        queryset = queryset.order_by('-created_at')[:self.page_size + 1]
        self.has_next_page = len(queryset) > self.page_size
        return queryset[:self.page_size]

    def get_paginated_response(self, data):
        return Response({
            'has_next_page': self.has_next_page,
            'results': data,
        })