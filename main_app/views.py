from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import AIChat, AIMessage
from django.http import JsonResponse
import json
import ollama


# Главная страница — убрали main_app/
def index_view(request):
    return render(request, 'index.html')


# Страница казино — убрали main_app/
def casino_view(request):
    return render(request, 'casino.html')

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

@login_required(login_url='/login/')
def casino_action_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Неверный формат запроса!'}, status=400)
        action = data.get('action')
        profile = request.user.profile

        if action in ('spin', 'win'):
            try:
                bet = int(data.get('bet') or 50)
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'Неверная ставка!'}, status=400)
            if bet < 1:
                return JsonResponse({'success': False, 'error': 'Минимальная ставка — 1 ВПК!'})

        if action == 'spin':
            if profile.balance < bet:
                return JsonResponse({'success': False, 'error': 'Недостаточно ВПК!'})

            profile.balance -= bet
            profile.save()
            return JsonResponse({'success': True, 'balance': profile.balance})

        elif action == 'win':
            win_type = data.get('type', 'small')

            # ЖЕСТКАЯ МАТЕМАТИКА: мелкий выигрыш возвращает лишь х0.5 (чистый убыток!)
            if win_type == 'maxwin':
                prize = bet * 20
            else:
                prize = int(bet * 0.5)

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


@login_required
def polytech_ai_view(request):
    user_chats = AIChat.objects.filter(user=request.user)

    # Если у юзера вообще нет чатов в БД — принудительно создаем один базовый
    if not user_chats.exists():
        AIChat.objects.create(user=request.user, title="Новый диалог")
        user_chats = AIChat.objects.filter(user=request.user)

    active_chat = user_chats.first()

    # ОБРАБОТКА AJAX POST (Отправка реплики)
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        chat_id = request.POST.get("chat_id", "").strip()
        user_query = request.POST.get("query", "").strip()

        if not user_query:
            return JsonResponse({"error": "Вы отправили пустое сообщение"}, status=400)

        # Защита от пустых/неверных ID чата
        if not chat_id or chat_id == "None" or chat_id == "null" or chat_id == "":
            chat = active_chat
        else:
            try:
                chat = AIChat.objects.get(id=chat_id, user=request.user)
            except (AIChat.DoesNotExist, ValueError):
                chat = active_chat

        # Сохраняем входящий запрос в БД
        AIMessage.objects.create(chat=chat, role='user', content=user_query)

        # Интеллектуальное переименование первой темы
        if chat.title == "Новый диалог":
            chat.title = user_query[:25] + "..." if len(user_query) > 25 else user_query
            chat.save()

        try:
            # Сбор контекста всей переписки для Ollama
            db_messages = chat.messages.all()
            ollama_context = [{'role': 'system', 'content': 'Ты — Ассистент Политех AI. Слава Политеху!'}]
            for msg in db_messages:
                ollama_context.append({'role': msg.role, 'content': msg.content})

            # Обращение к локальной модели
            response = ollama.chat(model='qwen2.5-coder:7b', messages=ollama_context)
            ai_response = response['message']['content']

            # Запись ответа ИИ в БД
            AIMessage.objects.create(chat=chat, role='ai', content=ai_response)

            return JsonResponse({
                "response": ai_response,
                "chat_title": chat.title,
                "chat_id": chat.id
            })
        except Exception as e:
            # Возвращаем 500 ошибку в формате JSON, фронтенд её красиво отобразит в пузыре чата
            return JsonResponse({"error": f"Ошибка Ollama: {str(e)}. Проверьте терминал."}, status=500)

    # ОБРАБОТКА AJAX GET (Клик по истории в сайдбаре)
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        chat_id = request.GET.get("chat_id")
        try:
            chat = AIChat.objects.get(id=chat_id, user=request.user)
            messages = chat.messages.all().values('role', 'content')
            return JsonResponse({"chat_title": chat.title, "messages": list(messages)})
        except (AIChat.DoesNotExist, ValueError):
            return JsonResponse({"error": "Чат не найден"}, status=404)

    # ОБЫЧНЫЙ POST (Кнопка "Новый диалог")
    if request.method == "POST" and "create_chat" in request.POST:
        new_chat = AIChat.objects.create(user=request.user, title="Новый диалог")
        return JsonResponse({"chat_id": new_chat.id, "title": new_chat.title})

    # Обычный GET-рендер страницы
    return render(request, "polytech_ai.html", {
        "user_chats": user_chats,
        "active_chat": active_chat,
    })
