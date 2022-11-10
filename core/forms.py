import datetime
import re
from cities_light.models import City
from django import forms
from django.contrib.auth import get_user_model, authenticate, password_validation
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm,
    AuthenticationForm,
)
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from .models import House, Image

User = get_user_model()


def year_choices():
    year_choices = [("older", "older"), ("1800s", "1800s"), ("1900s", "1900s")]
    year_choices.extend(
        [(str(x), str(x)) for x in range(2000, datetime.date.today().year + 1)]
    )
    return year_choices


class LoginForm(AuthenticationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "class": "text-slate-900 text-sm rounded-md w-full p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
            }
        )
    )

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "text-slate-900 text-sm rounded-md w-full p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
            }
        ),
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "w-4 h-4 border-2 border-indigo-600 rounded",
            }
        ),
    )
    username = None

    error_messages = {
        "invalid_login": _(
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        forms.Form.__init__(self, *args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login"
        )


class AdminUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": " text-slate-900 text-sm rounded-md w-full p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
            }
        ),
        help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": " text-slate-900 text-sm rounded-md w-full p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
            }
        ),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
                    attrs={
                        "class": "text-slate-900 text-sm rounded-md w-full p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
                        }
                    ),
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$", 
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits is allowed.",
                )
            ]
        )
    
    photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "photo",
            "password1",
            "password2",
            "twitter",
            "instagram",
            "facebook",
            "is_staff",
            "is_active",
        ]

        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": " text-slate-900 text-sm rounded-md w-full  p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": " text-slate-900 text-sm rounded-md w-full  p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": " text-slate-900 text-sm rounded-md w-full  p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
                }
            ),
            "twitter": forms.TextInput(
                attrs={
                    "class": " text-slate-900 text-sm rounded-md w-full  p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
                }
            ),
            "instagram": forms.TextInput(
                attrs={
                    "class": " text-slate-900 text-sm rounded-md w-full  p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
                }
            ),
            "facebook": forms.TextInput(
                attrs={
                    "class": " text-slate-900 text-sm rounded-md w-full  p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
                }
            ),
            "is_staff": forms.CheckboxInput(
                attrs={
                    "class": "rounded-full px-1 mb-2 form-check-input appearance-none h-4 w-4 border border-gray-300 bg-white checked:bg-indigo-500 checked:border-indigo-500 transition duration-200 mt-1 align-top bg-no-repeat bg-center bg-contain cursor-pointer"
                }),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "rounded-full px-1 mb-2 form-check-input appearance-none h-4 w-4 border border-gray-300 bg-white checked:bg-indigo-500 checked:border-indigo-500 transition duration-200 mt-1 align-top bg-no-repeat bg-center bg-contain cursor-pointer"
                })
        }


class CustomUserCreationForm(AdminUserCreationForm):

    class Meta:
        model = User
        fields = AdminUserCreationForm.Meta.fields
        fields.remove("is_staff")
        fields.remove("is_active")

        widgets = AdminUserCreationForm.Meta.widgets
        widgets.pop("is_staff")
        widgets.pop("is_active")


class AdminUserChangeForm(UserChangeForm):

    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
                    attrs={
                        "class": "text-slate-900 text-sm rounded-md w-full p-2 outline-none focus:border-2 focus:border-indigo-600 placeholer-opacity-0.5 placeholder:italic placeholder:text-sm placeholder:opacity-70",
                        }
                    ),
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$", 
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits is allowed.",
                )
            ]
        )

    photo = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "photo",
            "twitter",
            "instagram",
            "facebook",
            "is_staff",
            "is_active",
            "password"
        )

        widgets = AdminUserCreationForm.Meta.widgets


class CustomUserChangeForm(AdminUserChangeForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "twitter",
            "instagram",
            "facebook",
        )
        widgets = CustomUserCreationForm.Meta.widgets
        widgets.pop("email")
        

