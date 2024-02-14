from django import forms
from .models import Post, Response
from django.core.exceptions import ValidationError


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'categoryType',
            'text',


        ]

        def __init__(self, *args, **kwargs):

            super().__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control', 'autocomplete': 'off'})

            self.fields['title'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
            self.fields['text'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
            self.fields['title'].required = False
            self.fields['text'].required = False

        def clean(self):
            cleaned_data = super().clean()
            name = cleaned_data.get("title")
            description = cleaned_data.get("text")

            if name == description:
                raise ValidationError(
                    "Описание не должно быть идентично названию."
                )

            return cleaned_data


class RespondForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(RespondForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = "Текст отклика:"


class ResponsesFilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(ResponsesFilterForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.ModelChoiceField(
            label='Объявление',
            queryset=Post.objects.filter(author_id=user.id).order_by('-dateCreation').values_list('title', flat=True),
            empty_label="Все",
            required=False
        )
