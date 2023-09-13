from django.apps import AppConfig
from openvas.getTask import GvmService
import logging


class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"

    def ready(self) -> None:
        gvm_service = GvmService()
        self.gvm_service = gvm_service
