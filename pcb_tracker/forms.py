from django import forms
from .models import Batch, PCB, TestMeasurement, FileAttachment, Module, ModuleTestRecord


class PCBTestForm(forms.Form):
    pcb_serial = forms.CharField(max_length=100, label='PCB Serial Number')
    voltage = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    current = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    temperature = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    other_measurements = forms.JSONField(required=False, 
                                         widget=forms.Textarea(attrs={'rows': 3}),
                                         label='Other Measurements (JSON format)')
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_pcb_serial(self):
        serial = self.cleaned_data['pcb_serial']
        try:
            pcb = PCB.objects.get(serial_number=serial)
            # Ensure the PCB is in a state that allows testing
            if pcb.status != 'pending':
                if pcb.status == 'tested':
                    raise forms.ValidationError('This PCB has already been tested.')
                else:
                    raise forms.ValidationError('This PCB is not ready for testing.')
            return pcb
        except PCB.DoesNotExist:
            raise forms.ValidationError('PCB with this serial number does not exist.')
    
    def clean(self):
        cleaned_data = super().clean()
        pcb = cleaned_data.get('pcb_serial')
        
        if pcb:
            cleaned_data['pcb'] = pcb
        
        return cleaned_data


class FileAttachmentForm(forms.ModelForm):
    class Meta:
        model = FileAttachment
        fields = ['file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class ModuleAssemblyForm(forms.Form):
    module_serial_number = forms.CharField(max_length=100, label='Module Serial Number')
    pcb_serials = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), 
                                  label='PCB Serial Numbers (one per line)')
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    def clean_pcb_serials(self):
        serials_text = self.cleaned_data['pcb_serials']
        serials = [s.strip() for s in serials_text.split('\n') if s.strip()]
        
        # Validate that all PCBs exist and are in the correct status
        pcbs = []
        for serial in serials:
            try:
                pcb = PCB.objects.get(serial_number=serial)
                # Only allow PCBs that have been QA verified
                if pcb.status != 'qa_verified':
                    raise forms.ValidationError(f'PCB {serial} is not ready for assembly. Status: {pcb.status}')
                pcbs.append(pcb)
            except PCB.DoesNotExist:
                raise forms.ValidationError(f'PCB with serial number {serial} does not exist.')
        
        return pcbs
    
    def clean(self):
        cleaned_data = super().clean()
        pcbs = cleaned_data.get('pcb_serials')
        
        if pcbs:
            cleaned_data['pcbs'] = pcbs
        
        return cleaned_data
    
    def save(self):
        module_serial = self.cleaned_data['module_serial_number']
        pcbs = self.cleaned_data['pcbs']
        notes = self.cleaned_data['notes']
        
        # Create the module
        module = Module.objects.create(
            module_serial_number=module_serial,
            assembler=None,  # Will be set by the view
            notes=notes
        )
        
        # Add PCBs to the module
        for pcb in pcbs:
            module.pcbs.add(pcb)
        
        return module


class ModuleTestForm(forms.ModelForm):
    class Meta:
        model = ModuleTestRecord
        fields = ['module', 'result', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show modules that are in the correct state for this test
        self.fields['module'].queryset = Module.objects.filter(status='assembled')


class PCBCreateForm(forms.ModelForm):
    class Meta:
        model = PCB
        fields = ['serial_number', 'batch', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show batches that exist
        self.fields['batch'].queryset = Batch.objects.all()