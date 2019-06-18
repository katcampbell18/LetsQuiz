from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (logout,login, authenticate)
from django.utils import timezone
from .models import *
from .forms import *
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.
score = 0

def index(request):
    return render(request,'myapp/index.html')

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        username = request.POST['username']
        r_password = request.POST['password1']
        user = authenticate(request, username = username, password = r_password)
        if user:
            login(request, user)
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            messages.warning(request, 'Incorrect Login Details')
            return render(request, 'myapp/home.html',{})
    else:
        return render(request, 'myapp/home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            if not (User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists()):
                User.objects.create_user(username, first_name, last_name, email, password1)
            user = form.save()
            login(request, user)
            raise forms.ValidationError('A username with that email or password already exists')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'myapp/register.html', {'form': form})

def dashboard(request):
    all_quizzes = Quiz.objects.all().order_by('-created_at')
    if request.user.is_authenticated:
        taken_quizzes = request.user.score_set.all().order_by('-taken_on')
        my_quizzes = request.user.quiz_set.all()
    else:
        taken_quizzes = {}
        my_quizzes = {}
    return render(request, 'myapp/dashboard.html', {'all_quizzes' : all_quizzes, 'taken_quizzes':taken_quizzes, 'my_quizzes' : my_quizzes})

@login_required(login_url='/')
def new_quiz(request):
    if request.method == "POST":
        date_created = timezone.now()
        author = request.user
        quiz_name = request.POST['title']
        if quiz_name == '':
            return render(request, 'new_quiz', {'error_message' : "Quiz name can't be blank"})
        quiz = Quiz.objects.create(created_at=date_created, author=author, title=quiz_name)
        quiz.save()
        return redirect('add_question', quiz_id=quiz.id, question_num=1)
    else:
        return render(request, 'myapp/add_quiz.html', {})

def add_question(request, quiz_id, question_num):
    error_message=""
    if request.method == "POST":
        if request.POST['question_text']=='':
            context = {'title': Quiz.objects.get(id=quiz_id).title, 'quest_no' : question_num, 'error_message' : "Question text can't be blank"}
            return render(request, 'myapp/add_question.html', context)
        elif request.POST['choice1'] == '' or request.POST['choice2']=='' or request.POST['choice3']=='' or request.POST['choice4']=='':
            context = {'title': Quiz.objects.get(id=quiz_id).title, 'ques_no' : question_num, 'error_message' : "Please fill all the choices"}
            return render(request, 'myapp/add_question.html', context)
        else:
            quiz = get_object_or_404(Quiz, id=quiz_id)
            question_text = request.POST['question_text']
            q = Question.objects.create(quiz=quiz, question_text=question_text, question_num=question_num)
            choice1 = Choice(question = q, choice_text = request.POST['choice1'])
            choice2 = Choice(question = q, choice_text = request.POST['choice2'])
            choice3 = Choice(question = q, choice_text = request.POST['choice3'])
            choice4 = Choice(question = q, choice_text = request.POST['choice4'])
            try:
                r_choice = request.POST['choice']
                if r_choice == 'choice1':
                    choice1.right_choice = True
                elif r_choice == 'choice2':
                    choice2.right_choice = True
                elif r_choice == 'choice3':
                    choice3.right_choice = True
                elif r_choice == 'choice4':
                    choice4.right_choice = True
            except MultiValueDictKeyError:
                q.delete()
                error_message = "Please mark the correct answer"
                context =  {'quiz_name': Quiz.objects.get(id=quiz_id).title, 'ques_no' : question_num, "error_message" : error_message}
                return render(request, 'myapp/add_question.html', context)

            quiz.num_of_quest = question_num
            quiz.save()
            choice1.save()
            choice2.save()
            choice3.save()
            choice4.save()

            #button dependant behaviour
            if '_save&add' in request.POST:
                return redirect('add_question', quiz_id=quiz_id, question_num=question_num+1)
            else:
                return redirect('dashboard')
    else:
        context =  {'quiz_name': Quiz.objects.get(id=quiz_id).title, 'ques_no' : question_num}
        return render(request, 'myapp/add_question.html', context)

@login_required(login_url='/')
def question_view(request, quiz_id, question_num):
    global score
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if question_num == len(quiz.question_set.all())+1:
        quiz.taken_by += 1
        if score > quiz.highest_score:
            quiz.highest_score = score
        quiz.save()
        sc = str(score)
        s = Score.objects.create(score=score, user=request.user, quiz=quiz, taken_on=timezone.now())
        s.save()
        score = 0
        return render(request, 'myapp/score.html', {"score" : sc})
    ques = quiz.question_set.all()[question_num-1]
    done_p = int(100*question_num/len(quiz.question_set.all()))
    if request.method == "POST":
        if '_skip' in request.POST:
            return redirect('question', quiz_id=quiz_id, question_num=question_num+1)
        else:
            try:
                selected_choice = Choice.objects.get(id = request.POST["choices"])
                if selected_choice.right_choice == True:
                    score += 1
            except MultiValueDictKeyError:
                context = {'quiz' : quiz, 'ques' : ques, 'done_p' : done_p}
                messages.warning(request, "Please select a choice")
                return render(request, 'myapp/question_view.html', context)
            return redirect('question', quiz_id=quiz_id, question_num=question_num+1)
    context = {'quiz' : quiz, 'ques' : ques, 'done_p' : done_p}
    return render(request, 'myapp/question_view.html', context)

def result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.author != request.user:
        messages.warning(request, "You can't view the results. Only author can do that")
        return redirect('dashboard')
    else:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        scores = quiz.score_set.all().order_by('score')
        return render(request, 'myapp/results.html', {'quiz':quiz, 'scores': scores})

def delete(request, quiz_id):
    q = Quiz.objects.get(id=quiz_id)
    if q.author == request.user:
        q.delete()
        messages.success(request, "Quiz deleted")
    else:
        messages.warning(request, "Can't delete the quiz. Rights reserved with the author")
    return redirect('dashboard')

def signout(request):
    logout(request)
    return redirect('/home')



