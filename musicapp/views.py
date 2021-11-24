from django.shortcuts import render
from django import views
from .models import Artist, Album, Customer, CartProduct
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from .forms import RegistrationForm, LoginForm
from .mixins import *
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from utils import recalc_cart


class BaseView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        albums = Album.objects.all().order_by('-id')[:5]
        context = {
            'albums': albums,
            'cart': self.cart
        }
        return render(request, 'base.html', context)


class ArtistDetailView(views.generic.DetailView):
    model = Artist
    template_name = 'artist/artist_detail.html'
    slug_url_kwarg = 'artist_slug'
    context_object_name = 'artist'


class AlbumDetailView(views.generic.DetailView):
    model = Album
    template_name = 'album/album_detail.html'
    slug_url_kwarg = 'album_slug'
    context_object_name = 'album'


class LoginView(views.View):
    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'login.html', context)


class RegistrationView(views.View):
    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        context = {
            'form': form
        }
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
            )
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')

        context = {
            'form': form
        }
        return render(request, 'registration.html', context)


class AccountView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        context = {
            'customer': customer,
            'cart': self.cart
        }
        return render(request, 'account.html', context)


class CartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        context = {
            'cart': self.cart
        }
        return render(request, 'cart.html', context)


class AddToCartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        if created:
            self.cart.product.add(cart_product)
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Товар успешно добавлен')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class DeleteFromCartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )

        self.cart.product.remove(cart_product)
        cart_product.delite()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Товар успешно удалён из корзины')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class ChangeQTYView(CartMixin, views.View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model', kwargs.get('slug'))
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Количество успешно изменено')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class AddToWishList(views.View):
    @staticmethod
    def get(request, *args, **kwargs):
        album = Album.objects.get(id=kwargs['album_id'])
        customer = Customer.objects.get(user=request.user)
        customer.wishlist.add(album)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
