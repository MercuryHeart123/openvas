from django.urls import path
from . import controller
urlpatterns = [
    path('gmp', controller.loginController),
    # path('interface/', views.viewInterface),
    path('gettask/', controller.getTaskController),
    path('getscanner/', controller.getScannerController),
    path('createtask/', controller.createTaskController),
    path('createtarget/', controller.createTargetController),
    path('gettarget/', controller.getTargetController),
    path('getreport/', controller.getReportController),
    path('starttask/', controller.startTaskController),
    path('getnvt/', controller.getNvtController)
]
