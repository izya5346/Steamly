from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import models
@login_required(login_url='login/')
def index(request):
    return render(request, 'index.html')
def create_new_items(request):
    increment = int(request.GET['append_increment'])
    increment_to = increment + 10
    kalat = list(models.ItemJson.objects.values('data')[increment:increment_to])
    list_result = [entry['data'] for entry in kalat]
    new_list = []
    for i in list_result:
        k = i.copy()
        k.update(float_forward = k['float'] * 100)
        k.update(price = str(k['price'])[:-2] + ',' + str(k['price'])[-2:])
        k.update(default = str(k['default'])[:-2] + ',' + str(k['default'])[-2:])
        sticks = []
        for j in k['stickers']:
            q = j.copy()
            q.update(price = str(q['price'])[:-2] + ',' + str(q['price'])[-2:])
            try:
                q.update(wear = round(q['wear'] * 100))
            except:
                q.update(wear = 100)
            sticks.append(q)
        k.update(stickers = sticks)
        new_list.append(k)
    return render(request, 'create_new_items.html', {'items': new_list})
# Create your views here.
