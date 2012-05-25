from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    evernote_token = models.CharField(blank=True, max_length=256)
    evernote_token_expires_time = models.DateTimeField(null=True, blank=True)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
      UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
