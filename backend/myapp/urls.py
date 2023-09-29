from django.urls import path
from . import controller
urlpatterns = [
    path('gmp', controller.loginController),
    path('logout', controller.logoutController),
    path('download', controller.dowloadReportController),
]
