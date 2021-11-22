import operator

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.contrib.auth import get_user_model
from utils import upload_function
from django.utils.safestring import mark_safe
from django.urls import reverse


class Musician(models.Model):
    """Имя музыканта"""

    name = models.CharField(max_length=255, verbose_name='Имя музыканта')
    slug = models.SlugField()
    image = models.ImageField(upload_to=upload_function, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Музыкант'
        verbose_name_plural = "Музыканты"


class MediaType(models.Model):
    """Наиминования носителя"""

    name = models.CharField(max_length=100, verbose_name='Название медианосителя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Медианоситель'
        verbose_name_plural = 'Медианосители'


class Genre(models.Model):
    """Жанр"""
    name = models.CharField(max_length=50, verbose_name='Название жанра')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Artist(models.Model):
    """Имя исполнителя"""

    name = models.CharField(max_length=255, verbose_name='Исполнитель/группа')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    musician = models.ManyToManyField(Musician, verbose_name='Участник', related_name='artist')
    slug = models.SlugField()
    image = models.ImageField(upload_to=upload_function, null=True, blank=True)

    def __str__(self):
        return f"{self.name} | {self.genre.name}"

    def get_absolute_url(self):
        return reverse('artist_detail', kwargs={'artist_slug': self.slug})

    class Meta:
        verbose_name = 'Исполнитель/группа'
        verbose_name_plural = 'Исполнители/группы'


class Album(models.Model):
    """Название альбома"""

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name='Исполнитель')
    name = models.CharField(max_length=255, verbose_name='Название альбома')
    media_type = models.ForeignKey(MediaType, verbose_name='Носитель', on_delete=models.CASCADE)
    trek_list = models.TextField(verbose_name='Треклист')
    release_date = models.DateField(verbose_name="Дата релиза")
    description = models.TextField(verbose_name='Описание', default='Описание появиться позже')
    slug = models.SlugField()
    stock = models.IntegerField(verbose_name='Наличие на складе')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    offer_of_the_week = models.BooleanField(default=False, verbose_name='Предложение недели')
    image = models.ImageField(upload_to=upload_function)

    def __str__(self):
        return f"{self.id} | {self.artist.name} | {self.name}"

    @property
    def ct_model(self):
        return self._meta.model_name

    def get_absolute_url(self):
        return reverse('album_detail', kwargs={'artist_slug': self.artist.slug, 'album_slug': self.slug})

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'


class CartProduct(models.Model):
    """Продукт карзины"""

    MODEL_CARTPRODUCT_DISPLAY_NAME_MAP = {
        'Album': {'is_constructable': True, 'fields': ['name', 'artist.name'], 'separator': ' - '}
    }

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return f"Продукт: {self.content_object.name} (для корзины)"

    @property
    def display_name(self):
        model_fields = self.MODEL_CARTPRODUCT_DISPLAY_NAME_MAP.get(
            self.content_object.__class__._meta.model_name.capitalizer())
        if model_fields and model_fields['is_constructable']:
            display_name = model_fields['separator'].join(
                [operator.attrgetter(field)(self.content_object) for field in model_fields['fields']]
            )
            return display_name
        if model_fields and not model_fields['is_constructable']:
            display_name = operator.attrgetter(model_fields['field'])(self.content_object)
            return display_name

        return self.content_object

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'


class Cart(models.Model):
    """Корзина"""

    owner = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    product = models.ManyToManyField(CartProduct, verbose_name="Продукт для корзины",
                                     related_name='related_cart')
    total_product = models.IntegerField(default=0, verbose_name='Общее кол-во товара')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена', null=True, blank=True)
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = "Корзины"


class Order(models.Model):
    """Заказ"""

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOISES = {
        (STATUS_NEW, "Новый заказ"),
        (STATUS_IN_PROGRESS, "Заказ в обработке"),
        (STATUS_READY, "Заказ готов"),
        (STATUS_COMPLETED, 'Заказ получен покупателем'),
    }
    BUYING_TYPE_CHOISES = {
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка'),
    }

    customer = models.ForeignKey('Customer', verbose_name="Покупатель", related_name='orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = PhoneNumberField(verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE)
    address = models.CharField(max_length=1024, verbose_name='Адресс', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOISES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип заказа', null=True, blank=True)
    created_at = models.DateField(verbose_name="Дата создания заказа", auto_created=True)
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Customer(models.Model):
    '''Покупатель'''

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    customer_order = models.ManyToManyField(Order, related_name='related_customer')
    wishlist = models.ManyToManyField(Album, blank=True, verbose_name='Список ожидаемого')
    phone = PhoneNumberField(verbose_name='Телефон')
    address = models.TextField(null=True, blank=True, verbose_name='Адресс')

    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Notification(models.Model):
    """Уведомления"""

    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Получатель')
    text = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Уведомление для {self.recipient.user.username} | id={self.id}"

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class ImageGallery(models.Model):
    """Галерея"""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to=upload_function)
    user_in_slider = models.BooleanField(default=False)

    def __str__(self):
        return f"Изображения для {self.content_object}"

    def image_url(self):
        return mark_safe(f'<img src="{self.image.url}" width = "auto", height="280px"')

    class Meta:
        verbose_name = "Галерея изображений"
        verbose_name_plural = "Галерея изображений"
