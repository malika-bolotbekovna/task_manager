from .models import List

def lists_for_sidebar(request):
    if request.user.is_authenticated:
        lists = List.objects.filter(owner=request.user)
    else:
        lists = []
    return {'lists': lists}
