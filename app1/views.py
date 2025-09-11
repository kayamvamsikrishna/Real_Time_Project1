#what is api -----  API is like a middleman that helps two different apps or programs talk to each other and share information.
"Using the features and functionalities of another application or service in my own application to perform a specific task is known as using APIs."


"APIs allow an application to utilize the features and functionalities of another service or application to perform specific tasks."


from django.shortcuts import render

# Create your views here.
from app1.forms import *
from django.http import HttpResponse,HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse

from django.contrib.auth.decorators import login_required
#python -m pip install Pillow
#pip install requests
import requests
from django.shortcuts import render
from django.conf import settings
from app1.models import * 


def home(request):
    if request.session.get('username'):
        username = request.session.get('username', request.user.username)
        pf= request.user.profile
        pic = pf.profile_pic.url 
        d = {'username': username, 'pic': pic}
        return render(request, 'home.html', d)
    else:
        pic='/media/default.jpg'
        d = {'pic': pic}
        return render(request, 'home.html',d) 

           

def registration(request):
    uf=UserForm()
    pf=ProfileForm()
    d={'uf':uf,'pf':pf}

    if request.method=='POST' and request.FILES:
        UFD=UserForm(request.POST)
        PFD=ProfileForm(request.POST,request.FILES)
        if UFD.is_valid() and PFD.is_valid():
            UFO=UFD.save(commit=False)
            password=UFD.cleaned_data['password']
            UFO.set_password(password)
            UFO.save()

            PFO=PFD.save(commit=False)
            PFO.profile_user=UFO
            PFO.save()

            send_mail('registration',
            'Thanks for registartion,ur registration is Successfull',
            'kayamvamsikrishna@gmail.com',
            [UFO.email],
            fail_silently=False
            )
            
            login_url = reverse('user_login')
            html = f'''<html>
                            <body><br>
                                    <h6>IF U WANT TO GET LOGIN THEN TAP HERE </h6>
                                <br>
                                <a href="{login_url}">USER LOGIN</a>
                            </body>
                        </html>'''
            return HttpResponse(f'REGISTRATION IS DONE SUCCESSFULLY {html}')
        else:
            registration_url = reverse('registration')
            html = f'''
            <html>
                <body><br>
                         <h6>TRY AGAIN PLEASE TAP HERE </h6>
                        <br>
                    <a href="{registration_url}">REGISTRATION</a>
                </body>
            </html>'''
            return HttpResponse(f'DATA IS INVALID{html}')


    return render(request,'registration.html',d)

def user_login(request):
    if request.method=='POST':
        username=request.POST['un']
        password=request.POST['pw']

        AUO=authenticate(username=username,password=password) #It checks if a user exists with the provided username and password. if TRUE ELSE FALSE
        if AUO and AUO.is_active:#IF TRUE
            login(request,AUO) 
            request.session['username']=username   
            '''
            Manually storing the username in the session dictionary.

            Note: This is not necessary, as request.user is already available once the user is logged in.

            You might use it if you're tracking usernames separately or outside of Django's auth system.
            
            '''
            return HttpResponseRedirect(reverse('home'))
        else:
            login_url = reverse('user_login')
            html = f'''
            <html>
                <body><br>
                         <h6>TRY AGAIN PLEASE TAP HERE </h6>
                        <br>
                    <a href="{login_url}">USER LOGIN</a>
                </body>
            </html>'''
            return HttpResponse(f'Invalid Credentials {html} ')
    return render(request,'user_login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

@login_required
def profile_display(request):
    un=request.session.get('username')
    UO=User.objects.get(username=un)
    PO=Profile.objects.get(profile_user=UO)
    d={'UO':UO,'PO':PO}
    return render(request,'profile_display.html',d)

@login_required
def change_password(request):

    if request.method=='POST':
        pw=request.POST['password']

        un=request.session.get('username')
        UO=User.objects.get(username=un)

        UO.set_password(pw)
        UO.save()
        return HttpResponse('password is changed successfully')
    return render(request,'change_password.html')


def reset_password(request):

    if request.method=='POST':
        un=request.POST['un']
        pw=request.POST['pw']

        LUO=User.objects.filter(username=un)

        if LUO:
            UO=LUO[0]
            UO.set_password(pw)
            UO.save()
            login_url = reverse('user_login')
            html = f'''<html>
                            <body><br>
                                    <h6>IF U WANT TO GET LOGIN THEN TAP HERE </h6>
                                <br>
                                <a href="{login_url}">USER LOGIN</a>
                            </body>
                        </html>'''
            return HttpResponse(f'password reset is done {html}')
        else:
            return HttpResponse('user is not present in my DB')
        

        return HttpResponse('Reset password is done successfully')
    return render(request,'reset_password.html')





@login_required
def search(request):
    if request.method == 'POST':
        city_name = request.POST.get('city', '').strip()

        if not city_name:
            return HttpResponse("Please enter a city name.", status=400)

        #Weather API 
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={settings.OPENWEATHER_API_KEY}"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        if str(weather_data.get('cod')) != '200':
            return HttpResponse("City not found.", status=404)

        main_data = weather_data.get('main', {})
        wind_data = weather_data.get('wind', {})
        coord_data = weather_data.get('coord', {})

        # Convert temperature from Kelvin to Celsius
        temperature = main_data.get('temp')
        temperature_celsius = round(temperature - 273.15, 2) if temperature else None
        humidity = main_data.get('humidity')
        feels_like = main_data.get('feels_like')
        weather = feels_like
        speed = wind_data.get('speed')
        lat = coord_data.get('lat')
        lon = coord_data.get('lon')

        #Save to database
        obj = WeatherData.objects.create(
            username=request.user,
            city=city_name,
            temperature=temperature_celsius,
            humidity=humidity,
            weather=weather,
            speed=speed
        )

        #articles
        gnews_url = f"https://gnews.io/api/v4/search?q={city_name}&lang=en&country=in&max=5&token={settings.GNEWS_API_KEY}"
        gnews_response = requests.get(gnews_url)
        gnews_data = gnews_response.json()
        articles = gnews_data.get('articles', [])

        context = {
            'obj': obj,
            'articles': articles,
            'lat': lat,
            'lon': lon,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
        }

        return render(request, 'search.html', context)

    return render(request, 'search.html')
