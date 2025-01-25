from django.conf import settings


def get_page(request):
    """
    Utility function to get the page number from the request.
    - If the page parameter exists, convert it to a number.
    - If it's not numeric, set it to 1.
    - If it doesn't exist, set it to 1.
    """
    page = request.query_params.get("page", "1")
    if not page.isnumeric():
        page = 1
    else:
        page = int(page)
    return page


def get_page_items(page, queryset, page_size=settings.PAGE_SIZE):
    """
    Utility function to get items for a specific page.
    - Calculate the start and end index for the page.
    - Return the items for the page.
    """
    start_index = (page - 1) * page_size
    end_index = page * page_size
    return queryset[start_index:end_index]
