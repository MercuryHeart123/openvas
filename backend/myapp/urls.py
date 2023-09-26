from django.urls import path
from . import controller
urlpatterns = [
    path('gmp', controller.loginController),
    path('download', controller.dowloadReportController),
]
