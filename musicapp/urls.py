from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('delete-from-cart/<str:ct_model>/<str:slug>', DeleteFromCartView.as_view(), name="delete_from_cart"),
    path('change-qty/<str:ct_model>/<str:slug>/', ChangeQTYView.as_view(), name="change_qty"),
    path('', BaseView.as_view(), name='base'),
    path('login/', LoginView.as_view(), name='login'),
    path(r'activate/<uid64>/<token>/', activate_account, name='activate'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('account/', AccountView.as_view(), name='account'),
    path('add-to-wishlist/<int:album_id>/', AddToWishList.as_view(), name='add_to_wishlist'),

    path('<str:artist_slug>/', ArtistDetailView.as_view(), name='artist_detail'),
    path('<str:artist_slug>/<str:album_slug>', AlbumDetailView.as_view(), name='album_detail'),
]
