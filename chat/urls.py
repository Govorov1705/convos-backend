from django.urls import path

from . import views


urlpatterns = [
    path('', views.ChatListCreateAPIView.as_view()),
    path('with-recent-messages/', views.ChatWithRecentMessageListAPIView.as_view()),
    path('<int:id>/', views.ChatRetrieveUpdateDestroyAPIView.as_view()),
    path('<int:id>/with-messages/', views.ChatWithMessagesRetriveAPIView.as_view()),
    path('<int:id>/clear/', views.ClearChatAPIView.as_view()),
]