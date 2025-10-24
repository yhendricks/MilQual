from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Batch, PCB, TestMeasurement, FileAttachment, Module, ModuleTestRecord, UserGroupExtension


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'production_date', 'description']
    list_filter = ['production_date']
    search_fields = ['batch_number', 'description']


@admin.register(PCB)
class PCBAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'batch', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'batch']
    search_fields = ['serial_number', 'batch__batch_number']


@admin.register(TestMeasurement)
class TestMeasurementAdmin(admin.ModelAdmin):
    list_display = ['pcb', 'voltage', 'current', 'test_date', 'tester']
    list_filter = ['test_date', 'tester']
    search_fields = ['pcb__serial_number']


@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_type', 'pcb', 'uploaded_by', 'upload_date']
    list_filter = ['file_type', 'upload_date', 'uploaded_by']
    search_fields = ['pcb__serial_number', 'description']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['module_serial_number', 'assembler', 'assembly_date', 'status']
    list_filter = ['status', 'assembly_date', 'assembler']
    search_fields = ['module_serial_number']


@admin.register(ModuleTestRecord)
class ModuleTestRecordAdmin(admin.ModelAdmin):
    list_display = ['module', 'test_type', 'result', 'tester', 'test_date']
    list_filter = ['test_type', 'result', 'test_date', 'tester']
    search_fields = ['module__module_serial_number']


@admin.register(UserGroupExtension)
class UserGroupExtensionAdmin(admin.ModelAdmin):
    list_display = ['group', 'level', 'department']
    list_filter = ['level', 'department']
    search_fields = ['group__name', 'department']


# Register Group model to customize it
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_level', 'get_department']
    
    def get_level(self, obj):
        try:
            return obj.usergroupextension.level
        except UserGroupExtension.DoesNotExist:
            return "N/A"
    
    def get_department(self, obj):
        try:
            return obj.usergroupextension.department
        except UserGroupExtension.DoesNotExist:
            return "N/A"
    
    get_level.short_description = 'Level'
    get_department.short_description = 'Department'


# Unregister the default Group admin and register the new one
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)