from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json


# Главная страница — убрали main_app/
def index_view(request):
    return render(request, 'index.html')


# Страница казино — убрали main_app/
def casino_view(request):
    return render(request, 'casino.html')


# Логика регистрации — убрали main_app/
def register_view(request):
    if request.method == 'POST':
        data = request.POST
        if User.objects.filter(username=data['username']).exists():
            return render(request, 'register.html', {'error': 'Этот логин уже славит Политех!'})

        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        login(request, user)
        return redirect('/')
    return render(request, 'register.html')


# Логика авторизации — убрали main_app/
def login_view(request):
    if request.method == 'POST':
        data = request.POST
        user = authenticate(username=data['username'], password=data['password'])
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль!'})
    return render(request, 'login.html')

@login_required(login_url='/login/')
def profile_view(request):
    return render(request, 'profile.html')

# Функция выхода из системы
def logout_view(request):
    logout(request)
    return redirect('/')


# Обновите эту функцию в main_app/views.py

# Обновите эту функцию в main_app/views.py

# Обновите эту функцию в main_app/views.py

@login_required(login_url='/login/')
def casino_action_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        profile = request.user.profile

        if action == 'spin':
            bet = int(data.get('bet', 50))
            if bet < 1:
                return JsonResponse({'success': False, 'error': 'Минимальная ставка — 1 ВПК!'})
            if profile.balance < bet:
                return JsonResponse({'success': False, 'error': 'Недостаточно ВПК!'})

            profile.balance -= bet
            profile.save()
            return JsonResponse({'success': True, 'balance': profile.balance})

        elif action == 'win':
            win_type = data.get('type', 'small')
            bet = int(data.get('bet', 50))

            # ЖЕСТКАЯ МАТЕМАТИКА: мелкий выигрыш возвращает лишь х0.5 (чистый убыток!)
            if win_type == 'maxwin':
                prize = bet * 20
            else:
                prize = int(bet * 10)

            profile.balance += prize
            profile.save()
            return JsonResponse({'success': True, 'balance': profile.balance, 'prize': prize})

    return JsonResponse({'success': False})


@login_required(login_url='/login/')
def deposit_view(request):
    if request.method == 'POST':
        amount = int(request.POST.get('amount', 0))
        profile = request.user.profile
        profile.balance += amount
        profile.save()
        return render(request, 'deposit.html', {'success': True, 'amount': amount})
    return render(request, 'deposit.html')
