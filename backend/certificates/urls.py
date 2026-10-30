from django.urls import path

from . import views

app_name = 'certificates'

urlpatterns = [
    path('me/certificates/', views.my_certificates, name='my-certificates'),
    path(
        'courses/<slug:slug>/certificate/eligibility/',
        views.course_eligibility,
        name='course-eligibility',
    ),
    path(
        'courses/<slug:slug>/certificate/issue/',
        views.issue_certificate,
        name='course-issue-certificate',
    ),
    path(
        'certificates/verify/<str:public_id>/',
        views.verify_certificate,
        name='verify',
    ),
    path(
        'certificates/verify/<str:public_id>/image.png',
        views.public_certificate_image,
        name='verify-image',
    ),
    path(
        'certificates/<str:public_id>/download/',
        views.download_certificate,
        name='download',
    ),
]
