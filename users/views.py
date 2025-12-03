from django.contrib import messages, auth
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


# Create your views here.
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Mật khẩu không trùng khớp!')
            return redirect('home')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được đăng ký')
            return redirect('home')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại, vui lòng chọn tên khác!')
            return redirect('home')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        login(request, user)
        messages.success(request, 'Đăng ký thành công!')
        return redirect('home')
    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        login_input = request.POST.get('username')
        password = request.POST.get('password')

        username_to_login = login_input
        if '@' in login_input:
            try:
                user_obj = User.objects.get(email=login_input)
                username_to_login = user_obj.username
            except User.DoesNotExist:
                pass

        user = auth.authenticate(request, username=username_to_login, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, f'Chào mừng trở lại, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Sai email/tên đăng nhập hoặc mật khẩu')
            return redirect('home')

    return redirect('home')

def logout_view(request):
    auth.logout(request)
    messages.success(request, 'Đã đăng xuất!')
    return redirect('home')