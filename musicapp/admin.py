from django.contrib import admin
from .models import *
from django.contrib.contenttypes.admin import GenericTabularInline


class MembersInLine(admin.TabularInline):
    model = Artist.musician.through


class ImageGalleryInLine(GenericTabularInline):
    model = ImageGallery
    readonly_fields = ('image_url',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    inlines = [ImageGalleryInLine]

    list_display = ('artist', 'name', 'release_date', 'price',)
    list_filter = ('artist',)

    search_fields = ['artist.genre.name', 'artist', 'media_type.name']
    sortable_by = 'price'

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    inlines = [MembersInLine, ImageGalleryInLine]
    exclude = ('musician',)

    # search_fields = ('','')


admin.site.register(Musician)
admin.site.register(MediaType)
admin.site.register(Genre)
# admin.site.register(Artist)
# admin.site.register(Album)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(Notification)
admin.site.register(ImageGallery)
