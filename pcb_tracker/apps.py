from django.apps import AppConfig


class PcbTrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pcb_tracker'
    
    def ready(self):
        import pcb_tracker.signals  # Import signals if we have any
        from . import signals  # Import the signals module