from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction


@receiver(post_delete, sender=User)
def ensure_superuser_exists(sender, instance, **kwargs):
    """
    When a user is deleted, if this leaves only one user in the system,
    make that user a superuser to ensure there's always an admin.
    """
    # Count remaining users
    remaining_users_count = User.objects.count()
    
    # If there's only one user left, make sure they're a superuser
    if remaining_users_count == 1:
        remaining_user = User.objects.first()
        if remaining_user and not remaining_user.is_superuser:
            remaining_user.is_superuser = True
            remaining_user.is_staff = True
            # Use update to avoid triggering signals again
            User.objects.filter(id=remaining_user.id).update(
                is_superuser=True,
                is_staff=True
            )