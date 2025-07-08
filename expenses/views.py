from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Category, Expense
import json
import datetime

@login_required(login_url='/authentication/login')
def index(request):
    try:
        categories = Category.objects.all()
        expenses = Expense.objects.filter(user=request.user)
        
        paginator = Paginator(expenses, 5)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator, page_number)
        
        context = {
            'expenses': expenses,
            'page_obj': page_obj
        } 
        return render(request, 'expenses/index.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred while fetching Expenses: {e}')
        return render(request, 'expenses/index.html', {'expenses': []})


@login_required(login_url='/authentication/login')
def add_expense(request):
    try:
        categories = Category.objects.all()
        context = {
            'categories': categories,
            'values': request.POST
        }

        if request.method == 'GET':
            return render(request, 'expenses/add_expense.html', context)
        elif request.method == 'POST':
            date = datetime.datetime.strptime(request.POST['date'], "%Y-%m-%d").date()

            # category
            category = request.POST['category']
            if not category:
                messages.error(request, 'Category is required')
                return render(request, 'expenses/add_expense.html', context)
            else:
                category = Category.objects.get(name=category)
                if not category:
                    messages.error(request, 'Category does not exist')
                    return render(request, 'expenses/add_expense.html', context)
                
            # description
            description = request.POST['description']
            if not description:
                messages.error(request, 'Description is required')
                return render(request, 'expenses/add_expense.html', context)

            # amount
            amount = request.POST['amount'] 
            if not amount:
                messages.error(request, 'Amount is required')
                return render(request, 'expenses/add_expense.html', context)
            
            Expense.objects.create(
                date=date, 
                category=category, 
                description=description, 
                amount=amount, 
                user=request.user
            )
            messages.success(request, 'Expense saved successfully')
            return redirect('expenses')
    except Exception as e:
        messages.error(request, f'An error occurred while adding the Expense: {e}')
        return render(request, 'expenses/add_expense.html', context)


@login_required(login_url='/authentication/login')
def edit_expense(request, id):
    try:
        expense = Expense.objects.get(pk=id)
        categories = Category.objects.all()
        context = {
            'categories': categories,
            'values': expense,
            'expense': expense
        }

        if request.method == 'GET':
            return render(request, 'expenses/edit_expense.html', context)
        elif request.method == 'POST':
            date = datetime.datetime.strptime(request.POST['date'], "%Y-%m-%d").date()

            # category
            category = request.POST['category']
            if not category:
                messages.error(request, 'Category is required')
                return render(request, 'expenses/edit_expense.html', context)
            else:
                category = Category.objects.get(name=category)
                if not category:
                    messages.error(request, 'Category does not exist')
                    return render(request, 'expenses/edit_expense.html', context)
                
            # description
            description = request.POST['description']
            if not description:
                messages.error(request, 'Description is required')
                return render(request, 'expenses/edit_expense.html', context)

            # amount
            amount = request.POST['amount'] 
            if not amount:
                messages.error(request, 'Amount is required')
                return render(request, 'expenses/edit_expense.html', context)

            expense.date = date
            expense.category = category
            expense.description = description
            expense.amount = amount
            expense.user = request.user
        
            expense.save()
            messages.success(request, 'Expense updated successfully')
            return redirect('expenses')
    except Exception as e:
        messages.error(request, f'An error occurred while editing the Expense: {e}')
        return render(request, 'expenses/edit_expense.html', context)


@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense deleted successfully')
    return redirect('expenses')


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(date__istartswith=search_str, user=request.user) \
            | Expense.objects.filter(description__icontains=search_str, user=request.user) \
            | Expense.objects.filter(amount__istartswith=search_str, user=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)
