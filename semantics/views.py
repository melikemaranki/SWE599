#from semantics.query import get_query_results
from semantics.tasks import *
from django.shortcuts import render, redirect
#from .data_util import getData


def home(request):
    return render(request, 'home.html')

def query(request):
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        text = request.POST['Text1'].strip()
        if not text:
            return
        q_res = query_data(text)
        prev_query = text

  
        return render(request, 'home.html', {'data': q_res.to_html() ,'prev_query': prev_query})
    else:
        return render(request, 'home.html')

def basic_query(request):
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        text = request.POST['search'].strip()
        if not text:
            return
        q_res = basic_query_data(text)
        prev_query = text

  
        return render(request, 'basic_query.html', {'data': q_res ,'prev_query': prev_query})
    else:
        return render(request, 'basic_query.html')
