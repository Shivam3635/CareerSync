from django.urls import path
from .views import JobListPublicView, JobMatchesView, JobCategoriesView

urlpatterns = [
    path('', JobListPublicView.as_view(), name='job_list_public'),
    path('matches/', JobMatchesView.as_view(), name='job_matches'),
    path('categories/', JobCategoriesView.as_view(), name='job_categories'),
]
