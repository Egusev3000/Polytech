from django import forms
from .models import MayoRegistration

class MayoForm(forms.ModelForm):
    class Meta:
        model = MayoRegistration
        fields = ['student_name', 'group_number', 'wishes']
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Введите ваше великое имя'}),
            'group_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например, 231-321'}),
            'wishes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Какого майонеза вы ждете больше всего?'}),
        }
