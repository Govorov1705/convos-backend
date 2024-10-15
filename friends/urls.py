from django.urls import path

from . import views

urlpatterns = [
    path('add-friend-search/', views.AddFriendSearchListAPIView.as_view()),

    path('<int:id>/', views.FriendRemoveAPIView.as_view()),

    path('friend_lists/my/', views.FriendListRetrieveAPIView.as_view()),

    path('friend_requests/', views.FriendRequestCreateAPIView.as_view()),
    path('friend_requests/sent/', views.SentFriendRequestListAPIView.as_view()),
    path('friend_requests/received/', views.ReceivedFriendRequestListAPIView.as_view()),
    path('friend_requests/<int:id>/', views.FriendRequestRetrieveAPIView.as_view()),
    path('friend_requests/<int:id>/accept/', views.AcceptFriendRequestAPIView.as_view()),
    path('friend_requests/<int:id>/decline/', views.DeclineFriendRequestAPIView.as_view()),
    path('friend_requests/<int:id>/cancel/', views.CancelFriendRequestAPIView.as_view()),
]