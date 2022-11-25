from django.core.paginator import Paginator


def truncatechars(chars: str, trim: int) -> str:
    return chars[:trim] + '…' if len(chars) > trim else chars


def paginate(request, queryset, objects_count):
    return Paginator(queryset, objects_count).get_page(request.GET.get('page'))
