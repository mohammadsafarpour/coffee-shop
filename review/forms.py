from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(),
        error_messages={
            'min_value': 'امتیاز باید بین ۱ تا ۵ باشد.',
            'max_value': 'امتیاز باید بین ۱ تا ۵ باشد.',
            'required': 'لطفاً امتیاز را ثبت کنید.',
        },
    )

    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'نظر خود را اینجا بنویسید...',
            }),
        }
        error_messages = {
            'text': {'required': 'متن نظر الزامی است.'},
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if len(text) < 5:
            raise forms.ValidationError('متن نظر باید حداقل 5 کاراکتر باشد.')
        return text
