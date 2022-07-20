

from django.urls import path
from .views import *

urlpatterns = [
    path("", staticManagerView.as_view(), name="staticManager"),
    path("<slug:Slug>", staticManagerView.as_view(), name="staticManager-search"),
    path("fetchCategory/", categoryView.as_view(), name="fetch-category"),
]
