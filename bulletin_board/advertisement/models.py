from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.core.cache import cache
from django.utils.translation import gettext as _
from django.utils.translation import pgettext_lazy
from crum import get_current_user
from django_ckeditor_5.fields import CKEditor5Field


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)


    def update_rating(self):
        postRat = self.post_set.aggregate(postRating=Sum('rating'))
        pRat = 0
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set.aggregate(commentRating=Sum('rating'))
        cRat = 0
        cRat += commentRat.get('commentRating')

        self.ratingAuthor = pRat * 3 + cRat
        self.save()


class Category(models.Model):
    TYPE = (
        ('tank', 'Танки'),
        ('heal', 'Хилы'),
        ('dd', 'ДД'),
        ('buyers', 'Торговцы'),
        ('gildemaster', 'Гилдмастеры'),
        ('quest', 'Квестгиверы'),
        ('smith', 'Кузнецы'),
        ('tanner', 'Кожевники'),
        ('potion', 'Зельевары'),
        ('spellmaster', 'Мастера заклинаний'),
    )
    name = models.CharField(max_length=64, choices=TYPE, unique=True, help_text=_('category name'))
    # subscribers = models.ManyToManyField(User, through='Subscription')

    def __str__(self):
        return self.name


class MyModel(models.Model):
    name = models.CharField(max_length=100)
    kind = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='kinds',
        verbose_name=pgettext_lazy('help text for MyModel model', 'This is the help text'),
    )


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news',)
    categoryType = models.ForeignKey(Category, on_delete=models.CASCADE)
    dateCreation = models.DateField(auto_now_add=True)
    title = RichTextField(max_length=128)
    text = CKEditor5Field(blank=True, null=True, verbose_name="содержание")
    cover = models.ImageField(upload_to='images/', null=True)

    def __str__(self):
        return self.title

    def preview(self):
        return self.text[0:123] + '...'

    def __str__(self):
        return f'{self.title.title()[:20]}: {self.text[:20]}'

    def __str__(self):
        dataf = 'Post from {}'.format(self.dateCreation.strftime('%d.%m.%Y %H:%M'))
        return f"{dataf},{self.author},{self.title}"

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateField(auto_now_add=True)


class PostComment (models.Model):
    title = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.ForeignKey(Comment, on_delete=models.CASCADE)


class Response(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст')
    status = models.BooleanField(default=False)
    dateCreation = models.DateTimeField(auto_now_add=True)

# class Subscription(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subscriptions')
#     title = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='subscriptions', default=1)
