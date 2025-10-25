from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pcb/test/', views.pcb_test, name='pcb_test'),
    path('pcb/create/', views.pcb_create, name='pcb_create'),
    path('pcb/<int:pcb_id>/verify/', views.pcb_qa_verify, name='pcb_qa_verify'),
    path('module/assemble/', views.module_assemble, name='module_assemble'),
    path('module/functional-test/', views.module_functional_test, name='module_functional_test'),
    path('module/sign-off/', views.module_sign_off, name='module_sign_off'),
    path('pcb/<int:pcb_id>/', views.pcb_detail, name='pcb_detail'),
]