import re

from django.shortcuts import render, redirect, HttpResponse, reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.conf import settings
from django.core import serializers
from django.template import RequestContext
from django.contrib import messages

from apps.user.models import User, Address, UserImage, Shop, ShopImage, ShopTypeDetail
from utils.fdfs.storage import FastDFSStorage
from utils import common
from celery_execute_task.sendmail import send_activate_email

from itsdangerous import TimedJSONWebSignatureSerializer as TJSS
from itsdangerous import SignatureExpired


def find_type(request):
    """根据店铺类型获取具体类型"""

    type_detail = request.GET.get('type_detail')
    shop_type_detail = serializers.serialize("json", ShopTypeDetail.objects.filter(type_code__contains=type_detail))
    return HttpResponse(shop_type_detail)


class RegisterView(View):
    """注册"""

    def get(self, request):
        """显示注册页面"""

        # 买家注册页面
        return render(request, 'register.html')

    def post(self, request):
        """显示注册处理"""

        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        cpassword = request.POST.get('cpwd')
        receiver = request.POST.get('receiver')
        phone = request.POST.get('phone')
        addr = request.POST.get('addr')
        email = request.POST.get('email')
        sex = request.POST.get('sex')
        mjsj = request.POST.get('mjsj')
        img = request.FILES.get('file')

        # 校验数据
        if not all([username, password, cpassword, receiver, phone, addr, email, sex, mjsj, img]):
            # 缺少相关数据
            return render(request, 'register.html', {'errmsg': '缺少相关数据'})

        rec = FastDFSStorage().save(img.name, img)

        # 校验密码是否一致
        if not (password == cpassword):
            # 两次输入密码不一致
            return render(request, 'register.html', {'errmsg': '两次输入密码不一致'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            # 邮箱不规范
            return render(request, 'register.html', {'errmsg': '邮箱不规范'})

        # 校验用户名是否重复
        if common.verify_exist(request, 'username', username):
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 校验手机号码是否重复
        if common.verify_exist(request, 'phone', phone):
            return render(request, 'register.html', {'errmsg': '手机号码已存在'})

        # 校验邮箱是否重复
        if common.verify_exist(request, 'email', email):
            return render(request, 'register.html', {'errmsg': '邮箱已存在'})

        # 业务处理
        # user表添加数据
        user = User.objects.create_user(username, email, password)
        # 1:男 0:女
        user.sex = sex
        # 0:买家 1:商家
        user.is_staff = mjsj
        user.phone = phone
        user.real_name = receiver

        # 读取上传的文件中的file项为二进制文件
        # file_content = ContentFile(img.read())
        # user.image.save(img.name, file_content)
        user.is_active = 1  # 设置为未激活状态
        user.save()

        # 处理发送邮件
        # 加密用户的身份信息，生成激活token
        serializer = TJSS(settings.SECRET_KEY, 900)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        # 默认解码为utf8
        token = token.decode()
        # 使用celery发邮件
        send_activate_email.delay(email, username, token)

        # address表添加数据
        address = Address()
        address.receiver = receiver
        address.phone = phone
        address.addr = addr
        address.is_default = True
        address.user = user
        lat_lng = common.get_lng_lat(addr)
        address.lat = lat_lng['lat']
        address.lng = lat_lng['lng']
        address.save()

        # user_image 表添加数据
        user_image = UserImage()
        user_image.user = user
        user_image.image = rec
        user_image.save()

        # 返回响应
        if int(mjsj):
            # 店铺注册页面
            return render(request, 'sj_register.html', {'user': user.id})
            # return redirect(reverse('user:sj_register'))
        else:
            # 买家登录页面
            # return render(request, 'login.html', locals())
            return redirect(reverse('user:login'))


class UserActivate(View):
    """用户通过邮件激活功能"""

    def get(self, request, token):
        """点击邮件链接激活业务处理"""

        serializer = TJSS(settings.SECRET_KEY, 900)
        try:
            info = serializer.loads(token)

            # 获取要激活用户的id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse('user:login'))

        except SignatureExpired as se:
            # 激活链接已过期，应重发激活邮件
            return HttpResponse('激活链接已过期，请注意查收新的激活邮件！')


class ShopRegisterView(View):
    """店铺注册处理"""

    def get(self, request):
        """显示注册页面"""

        return render(request, 'sj_register.html')

    def post(self, request):
        """显示注册处理"""

        # 接收数据
        shop_name = request.POST.get('shop_name')
        shop_type = request.POST.get('bus_style')
        shop_addr = request.POST.get('shop_addr')
        shop_user = request.POST.get('shop_user')
        shop_price = request.POST.get('shop_price')
        img = request.FILES.get('shop_file')
        receive_start = request.POST.get('receive_start')
        receive_end = request.POST.get('receive_end')
        if not all([shop_name, shop_type, shop_addr, img, shop_user, receive_start, receive_end]):
            # 数据不完整
            return render(request, 'sj_register.html', {'errmsg': '缺少相关数据'})

        rec = FastDFSStorage().save(img.name, img)

        # 校验店铺名称是否重复
        try:
            shop = Shop.objects.get(shop_name=shop_name)
        except Shop.DoesNotExist:
            shop = None
        if shop:
            return render(request, 'sj_register.html', {'errmsg': '店铺名已存在'})

        df_shop = Shop(shop_name=shop_name, shop_type=shop_type, shop_addr=shop_addr, user_id=shop_user,
                       shop_price=shop_price, receive_start=receive_start, receive_end=receive_end, high_opinion='0')
        df_shop.save()

        shop_image = ShopImage(image=rec, shop_id=df_shop.id)
        shop_image.save()

        return redirect(reverse('user:login'))


# /user/login
class LoginView(View):
    """登录"""

    def get(self, request):
        """显示登录页面"""

        # 判断COOKIES是否存在用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        # 使用模板
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        """登录校验"""

        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '请输入用户名和密码'})

        # 业务处理:登录校验
        user = None
        login_user = authenticate(username=username, password=password)
        login_phone = authenticate(phone=username, password=password)
        login_email = authenticate(email=username, password=password)

        if login_user is not None:
            user = login_user
        if login_phone is not None:
            user = login_phone
        if login_email is not None:
            user = login_email

        if user:
            # 用户名密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request, user)

                # 判断商家买家，跳转不同首页，1为商家
                if user.is_staff:
                    response = redirect(reverse('goods:sj_index'))
                    # response = render(request, 'sj_index.html')
                else:
                    response = redirect(reverse('goods:index'))  # HttpResponseRedirect
                    # response = render(request, 'index.html')
                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            messages.error(request, "用户名或密码错误")
            return render(request, 'login.html', locals(), RequestContext(request))


class LogoutView(View):
    '''退出登录'''

    def get(self, request):
        '''退出登录'''

        # 清除用户的session信息
        logout(request)

        # 跳转到登录
        return render(request, 'login.html')
