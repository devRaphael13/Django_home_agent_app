import json

import cloudinary
import cloudinary.api
import cloudinary.uploader
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from django.contrib import admin

from .forms import (
    AdminHouseCreationForm,
    AdminUserChangeForm,
    AdminUserCreationForm
    )
from .models import House, Image, User

config = cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)


class HouseModelAdmin(admin.ModelAdmin):
    add_form_template = "admin/add_house.html"
    change_form_template = "admin/update_house.html"

    def get_form(self, request, obj=None, **kwargs):
        try:
            instance = kwargs["instance"]
            return AdminHouseCreationForm(instance=instance)

        except KeyError:
            return AdminHouseCreationForm

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["form"] = self.get_form(request)
        return super().add_view(
            request, form_url=form_url, extra_context=extra_context
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        house = House.objects.get(id=object_id)
        extra_context["form"] = self.get_form(instance=house, request=request)
        extra_context["images"] = house.image_set.all()
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )

    def save_model(self, request, obj, form, change):
        obj.save()
        images = request.FILES.getlist("images")
        with ThreadPoolExecutor() as executor:
            executor.map(self.upload, images)
            
        return super().form_valid(form)

    def upload(self, image):
        data = cloudinary.uploader.upload(image)
        Image.objects.create(house=self.object, url=data["secure_url"], name=data["public_id"])

class UserModelAdmin(admin.ModelAdmin):
    model = User
    add_form_template = "admin/add_user.html"
    change_form_template = "admin/update_user.html"
    list_display = ("email", "is_active", "is_staff")
    list_filter = ("email", "is_active", "is_staff")

    search_fields = ("email",)
    ordering = ("email",)

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            return AdminUserChangeForm
        return AdminUserCreationForm

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["form"] = self.get_form(request)
        return super().add_view(
            request, form_url=form_url, extra_context=extra_context
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        user = User.objects.get(id=object_id)
        extra_context["form"] = self.get_form(request, obj=True)(instance=user)
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )

    def delete_pic(self, obj):
        photo_name = obj.photo_name
        if photo_name:
            cloudinary.uploader.destroy(photo_name)

    def upload_pic(self, photo):
        data = cloudinary.uploader.upload(photo)
        return data

    def save_model(self, request, obj, form, change):
        photo = request.FILES.get("photo")
        if photo:

            with ThreadPoolExecutor() as executor:
                executor.submit(self.delete_pic, obj)
                data = executor.submit(self.upload_pic, photo)

            data = data.result()
    
            obj.photo_url=data["secure_url"]
            obj.photo_name=data["public_id"]
        obj.save()

admin.site.register(House, HouseModelAdmin)
admin.site.register(User, UserModelAdmin)
admin.site.site_header = "Home"
