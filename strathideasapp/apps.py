from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class StrathideasappConfig(AppConfig):
    name = 'strathideasapp'
    verbose_name = _('strathideasapp')

    def ready(self):
        import strathideasapp.signals

