from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth import authenticate,login
from django.contrib import  messages
from instamojo_wrapper import Instamojo
from django.conf import settings
api = Instamojo(api_key=settings.API_KEY,
                auth_token=settings.AUTH_TOKEN,endpoint="https://test.instamojo.com/api/1.1/")
# Create your views here.
def home(request):
    pizzas = Pizza.objects.all()
    context={"pizzas": pizzas}
    return render(request,'home.html',context)

def login_page(request):
  if request.method == 'POST':
    try:
     username=request.POST.get('username')
     password=request.POST.get('password')

     user_obj = User.objects.filter(username=username)
     if not user_obj.exists():
       messages.warning(request,'User not Found') 
       return redirect('/login/')
     user_obj=authenticate(username=username,password=password)
     if user_obj:
        login(request, user_obj)
        messages.success(request, 'Log-in Done')
        return redirect('/')
     messages.warning(request, 'Please Enter Your Correct Password')
     return redirect('/login/')
    except Exception as e:
     messages.error(request, 'Somthing Went Wrong')
     return redirect('/login/')
    
  return render(request,'login.html') 

def register_page(request):
  if request.method == 'POST':
    try:
     username=request.POST.get('username')
     password=request.POST.get('password')

     user_obj = User.objects.filter(username=username)
     if user_obj.exists():
       messages.warning(request,'Username Already Taken') 
       return redirect('/register/')
     user_obj=User.objects.create(username=username)
     user_obj.set_password(password)
     user_obj.save()
     messages.success(request, 'Your Account has been Created')
     return redirect('/login/')
    except Exception as e:
     messages.error(request, 'Somthing Went Wrong')
     return redirect('/register/')

  return render(request,'register.html')    

def add_cart(request, pizza_uid):
    user= request.user
    pizza_obj=Pizza.objects.get(uid=pizza_uid)
    cart , _=Cart.objects.get_or_create(user=user,is_paid=False)
    cart_items= CartItems.objects.create(
      cart=cart,
      pizza=pizza_obj
    )
    return redirect('/')


def cart(request):
  cart=Cart.objects.get(is_paid=False,user=request.user)
  response=api.payment_request_create(
    amount=cart.get_cart_total(),
    purpose="Order",
    buyer_name=request.user.username,
    email="bnanda405@gmail.com",
    redirect_url="http://127.0.0.1:8000/success/"
  )
  cart.instamojo_id=response['payment_request']['id']
  cart.save()
  # print(response)
  context={'carts': cart,"payment_url": response['payment_request']['longurl']}
  print(response)
  return render(request, "cart.html",context)

def remove_cart_items(requset,cart_item_uid):
  try:
   CartItems.objects.get(uid=cart_item_uid).delete()
   return redirect('/cart/')

  except Exception as e:
    print(e)  

def orders(request):
  orders = Cart.objects.filter(is_paid=True,user=request.user)
  context={'orders':orders}
  return render(request,'orders.html',context)


def success(request):
  payment_request=request.GET.get('payment_request_id')
  cart=Cart.objects.get(instamojo_id = payment_request)
  cart.is_paid=True
  cart.save()
  return redirect('/orders/')

