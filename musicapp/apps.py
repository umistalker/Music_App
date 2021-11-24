from django.apps import AppConfig

# from suit.config import DjangoSuitConfig
# from suit.menu import ParentItem, ChildItem

class MusicappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'musicapp'


# class DjangoSuitConfig(DjangoSuitConfig):
#     layout = 'horizontal'