class HouseFilterForm(forms.ModelForm):
    class Meta:

        model = House
        fields = (
            "city",
            "region",
            "rooms",
            "forsale",
            "price",
            "garages",
            "sitting_rooms",
            "dining_rooms",
            "kitchen",
            "bathrooms",
        )

        widgets = {
            "city": forms.Select(attrs={"class": "text-sm sm:text-base px-2 w-full h-8 outline-none focus:border-2 focus:border-indigo-600 rounded-md mt-1 "}),
            "region": forms.Select(attrs={"class": "text-sm sm:text-base px-2 w-full h-8 outline-none focus:border-2 focus:border-indigo-600 rounded-md mt-1 "}),
            "rooms": forms.NumberInput(attrs={"class": "text-sm sm:text-base px-2 w-full h-8 outline-none focus:border-2 focus:border-indigo-600 rounded-md mt-1 "}),
            "garages": forms.NumberInput(
                attrs={"class": "text-sm sm:text-base px-2 w-full outline-none focus:border-2 focus:border-indigo-600 h-8 rounded-md mt-1 "}
            ),
            "sitting_rooms": forms.NumberInput(
                attrs={"class": "text-sm sm:text-base px-2 w-full outline-none focus:border-2 focus:border-indigo-600 h-8 rounded-md mt-1 "}
            ),
            "dining_rooms": forms.NumberInput(
                attrs={"class": "text-sm sm:text-base px-2 w-full outline-none focus:border-2 focus:border-indigo-600 h-8 rounded-md mt-1 "}
            ),
            "bathrooms": forms.NumberInput(
                attrs={"class": "text-sm sm:text-base px-2 w-full outline-none focus:border-2 focus:border-indigo-600 h-8 rounded-md mt-1 "}
            ),
            "kitchen": forms.NumberInput(
                attrs={"class": "text-sm sm:text-base px-2 w-full outline-none focus:border-2 focus:border-indigo-600 h-8 rounded-md mt-1 "}
            ),
            "forsale": forms.CheckboxInput(
                attrs={
                    "class": "rounded-full  px-1 mb-2 appearance-none h-4 w-4 border-2 border-slate-400 bg-slate-900 checked:bg-indigo-600 checked:border-indigo-600 transition duration-200 mt-1 align-top bg-no-repeat bg-center bg-contain cursor-pointer"
                }
            ),
            "price": forms.NumberInput(attrs={"class": "text-sm sm:text-base px-2 w-full h-8 outline-none focus:border-2 focus:border-indigo-600 rounded-md mt-1 "}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, field in self.fields.items():
            self.fields[key].required = False

        self.fields["city"].queryset = City.objects.none()


class HouseCreationForm(forms.ModelForm):

    year_built = forms.TypedChoiceField(
        choices=year_choices,
        initial=str(datetime.date.today().year),
        widget=forms.Select(
            attrs={
                "class": "text-sm sm:text-base px-2 w-full h-8 rounded-md outline-none focus:border-2 focus:border-indigo-600 mt-1",
                "type": "month",
                "placeholder": "Select a Year",
            }
        ),
    )

    class Meta:
        model = House
        exclude = ("agent",)

        widgets = HouseFilterForm.Meta.widgets
        widgets.update(
            {
                "description": forms.Textarea(
                    attrs={"class": "text-sm leading-tight sm:text-base p-2 outline-none focus:border-2 focus:border-indigo-600 w-full rounded-md mt-1 h-32 "}
                ),
                "address": forms.Textarea(
                    attrs={"class": "text-sm leading-tight sm:text-base p-2 outline-none focus:border-2 focus:border-indigo-600 w-full rounded-md mt-1 h-12"}
                ),
            }
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["city"].queryset = City.objects.none()

        if "region" in self.data:
            region_id = int(self.data.get("region"))
            self.fields["city"].queryset = City.objects.filter(region_id=region_id)

        elif self.instance.pk:
            self.fields["city"].queryset = self.instance.region.city_set.all()


class AdminHouseCreationForm(HouseCreationForm):
    class Meta:
        model = House
        fields = "__all__"

        widgets = HouseCreationForm.Meta.widgets
        widgets.update(
            {"agent": forms.Select(attrs={"class": "text-sm sm:text-base px-2 h-8 outline-none focus:border-2 focus:border-indigo-600 w-full rounded-md mt-1 "})}
        )


class HouseUpdateForm(forms.ModelForm):
    class Meta:
        model = House
        fields = (
            "address",
            "description",
            "price",
            "forsale",
            "rooms",
            "garages",
            "sitting_rooms",
            "dining_rooms",
            "bathrooms",
            "kitchen",
        )
        widgets = HouseCreationForm.Meta.widgets
        widgets.pop("region")
        widgets.pop("city")
