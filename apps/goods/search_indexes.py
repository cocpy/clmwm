# 本文件名称不允许修改，否则将无法创建索引
from haystack import indexes
from apps.user.models import Shop
# 类名必须为模型名+Index，比如模型Shop,则索引类为ShopIndex
# 其对应的索引模板路径应为/项目的应用模块名称/templates/search/indexes/项目的应用模块名称/模型（小写）_text.txt


class ShopIndex(indexes.SearchIndex, indexes.Indexable):
    # doucument=True代表搜索引擎将使用此字段的内容作为索引进行检索
    # use_template=True代表使用索引模板建立索引文件
    text = indexes.CharField(document=True, use_template=True)
    # 将索引类与模型Shop进行绑定

    def get_model(self):
        return Shop

    # 设置索引的查询范围
    def index_queryset(self, using=None):
        return self.get_model().objects.all()
