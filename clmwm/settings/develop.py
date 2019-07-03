# PEP8无需检测此处
from .base import *   # NOQA

# 以下内容由base.py文件剪切过来
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }

    'default': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'clmww',
         'USER': 'root',
         'PASSWORD': 'yourpassword',
         'HOST': '134.175.106.182',
         'PORT': 3306,
     }
}

# 以下为新增
# django的缓存配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # 提升Redis解析性能
            "PARSER_CLASS": "redis.connection.HiredisParser",
        }
    }
}

# 百度地图AK
BAIDU_AK = 'p0C5pNxcBpu7hYebHbkRqALvTltOX3OD'

# 发送邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# SMTP服务地址，使用其他服务器需更换
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
# 发送邮件的邮箱，换成自己的
EMAIL_HOST_USER = '15754324003@163.com'
# 在邮箱中设置的客户端授权密码，换成自己的
EMAIL_HOST_PASSWORD = 'mingrikejio8o2'
# 收件人看到的发件人，<>中地址必须与上方保持一致
EMAIL_FROM = 'c0c<15754324003@163.com>'

# django文件存储
# DEFAULT_FILE_STORAGE = 'clmwm.utils.fastdfs.fdfs_storage.FastDFSStorage'
# FastDFS
# FDFS_URL = 'http://域名:端口'
# FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')

# 设置Django的文件存储类
DEFAULT_FILE_STORAGE = 'utils.fdfs.storage.FDFSStorage'
# 设置fdfs使用的client.conf文件路径
FDFS_CLIENT_CONF = './utils/fdfs/client.conf'
# 设置fdfs存储服务器上nginx的IP和端口号
FDFS_URL = 'http://134.175.106.182:80/'

# 配置HayStack
HAYSTACK_CONNECTIONS = {
    'default': {
        # 设置搜索引擎，文件是apps下的goods的whoosh_cn_backend.py
        # 如果goods模块未在apps下请自行替换或者去掉apps
        'ENGINE': 'apps.goods.whoosh_cn_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
        'INCLUDE_SPELLING': True,
    },
}
# 设置每页显示的数据量
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 2
# 当数据库改变时，自动更新索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# APPID
ALIPAY_APPID = '2016100100636422'  # 沙箱APPID，生产环境须更改为应用APPID。
# 网关
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'  # 沙箱网关，生产环境须更改为正式网关。
# ALIPAY_URL = "https://openapi.alipay.com/gateway.do" # 正式网关，开发环境勿使用。
# 回调通知地址 36.104.214.196 127.0.0.1:8000
ALIPAY_NOTIFY_URL = "http://127.0.0.1:8000/order/result/"  # 如果只可以内网访问开发服务器
# ALIPAY_NOTIFY_URL = "http://36.104.214.196:8000/order/result/"  # 如果生产环境或外网可以访问开发服务器
# ALIPAY_RETURN_URL = "http://36.104.214.196:8000/order/result/"
# 使用密钥文件
APP_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'apps/order/app_private_key.pem'),
ALIPAY_PUBLIC_KEY_PATH = os.path.join(BASE_DIR, 'apps/order/alipay_public_key.pem')

INSTALLED_APPS +=[
    'debug_toolbar',  # 性能排查插件
]
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
INTERNAL_IPS = ['127.0.0.1']
