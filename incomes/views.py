from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Source, Income
import json
import datetime

@login_required(login_url='/authentication/login')
def index(request):
    try:
        sources = Source.objects.all()
        incomes = Income.objects.filter(user=request.user)

        paginator = Paginator(incomes, 5)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator, page_number)
        
        context = {
            'incomes': incomes,
            'page_obj': page_obj
        }

        return render(request, 'incomes/index.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred while fetching Incomes: {e}')
        return render(request, 'incomes/index.html', {'incomes': []})


@login_required(login_url='/authentication/login')
def add_income(request):
    try:
        sources = Source.objects.all()
        context = {
            'sources': sources,
            'values': request.POST
        }

        if request.method == 'GET':
            return render(request, 'incomes/add_income.html', context)
        elif request.method == 'POST':
            date = datetime.datetime.strptime(request.POST['date'], "%Y-%m-%d").date()

            # source
            source = request.POST['source']
            if not source:
                messages.error(request, 'Source is required')
                return render(request, 'incomes/add_income.html', context)
            else:
                source = Source.objects.get(name=source)
                if not source:
                    messages.error(request, 'Source does not exist')
                    return render(request, 'incomes/add_income.html', context)
                
            # description
            description = request.POST['description']
            if not description:
                messages.error(request, 'Description is required')
                return render(request, 'incomes/add_income.html', context)

            # amount
            amount = request.POST['amount'] 
            if not amount:
                messages.error(request, 'Amount is required')
                return render(request, 'incomes/add_income.html', context)
            
            Income.objects.create(
                date=date, 
                source=source, 
                description=description, 
                amount=amount, 
                user=request.user
            )
            messages.success(request, 'Income saved successfully')
            return redirect('incomes')
    except Exception as e:
        messages.error(request, f'An error occurred while adding the Income: {e}')
        return render(request, 'incomes/add_income.html', context)


@login_required(login_url='/authentication/login')
def edit_income(request, id):
    try:
        income = Income.objects.get(pk=id)
        sources = Source.objects.all()
        context = {
            'sources': sources,
            'values': income,
            'income': income
        }

        if request.method == 'GET':
            return render(request, 'incomes/edit_income.html', context)
        elif request.method == 'POST':
            date = datetime.datetime.strptime(request.POST['date'], "%Y-%m-%d").date()

            # source
            source = request.POST['source']
            if not source:
                messages.error(request, 'Source is required')
                return render(request, 'incomes/edit_income.html', context)
            else:
                source = Source.objects.get(name=source)
                if not source:
                    messages.error(request, 'Source does not exist')
                    return render(request, 'incomes/edit_income.html', context)
                
            # description
            description = request.POST['description']
            if not description:
                messages.error(request, 'Description is required')
                return render(request, 'incomes/edit_income.html', context)

            # amount
            amount = request.POST['amount'] 
            if not amount:
                messages.error(request, 'Amount is required')
                return render(request, 'incomes/edit_income.html', context)

            income.date = date
            income.source = source
            income.description = description
            income.amount = amount
            income.user = request.user
        
            income.save()
            messages.success(request, 'Income updated successfully')
            return redirect('incomes')
    except Exception as e:
        messages.error(request, f'An error occurred while editing the Income: {e}')
        return render(request, 'incomes/edit_income.html', context)


@login_required(login_url='/authentication/login')
def delete_income(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income deleted successfully')
    return redirect('incomes')


def search_incomes(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        incomes = Income.objects.filter(date__istartswith=search_str, user=request.user) \
            | Income.objects.filter(source__name__icontains=search_str, user=request.user) \
            | Income.objects.filter(description__icontains=search_str, user=request.user) \
            | Income.objects.filter(amount__istartswith=search_str, user=request.user)
        
        incomes = incomes.select_related('source')

        data = [{
            'id': income.id,
            'date': income.date.strftime('%Y-%m-%d'),
            'source': income.source.name if income.source else '',
            'description': income.description,
            'amount': income.amount
        } for income in incomes]

        print(f"Incomes found: {data}")
        return JsonResponse(data, safe=False)
