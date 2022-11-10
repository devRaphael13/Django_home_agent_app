import json

import cloudinary
import cloudinary.api
import cloudinary.uploader

from cities_light.models import City, Region
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, resolve_url, reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
    FormView,
)

from core.forms import (
    HouseCreationForm,
    HouseFilterForm,
    LoginForm,
    CustomUserChangeForm,
    CustomUserCreationForm,
    HouseUpdateForm,
)
from core.models import House, Image

config = cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)


User = get_user_model()



class LandingPageView(TemplateView):
    template_name = "core/landing.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        agents = User.objects.all()[:4]
        houses = House.objects.all()[:4]
        context.update({"agents": agents, "houses": houses})
        return context


class ContactPageView(TemplateView):
    template_name = "core/contact.html"


class HouseIndexView(View):
    template_name = "core/house-index.html"

    def get(self, request, *args, **kwargs):
        queryset = House.objects.all()
        form = HouseFilterForm()

        region = request.GET.get("region")
        city = request.GET.get("city")
        price = request.GET.get("price")
        rooms = request.GET.get("rooms")
        garages = request.GET.get("garages")
        sitting_rooms = request.GET.get("sitting_rooms")
        dining_rooms = request.GET.get("dining_rooms")
        kitchen = request.GET.get("kitchen")
        forsale = request.GET.get("forsale")
        bathrooms = request.GET.get("bathrooms")
        search = request.GET.get("search")

        if bathrooms:
            queryset = queryset.filter(bathrooms__gte=bathrooms)

        if region:
            queryset = queryset.filter(region__id=region)

        if city:
            queryset = queryset.filter(city__id=city)

        if garages:
            queryset = queryset.filter(garages__gte=garages)

        if sitting_rooms:
            queryset = queryset.filter(sitting_rooms__gte=sitting_rooms)

        if dining_rooms:
            queryset = queryset.filter(dining_rooms__gte=dining_rooms)

        if kitchen:
            queryset = queryset.filter(kitchen__gte=kitchen)

        if price:
            queryset = queryset.filter(price__lte=price)

        if forsale:
            queryset = queryset.filter(forsale=True)

        if rooms:
            queryset = queryset.filter(rooms__gte=rooms)

        if search:
            queryset = queryset.filter(
                Q(address__icontains=search)
                | Q(description__icontains=search)
                | Q(city__name__icontains=search)
                | Q(region__name__icontains=search)
            ).distinct()

        context = {"queryset": queryset, "states": Region.objects.all(), "form": form}

        return render(request, self.template_name, context)


class HouseDetailView(DetailView):
    model = House
    template_name = "core/house-detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        house = self.get_object()
        images = house.image_set.all()
        context.update({"images": images, "user": self.request.user})
        return context


class AgentIndexView(ListView):
    model = User
    template_name = "core/agent-list.html"


class AgentDetailView(DetailView):
    model = User
    template_name = "core/agent-detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(
            {
                "houses": House.objects.filter(agent=self.get_object()),
                "user": self.request.user,
            }
        )

        return context


class AgentSignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "core/signup.html"

    def form_valid(self, form):
        form.save(commit=False)
        photo = self.request.FILES.get("photo")
        if photo:
            data = cloudinary.uploader.upload(photo)
            form.instance.photo_url=data["secure_url"]
            form.instance.photo_name=data["public_id"]
        return super().form_valid(form)
    
    
        

class AgentLoginView(LoginView):
    template_name = "core/login.html"
    authentication_form = LoginForm

    def get_success_url(self):
        if not self.next_page:
            if self.request.user.is_superuser or self.request.user.is_staff:
                return reverse("admin:index")
            return reverse("agent-detail", args=(self.request.user.id,))
        return resolve_url(self.next_page)

    def form_valid(self, form):
        remember_me = form.cleaned_data["remember_me"]
        if remember_me:
            self.request.session.set_expiry(1209600)
        return super().form_valid(form)


