from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils.html import escape
from django.urls import reverse
from django.http import HttpResponse , HttpResponseRedirect
from weather_app.models import User
from weather_app.models import Subscribe
from weather_app.models import Favorites
import requests
import datetime


def index(request):
    min_temp=0
    max_temp=0
    api_key = 'e623f0a260633ca5e13c97c2a9e5b131'
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}'

    subscribe1 = Subscribe.objects.all().filter(user_id=request.session.get('user_id'))
    favcity = Favorites.objects.all().filter(user_id=request.session.get('user_id'))

    if request.method == 'POST':
        city1 = request.POST['city1']
        if len(city1) == 0:
            return redirect('index')

        city2 = request.POST.get('city2', None)

        weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, api_key, current_weather_url, forecast_url)

        if city2:
            weather_data2, daily_forecasts2 = fetch_weather_and_forecast(city2, api_key, current_weather_url,
                                                                         forecast_url)
        else:
            weather_data2, daily_forecasts2 = None, None

        context = {
            'favcity': favcity,
            'sub': subscribe1,
            'weather_data1': weather_data1,
            'daily_forecasts1': daily_forecasts1,
            'weather_data2': weather_data2,
            'daily_forecasts2': daily_forecasts2,
        }

        if not weather_data1:
            messages.warning(request, f"Weather data for {city1} is not available.")

        return render(request, 'weather_app/index.html', context)
    else:
        context = {
            'favcity': favcity,
            'sub': subscribe1,
        }

        # Check temperature for each city in favcity
        if 'temp_alert_shown' not in request.session:
            for fav in favcity:
                city_forecast = fetch_weather_and_forecast(fav.city, api_key, current_weather_url, forecast_url)[1]
                for forecast in city_forecast:
                    min_temp = forecast['min_temp']
                    max_temp = forecast['max_temp']
                    if min_temp < 10 or max_temp > 40:
                        # Display temperature alert message
                        messages.warning(request, f"Temperature for {fav.city} is outside the desired range!")
                        break

            request.session['temp_alert_shown'] = True
        return render(request, 'weather_app/index.html', context)
         
             

       
    

# def check_favcity(request):
#     favcity = Favorites.objects.filter(user_id=request.session.get('user_id'))

#     if favcity.exists():
#         data = ''
#         for fav in favcity:
#             data += fav.city + '\n'  # Replace 'name' with the actual field you want to include
#         return HttpResponse("favcity has data:\n" + data)
#     else:
#         return HttpResponse("favcity is empty")

def index2(request):
    api_key = 'e623f0a260633ca5e13c97c2a9e5b131'
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}'

    if request.method == 'POST':
        city1 = request.POST['city1']
        if(len(city1) == 0):
          messages.error(request, 'Field was Empty!')
          return redirect('index2')
        city2 = request.POST.get('city2', None)

        weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, api_key, current_weather_url, forecast_url)

        if city2:
            weather_data2, daily_forecasts2 = fetch_weather_and_forecast(city2, api_key, current_weather_url,
                                                                         forecast_url)
        else:
            weather_data2, daily_forecasts2 = None, None

        context = {
            'weather_data1': weather_data1,
            'daily_forecasts1': daily_forecasts1,
            'weather_data2': weather_data2,
            'daily_forecasts2': daily_forecasts2,
        }

        if not weather_data1:
            messages.warning(request, f"Weather data for {city1} is not available.")
        if not weather_data2:
            messages.warning(request, f"Weather data for {city2} is not available.")


        return render(request, 'weather_app/index2.html', context)
    else:
        return render(request, 'weather_app/index2.html')


def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    response = requests.get(current_weather_url.format(city, api_key)).json()
    
    if response.get('cod') == '404':
        return None, None


    forecast_response = requests.get(forecast_url.format(city, api_key)).json()

    weather_data = {
        'city': city,
        'temperature': round(response['main']['temp'] - 273.15, 2),
        'description': response['weather'][0]['description'],
        'icon': response['weather'][0]['icon'],
    }

    target_date = datetime.date.today() + datetime.timedelta(days=1)
    daily_forecasts = []
    day_counter = 0
    for daily_data in forecast_response['list'][:7]:
        daily_forecast_data = {
            'day': datetime.datetime.fromtimestamp(daily_data['dt'] + day_counter * 24 * 3600).strftime('%A'),
            'min_temp': round(daily_data['main']['temp_min']-273),
            'max_temp': round(daily_data['main']['temp_max']-273),
            'description': daily_data['weather'][0]['description'],
            'icon': daily_data['weather'][0]['icon'],
        }
        daily_forecasts.append(daily_forecast_data)
        day_counter += 1
        if day_counter >= 7:
            break

    return weather_data, daily_forecasts


def user_login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        u = User.objects.get(username = username)
        request.session['user_id'] = u.id
        user_id= request.session.get('user_id')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Redirect to the index page after successful login
        else:
            error_message = 'Invalid username or password.'
            messages.error(request, error_message)  # Add an error message to be displayed in the template
            return render(request, 'weather_app/login.html')
    else:
        return render(request, 'weather_app/login.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful registration
        else:
            error_message = 'Registration failed. Please check the entered information.'
            return render(request, 'weather_app/register.html', {'form': form, 'error_message': error_message})
    else:
        form = UserCreationForm()
    return render(request, 'weather_app/register.html', {'form': form})


def default_page(request):
    return redirect('index2')

def logout(request):
     request.session.flush()
     return redirect('index2')

def subscribe(request):
    user_id = request.session.get('user_id')

    if Subscribe.objects.filter(user_id=user_id).exists():
         messages.success(request, 'Already Subscribed!')
    else:     
        subscribee = Subscribe(user_id = user_id)
        subscribee.save()
        messages.success(request, 'Subscribed!')
    return redirect('index')   

def unsubscribe(request):
    user_id = request.session.get('user_id')
    Subscribe.objects.filter(user_id=user_id).delete()
    return redirect('index')

def remove(request,id):
    Favorites.objects.filter(id = id).delete()
    return redirect('index')

    
    

    

def add_to_favorites(request):
    if request.method == 'POST':
        city = request.POST['city']
        if city != "":
            user_id = request.session.get('user_id')
            if user_id:
                # Check if the city is already in favorites for the user
                if Favorites.objects.filter(city=city, user_id=user_id).exists():
                    messages.success(request, 'Already present in favorites!')
                else:
                    favorite = Favorites(city=city, user_id=user_id)
                    favorite.save()
                    messages.success(request, 'Added to favorites!')
            else:
                messages.error(request, 'User is not logged in.')
        else:
            messages.error(request, 'Field was empty.')

    return redirect('index')
            
   
