from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


class PCBType(models.Model):
    """
    Model to represent different types of PCBs
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Batch(models.Model):
    """
    Model to represent a batch of PCBs
    """
    batch_number = models.CharField(max_length=100, unique=True)
    pcb_type = models.ForeignKey(PCBType, on_delete=models.CASCADE, related_name='batches', null=True, blank=True)
    production_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        if self.pcb_type:
            return f"Batch {self.batch_number} ({self.pcb_type.name})"
        return f"Batch {self.batch_number}"
    
    class Meta:
        ordering = ['-production_date']


class PCB(models.Model):
    """
    Model to represent an individual PCB with its test status and workflow state
    """
    # Status choices for the PCB
    STATUS_CHOICES = [
        ('pending', 'Pending Testing'),
        ('tested', 'Tested by Board Tester'),
        ('qa_verified', 'Verified by QA'),
        ('assembled', 'Assembled into Module'),
        ('functional_tested', 'Functional Tested'),
        ('environmental_tested', 'Environmental Tested'),
        ('final_functional_tested', 'Final Functional Tested'),
        ('completed', 'Completed'),
    ]
    
    serial_number = models.CharField(max_length=100, unique=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='pcbs')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"PCB {self.serial_number} - Batch {self.batch.batch_number}"
    
    class Meta:
        ordering = ['-created_at']


class TestMeasurement(models.Model):
    """
    Model to store test measurements for a PCB
    """
    pcb = models.ForeignKey(PCB, on_delete=models.CASCADE, related_name='measurements')
    voltage = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    current = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    other_measurements = models.JSONField(default=dict, blank=True)  # For additional measurements
    tester = models.ForeignKey(User, on_delete=models.CASCADE)
    test_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Measurements for {self.pcb.serial_number} - {self.test_date}"
    

class FileAttachment(models.Model):
    """
    Model to store file attachments (like .xlsx files) for PCBs and modules
    """
    FILE_TYPE_CHOICES = [
        ('pcb_test', 'PCB Test Report'),
        ('functional_test', 'Functional Test Report'),
        ('environmental_test', 'Environmental Test Report'),
        ('other', 'Other'),
    ]
    
    pcb = models.ForeignKey(PCB, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    file = models.FileField(upload_to='attachments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        pcb_info = f"for {self.pcb.serial_number}" if self.pcb else ""
        return f"{self.file_type} {pcb_info} - {self.upload_date}"


class Module(models.Model):
    """
    Model to represent a module assembled from multiple PCBs
    """
    # Status choices for the module
    STATUS_CHOICES = [
        ('assembled', 'Assembled'),
        ('functional_tested', 'Functional Tested'),
        ('environmental_tested', 'Environmental Tested'),
        ('final_functioned_tested', 'Final Functional Tested'),
        ('completed', 'Completed'),
    ]
    
    module_serial_number = models.CharField(max_length=100, unique=True)
    pcbs = models.ManyToManyField(PCB, related_name='modules')
    assembler = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assembled_modules')
    assembly_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='assembled')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Module {self.module_serial_number}"
    
    class Meta:
        ordering = ['-assembly_date']


class ModuleTestRecord(models.Model):
    """
    Model to store test records for modules
    """
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='test_records')
    TEST_TYPE_CHOICES = [
        ('functional', 'Functional Test'),
        ('environmental', 'Environmental Test'),
        ('final_functional', 'Final Functional Test'),
    ]
    
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES)
    result = models.CharField(max_length=10, choices=[('pass', 'Pass'), ('fail', 'Fail')])
    tester = models.ForeignKey(User, on_delete=models.CASCADE)
    test_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.test_type} for Module {self.module.module_serial_number} - {self.result}"


class UserGroupExtension(models.Model):
    """
    Extension to add additional information to user groups
    """
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    level = models.IntegerField(help_text="Level of the group (e.g., 1 for lvl1, 2 for lvl2)")
    department = models.CharField(max_length=50, help_text="Department the group belongs to")
    
    def __str__(self):
        return f"{self.group.name} Extension"