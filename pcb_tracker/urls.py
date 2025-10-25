from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pcb-type/manage/', views.pcb_type_manage, name='pcb_type_manage'),
    path('batch/manage/', views.batch_manage, name='batch_manage'),
    path('pcb/test/', views.pcb_test, name='pcb_test'),
    path('pcb/create/', views.pcb_create, name='pcb_create'),
    path('pcb/<int:pcb_id>/verify/', views.pcb_qa_verify, name='pcb_qa_verify'),
    path('module/assemble/', views.module_assemble, name='module_assemble'),
    path('module/functional-test/', views.module_functional_test, name='module_functional_test'),
    path('module/sign-off/', views.module_sign_off, name='module_sign_off'),
    path('pcb/<int:pcb_id>/', views.pcb_detail, name='pcb_detail'),
    
    # Test configuration management URLs
    path('test-config/manage/', views.test_config_manage, name='test_config_manage'),
    path('test-config/create/', views.test_config_create, name='test_config_create'),
    path('test-config/<int:test_config_id>/edit/', views.test_config_edit, name='test_config_edit'),
    path('test-config/<int:test_config_id>/delete/', views.test_config_delete, name='test_config_delete'),
]