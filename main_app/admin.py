from django.contrib import admin

from .models import StudentProfile, AIChat, AIMessage

admin.site.register(StudentProfile)
admin.site.register(AIChat)
admin.site.register(AIMessage)
