from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.models import User

from users.models import Profile

# @receiver(post_save, sender=Profile)
def createUser(sender, instance, created, **kwargs):

    if created:
        user = instance
        profile = Profile.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            name=user.first_name,
        )

        subject = 'Welcome to DevSearch'
        message = "We're glad u are here!"

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[profile.email],
            fail_silently=False
        )


def updateUser(sender, instance, created, **kwargs):

    profile = instance
    user = profile.user
    if created == False:
        user.first_name = profile.name
        user.username = profile.username
        user.email = profile.email
        user.save()


def deleteUser(sender, instance, **kwargs):

    user = instance.user
    user.delete()


post_save.connect(createUser, sender=User)
post_save.connect(updateUser, sender=Profile)
post_delete.connect(deleteUser, sender=Profile)
