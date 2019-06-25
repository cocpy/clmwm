from django.contrib import admin
from .models import *

# 将模型直接注册到admin后台
# admin.site.register(OrderInfo)

# 修改title和header
admin.site.site_title = 'clmwm后台管理'
admin.site.site_header = 'clmwm'


# 自定义OrderAdmin类并继承ModelAdmin
@admin.register(OrderInfo)
class OrderAdmin(admin.ModelAdmin):
    # 设置显示的字段
    list_display = ['order_id', 'user', 'addr', 'shop', 'comment']
    # 设置搜索字段，如有外键应使用双下划线连接两个模型的字段
    search_fields = ['order_id', 'user__id', 'addr__id', 'shop__id', 'comment']
    # 设置过滤器，如有外键应使用双下划线连接两个模型的字段
    list_filter = ['order_id']
    # 设置排序方式，['order_id']为升序，降序为['-order_id']
    ordering = ['-order_id']
    # 设置时间选择器，如字段中有时间格式才可以使用
    # date_hierarchy = Field
    # 在添加新数据时，设置可添加数据的字段
    fields = ['order_status', 'remarks', 'score', 'taxpayer_number', 'invoice_head']
    # 设置可读字段,在修改或新增数据时使其无法设置
    readonly_fields = ['order_id', 'user', 'addr', 'shop']

    # 重写get_readonly_fields函数，设置超级用户和普通用户的权限
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            self.readonly_fields = []
        return self.readonly_fields
    # 添加自定义字段，在属性list_display添加自定义字段total_price
    list_display.append('total_price')

    # 根据当前用户名设置数据访问权限
    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(id__lt=6)
