from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    """
    Whenever a new User is saved for the first time, automatically
    create a matching Profile. This means every user has a Profile
    from the moment they register — no more edge cases where a user
    exists without one (e.g. commenting before ever visiting their
    own profile page).
    """
    if created:
        Profile.objects.get_or_create(user=instance)