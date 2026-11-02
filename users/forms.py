from django import forms
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError

from core.validators import normalize_phone
from users.models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email")
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "surname": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get("password")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "autofocus": True}),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {"invalid_login": "Неверный email или пароль"}

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user = authenticate(
                self.request, email=email.strip().lower(), password=password
            )
            if self.user is None:
                raise ValidationError(self.error_messages["invalid_login"])
        return cleaned_data


class ProfileForm(forms.ModelForm):
    phone = forms.CharField(
        label="Телефон",
        required=False,
        max_length=20,
        help_text="Формат: +7XXXXXXXXXX или 8XXXXXXXXXX",
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "autocomplete": "tel",
                "placeholder": "+7XXXXXXXXXX",
                "aria-describedby": "phone-hint",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "email", "phone", "github_url")
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "surname": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "avatar": forms.FileInput(attrs={"accept": "image/*"}),
            "about": forms.Textarea(attrs={"rows": 4, "maxlength": 256}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "github_url": forms.URLInput(
                attrs={"autocomplete": "url", "placeholder": "https://github.com/username"}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        duplicates = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return None
        phone = normalize_phone(phone)
        duplicates = User.objects.filter(phone=phone).exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError("Этот номер телефона уже используется другим пользователем.")
        return phone
