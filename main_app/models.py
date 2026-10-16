from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.IntegerField(default=1000, verbose_name="Баланс ВПК")

    def __str__(self):
        return f"Профиль {self.user.username} (Баланс: {self.balance})"

# Автоматически создаем профиль студента при регистрации нового пользователя User
@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    instance.profile.save()
