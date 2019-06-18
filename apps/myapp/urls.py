from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('home/', views.home),
    path('signup/', views.signup),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('new_quiz/', views.new_quiz),
    path('quiz/<int:quiz_id>/<int:question_num>', views.question_view, name='question'),
    path('quiz/<int:quiz_id>/add_question/<int:question_num>', views.add_question, name='add_question'),
    path('results/<int:quiz_id>', views.result, name='results'),
    path('delete/<int:quiz_id>', views.delete, name='delete'),
    path('signout/', views.signout),
]