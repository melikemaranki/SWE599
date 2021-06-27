from semantics.tasks import *
from django.shortcuts import render, redirect
from .forms import SearchForm

def sparql(request):
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        text = request.POST['Text1'].strip()
        if not text:
            return
        q_res = query_data(text)
        prev_query = text

  
        return render(request, 'sparql.html', {'data': q_res.to_html(show_dimensions= True,
        justify='center', render_links=True) ,'prev_query': prev_query})
    else:
        return render(request, 'sparql.html')

def home(request):
    content = {}
    form = SearchForm()
    if request.method == 'POST':
        form = SearchForm(request.POST)

        if not form.has_changed(): #if nothing is changed in the form return the same page
            context = {'form':form, 'content':content}
            return render(request, 'home.html', context) 

        if form.is_valid():
            form.save()
        keyword = form.cleaned_data.get("keyword")
        country = form.cleaned_data.get("country")
        search = form.cleaned_data.get("search")
        section = form.cleaned_data.get("section")
        content = basic_query_data(keyword, country, search, section)
        #prev_query = text
    context = {'form':form, 'content':content}
    return render(request, 'home.html', context)