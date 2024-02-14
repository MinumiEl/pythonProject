from django.contrib import admin
from .models import Post, Category,  MyModel, Comment, Author


admin.site.register(Post)
admin.site.register(Category)
admin.site.register(MyModel)
admin.site.register(Comment)


