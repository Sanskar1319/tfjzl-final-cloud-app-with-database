from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'onlinecourse'
urlpatterns = [
    # Course list and details views
    path(route='', view=views.CourseListView.as_view(), name='popular_course_list'),
    path('course/<int:pk>/', views.CourseDetailsView.as_view(), name='course_details'),

    # Authentication routes
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),

    # Course enrollment route
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),

    # <HINT> Create a route for submit view
    path('<int:course_id>/submit/', views.submit, name='submit'),
    path('course/<int:course_id>/submit/', views.submit, name='submit_course'),

    # <HINT> Create a route for show_exam_result view
    path('course/<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result, name='show_exam_result'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
