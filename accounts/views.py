from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from .forms import *
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_user, admin_only
from django.contrib.auth.models import Group
# Create your views here.
#-------------------(USER-PAGE VIEWS) -------------------

@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def userPage(request):
	orders = request.user.customer.order_set.all()
	total_orders = orders.count()

	delivered = orders.filter(status = 'Delivered').count()
	pending = orders.filter(status = 'Pending').count()
	print('ORDERS:', orders)
	context = {'orders': orders, 'total_orders':total_orders, 'delivered':delivered, 'pending':pending }
	return render(request, 'accounts/user.html', context)

#-------------------(Account Setting VIEWS) -------------------


@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def accountSettings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)

	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES,instance=customer)
		if form.is_valid():
			form.save()

	context = {'form':form}
	return render(request, 'accounts/account_settings.html', context)

#-------------------(REGISTER VIEWS) -------------------
@unauthenticated_user
def registerPage(request):
	
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			
			group = Group.objects.get(name='customer')# customer adding to group
			user.groups.add(group)
			Customer.objects.create(
				user=user,
				name=user.username,
			)

			messages.success(request,'Account Created for '+ username)
			return redirect('login')
			
	context = {'form':form}
	return render(request, 'accounts/register.html', context)
# def registerPage(request):
# 	if request.user.is_authenticated:
# 		return redirect('home')
# 	else:
# 		form = CreateUserForm()
# 		if request.method == 'POST':
# 			form = CreateUserForm(request.POST)
# 			if form.is_valid():
# 				form.save()
# 				user = form.cleaned_data.get('username')
# 				messages.success(request,'Account Created for '+ user)
# 				return redirect('login')
			
# 	context = {'form':form}
# 	return render(request, 'accounts/register.html', context)

#-------------------(LOGIN VIEWS) -------------------

@unauthenticated_user
def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
			
		if user is not None:
			login(request, user)
			return redirect('home')
		else:
			messages.info(request, 'Wrong Username OR Password')
				
	context = {}
	return render(request, 'accounts/login.html', context)

#-------------------(LOGOUT VIEWS) -------------------

def logoutUser(request):
	logout(request)
	return redirect('login')

#-------------------(Home VIEWS) -------------------
@login_required(login_url='login')
@admin_only
# @allowed_user(allowed_roles=['admin'])
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    
    total_customers = customers.count()
    total_orders = orders.count()

    delivered = orders.filter(status = 'Delivered').count()
    pending = orders.filter(status = 'Pending').count()


    context = {'orders': orders, 'customers': customers,'total_orders':total_orders, 'delivered':delivered, 'pending':pending }
    return render(request, 'accounts/dashboard.html', context)

#-------------------(PRODUCTS VIEWS) -------------------
@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def products(request):
   products = Product.objects.all()
   return render(request, 'accounts/products.html', {'products': products})

#-------------------(CUSTOMER VIEWS) -------------------
@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def customer(request,pk):

   customer = Customer.objects.get(id = pk)

   orders = customer.order_set.all()
   order_count = orders.count()

   orderFilter = OrderFilter(request.GET, queryset=orders)
   orders = orderFilter.qs

   context = {'customer':customer, 'orders': orders, 'order_count':order_count, 'orderFilter': orderFilter}
   return render(request, 'accounts/customer.html', context)

#-------------------(CREATE VIEWS) -------------------
@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def createOrder(request, pk):
	OrderFormSet = inlineformset_factory(Customer,Order, fields=('product','status'),extra=10)# parent model & chiled model
	customer = Customer.objects.get(id=pk)
	action = 'create'
	formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
	# form = OrderForm(initial={'customer':customer})
	if request.method == 'POST':
		# form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST,instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')

	context =  {'formset':formset}
	return render(request, 'accounts/order_form.html', context)

#-------------------(UPDATE VIEWS) -------------------
@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def updateOrder(request, pk):
	action = 'update'
	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)

	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('/')

	context =  {'action':action, 'form':form}
	return render(request, 'accounts/order_form.html', context)

#-------------------(DELETE VIEWS) -------------------
@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == 'POST':
		# customer_id = order.customer.id
		# customer_url = '/customer/' + str(customer_id)
		order.delete()
		return redirect('/')
		
	return render(request, 'accounts/delete_item.html', {'item':order})