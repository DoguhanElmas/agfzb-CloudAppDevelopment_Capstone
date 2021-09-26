from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from . import restapis
from . import models
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


def get_about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

def get_contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            print(user)
            return redirect('djangoapp:index')
        else:           
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

def logout_request(request):
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/user_registration.html', context)
            
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = 'https://3df11349.eu-gb.apigw.appdomain.cloud/api/dealership'
        context = {"dealerships": restapis.get_dealers_from_cf(url)}
        return render(request, 'djangoapp/index.html', context)


def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = 'https://3df11349.eu-gb.apigw.appdomain.cloud/api/review'
        context = {"reviews":  restapis.get_dealer_reviews_by_id_from_cf(url, dealer_id)}
        return render(request, 'djangoapp/dealer_details.html', context)

def add_review(request, dealer_id):
    print("request",request)
    print("dealerıd",dealer_id)
    if request.method == "GET":
        dealersid = dealer_id
        context = {
            "cars": models.CarModel.objects.all().filter(dealerid = dealersid),
            "dealerId":dealersid
        }
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
        if request.user.is_authenticated:
            form = request.POST
            # print("***************")
            # print(request.user)
            review = {
                "name": request.user.username,                
                "dealership": int(dealer_id),
                "review": form["content"],
                "purchase": form.get("purchasecheck"),
                }
            if form.get("purchasecheck"):
                review["purchase_date"] = datetime.strptime(form.get("purchasedate"), "%m/%d/%Y").isoformat()
                car = models.CarModel.objects.get(pk=form["car"])
                review["car_make"] = car.carmake.name
                review["car_model"] = car.name
                review["car_year"]= int(car.year.strftime("%Y"))
            json_payload = {"review": review}
            url = "https://3df11349.eu-gb.apigw.appdomain.cloud/api/submit"
            restapis.post_request(url, json_payload)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            return redirect("/djangoapp/login")
            
