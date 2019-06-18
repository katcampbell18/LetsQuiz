from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_of_quest = models.IntegerField(default=0)
    taken_by = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    users= models.ManyToManyField(User, related_name='quizzes', through='Score')
    author = models.ForeignKey(User, on_delete=models.CASCADE)

def __str__(self):
    return self.title

class Question(models.Model):
    question_text = models.TextField(max_length=255)
    question_num = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self):
        return self.question_text

class Score(models.Model):
    score = models.IntegerField()
    taken_on = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Choice(models.Model):
    choice_text = models.CharField(max_length=100)
    right_choice = models.BooleanField(default=False)
    question  = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.choice_text
