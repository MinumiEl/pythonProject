from django.urls import path
from .views import PostList, PostsDetail, PostCreate, PostUpdate, PostDelete,  Responses, Respond, \
   response_accept, response_delete, PostItem

urlpatterns = [
   path('', PostList.as_view()),
   path('post/', PostList.as_view(), name='post_list'),
   path('article/<int:pk>/', PostsDetail.as_view(), name='post_detail'),
   path('post/<int:pk>', PostItem.as_view(), name='post_detail'),
   path('create/', PostCreate.as_view(), name='post_create'),
   path('<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
   path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   path('responses', Responses.as_view(), name='responses'),
   path('responses/<int:pk>', Responses.as_view(), name='responses'),
   path('respond/<int:pk>', Respond.as_view(), name='respond'),
   path('response/accept/<int:pk>', response_accept),
   path('response/delete/<int:pk>', response_delete),

]
