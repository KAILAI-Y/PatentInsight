from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib import messages


def index(request):
    # 初始化表单
    register_form = UserCreationForm()
    login_form = AuthenticationForm()

    if request.method == "POST":
        print("收到 POST 请求")
        if "register_form" in request.POST:
            print("正在处理注册表单")
            register_form = UserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                print("用户注册成功：", user.username)
                login(request, user)  # 注册成功后自动登录用户
                messages.success(request, "注册成功！已为您自动登录。")
                return redirect("index")  # 重定向回首页
            else:
                print("注册表单无效")
        elif "login_form" in request.POST:  # 检查登录表单是否被提交
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                username = request.POST["username"]
                password = request.POST["password"]
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "登录成功！")
                    return redirect("index")  # 登录成功后重定向回首页

    return render(
        request,
        "index.html",
        {"register_form": register_form, "login_form": login_form},
    )


def logout_view(request):
    logout(request)
    return redirect("index")