class AgentLogoutView(LoginRequiredMixin, LogoutView):
    template_name = "core/logout.html"


class AgentEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = "core/agent-update.html"

    def form_valid(self, form):
        form.save(commit=False)
        photo = self.request.FILES.get("photo")
        if photo:
            xphoto_name = form.instance.photo_name
            if xphoto_name:
                cloudinary.uploader.destroy(xphoto_name)
            data = cloudinary.uploader.upload(photo)
            form.instance.photo_url=data["secure_url"]
            form.instance.photo_name=data["public_id"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("agent-detail", args=(self.get_object().id,))
    

class HouseCreateView(LoginRequiredMixin, CreateView):

    template_name = "core/house-add.html"
    model = House
    form_class = HouseCreationForm

    def form_valid(self, form):
        form.save(commit=False)
        form.instance.agent = self.request.user
        self.object = form.save()
        images = self.request.FILES.getlist("images")
        for image in images:
            data = cloudinary.uploader.upload(image)
            Image.objects.create(house=self.object, url=data["secure_url"], name=data["public_id"])
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({"title": "Add Property"})
        return context

    def get_success_url(self):
        return reverse("property-detail", args=(self.get_object().id,))


class HouseUpdateView(LoginRequiredMixin, UpdateView):
    model = House
    form_class = HouseUpdateForm
    template_name = "core/house-update.html"

    def get_queryset(self):
        return House.objects.filter(agent=self.request.user)

    def form_valid(self, form):
        form.save(commit=False)
        self.object = form.save()
        images = self.request.FILES.getlist("images")
        for image in images:
            data = cloudinary.uploader.upload(image)
            Image.objects.create(house=self.object, url=data["secure_url"], name=data["public_id"])
        return super().form_valid(form)
 
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            "images": Image.objects.filter(house_id=self.get_object().id),
            })
        return context

    def get_success_url(self):
        return reverse("property-detail", args=(self.get_object().id,))


class ImageIndexView(ListView):
    template_name = "core/house-images.html"

    def get_queryset(self):
        return Image.objects.filter(house_id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            "house_id": self.kwargs['pk']
        })
        return context
    
def delete_images(request):
    data = json.loads(request.body)

    try:
        image = Image.objects.get(id=data["image_id"])

    except Image.DoesNotExist:
        return JsonResponse({"delete": False}, safe=False)

    if request.user == image.house.agent or request.user.is_staff:
        cloudinary.uploader.destroy(image.name)
        image.delete()
        return JsonResponse({"delete": True, "id": data["image_id"]}, safe=False)
    return JsonResponse({"delete": False}, safe=False)


def cities(request):
    data = json.loads(request.body)
    queryset = City.objects.filter(region__id=data["state_id"])
    return JsonResponse(list(queryset.values("id", "name")), safe=False)

def delete_acct(request):
    pass

def delete_photo(request):
    data = json.loads(request.body)
    
    try:
        agent = User.objects.get(id=data["agent_id"])

    except User.DoesNotExist:
        return JsonResponse({"delete": False}, safe=False)
    
    if request.user == agent or request.user.is_staff:
        cloudinary.uploader.destroy(agent.photo_name)
        agent.photo_name = None
        agent.photo_url = None 
        agent.save()
        return JsonResponse({"delete": True}, safe=False)
    return JsonResponse({"delete": False}, safe=False)


def delete_house(request):
    data = json.loads(request.body)

    try:
        house = House.objects.get(id=data["house_id"])

    except House.DoesNotExist:
        return JsonResponse({"delete": False}, safe=False)

    if request.user == house.agent or request.user.is_staff:

        images = Image.objects.filter(house_id=data["house_id"])

        if images.count() > 1:
            cloudinary.api.delete_resources(list(images.values_list("name", flat=True)))
        
        else:
            cloudinary.uploader.destroy(images.first().name)

        house.delete()
        return JsonResponse({"delete": True}, safe=False)
    return JsonResponse({"delete": False}, safe=False)

        