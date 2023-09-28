from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import generic
# import speech_recognition as sr
# import pyttsx3
import wolframalpha
import wikipedia
# import webbrowser
# from django import JsonResponse,telegram
#from django.contrib.auth.models import User
# from django.shortcuts import render 
# from .models import User
import matplotlib.pyplot as plt
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, Http404
#from .models import Customer, Profile
from .forms import TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, ParentSignUpForm, QuestionForm, BaseAnswerInlineFormSet, LearnerInterestsForm, LearnerCourse, UserForm, ProfileForm, PostForm
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse,HttpResponseBadRequest
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.core import serializers
from django.conf import settings
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth
from datetime import datetime, date
from django.core.exceptions import ValidationError
from . import models
import operator
import itertools
from django.db.models import Avg, Count, Sum
from django.forms import inlineformset_factory
from .models import TakenQuiz, Profile, Quiz, Question, Answer, Learner, User, Course, Tutorial, Notes, Announcement , Parent,LearnerParentConnection
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm, PasswordChangeForm)
from django.utils.datastructures import MultiValueDictKeyError


from django.contrib.auth import update_session_auth_hash                                       


from bootstrap_modal_forms.generic import (
    BSModalLoginView,
    BSModalFormView,
    BSModalCreateView,
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView
)


# Shared Views

def home(request):
	return render(request, 'home.html')

def about(request):
	return render(request, 'about.html')

def services(request):
	return render(request, 'service.html')

def contact(request):
	return render(request, 'contact.html')

def login_form(request):
	return render(request, 'login.html')

def logoutView(request):
	logout(request)
	return redirect('home')


def loginView(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None and user.is_active:
			auth.login(request, user)
			if user.is_admin or user.is_superuser:
				return redirect('dashboard')
			elif user.is_instructor:
			    return redirect('instructor')
			elif user.is_learner:
			    return redirect('learner')
			elif user.is_parent:
			    return redirect('parent')
			else:
			    return redirect('login_form')
		else:
		    messages.info(request, "Invalid Username or Password")
		    return redirect('login_form')





# Admin Views
@login_required
def dashboard(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course_count = Course.objects.all().count()
    users = User.objects.all().count()
    # categories = ['Instructors','Learners']
    # counts = [learner,instructor]
    # counts = [learner,instructor]
    course_all= Course.objects.all()
    course_name_list=[]
    # learner_count_list=[]
    for course in course_all:
    #     learners=User.objects.filter(is_learner=True,learner_id=learner_id, course_id=course_id).count()
        course_name_list.append(course.name)
    #     learner_count_list.append(learners)
    data= Course.objects.annotate(learner_count=Count('interested_learners')).values('name','learner_count')
    chart_data=[
        {'course_id':item['name'],
        'learner_count':item['learner_count']}
        for item in data
    ]
    context = {'learner':learner, 'course_count':course_count, 'instructor':instructor, 'users':users, 'counts' : [learner,instructor], 'chart_data':chart_data,
    'course_name_list':course_name_list}

    return render(request, 'dashboard/admin/home.html', context)


class InstructorSignUpView(CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'dashboard/admin/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Instructor Was Added Successfully')
        return redirect('isign')


class AdminLearner(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'dashboard/admin/learner_signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Learner Was Added Successfully')
        return redirect('addlearner')


@login_required
def course(request):
	if request.method == 'POST':
		name = request.POST['name']
		color = request.POST['color']

		a = Course(name=name, color=color)
		a.save()
		messages.success(request, 'New Course Was Registed Successfully')
		return redirect('course')
	else:
	     return render(request, 'dashboard/admin/course.html')	



class AdminCreatePost(CreateView):
    model = Announcement
    form_class = PostForm
    template_name = 'dashboard/admin/post_form.html'
    success_url = reverse_lazy('alpost')


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class AdminListTise(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/admin/tise_list.html'


    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')


class ListAllTise(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/admin/list_tises.html'
    context_object_name = 'tises'
    paginated_by = 10


    def get_queryset(self):
        return Announcement.objects.order_by('-id')


class ListCourse(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'dashboard/admin/list_courses.html'
    context_object_name = 'courses'
    paginated_by = 10


    def get_queryset(self):
        return Course.objects.order_by('-id')


class ADeletePost(SuccessMessageMixin, DeleteView):
    model = Announcement
    template_name = 'dashboard/admin/confirm_delete.html'
    success_url = reverse_lazy('alistalltise')
    success_message = "Announcement Was Deleted Successfully"


class ListUserView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin/list_users.html'
    context_object_name = 'users'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')


class ListUserImmutableView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin/list_users_immutable.html'
    context_object_name = 'users'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')


class ListLearnerView(LoginRequiredMixin, ListView):
    model = Learner
    template_name = 'dashboard/admin/list_learners.html'
    context_object_name = 'learners'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')


class ListInstructorView(LoginRequiredMixin, ListView):
    model = Learner
    template_name = 'dashboard/admin/list_instructor.html'
    context_object_name = 'instructors'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')


class ADeleteuser(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard/admin/confirm_delete2.html'
    success_url = reverse_lazy('aluser')
    success_message = "User Was Deleted Successfully"

@login_required
def create_user_form(request):
    return render(request, 'dashboard/admin/add_user.html')


@login_required
def create_user(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password = make_password(password)

        a = User(first_name=first_name, last_name=last_name, username=username, password=password, email=email, is_admin=True)
        a.save()
        messages.success(request, 'Admin Was Created Successfully')
        return redirect('aluser')
    else:
        messages.error(request, 'Admin Was Not Created Successfully')
        return redirect('create_user_form')




def acreate_profile(request):
    if request.method == 'POST':
        try:
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            birth_date = request.POST['birth_date']
            bio = request.POST['bio']
            phonenumber = request.POST['phonenumber']
            city = request.POST['city']
            country = request.POST['country']
            avatar = request.FILES['avatar']
            # hobby = request.POST['hobby']
            current_user = request.user
            user_id = current_user.id
            print(user_id)

            Profile.objects.filter(id=user_id).create(user_id=user_id, phonenumber=phonenumber, first_name=first_name, last_name=last_name, bio=bio, birth_date=birth_date, avatar=avatar, city=city, country=country)
            messages.success(request, 'Your Profile Was Created Successfully')
            return redirect('auser_profile')
        except MultiValueDictKeyError:
            # Handle missing keys here, e.g., return a bad request response
            return HttpResponseBadRequest('Missing or incorrect form field(s).')
    else:
        current_user = request.user
        user_id = current_user.id
        users = Profile.objects.filter(user_id=user_id)
        users = {'users': users}
        return render(request, 'dashboard/admin/create_profile.html', users)     


@login_required
def auser_profile(request):
    current_user = request.user
    user_id = current_user.id
    users = Profile.objects.filter(user_id = user_id)
    users = {'users': users}
    return render(request, 'dashboard/admin/user_profile.html', users)     



# Instructor Views
@login_required
def home_instructor(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course_count = Course.objects.all().count()
    users = User.objects.all().count()
    course_all= Course.objects.all()
    course_name_list=[]
    # learner_count_list=[]
    for course in course_all:
    #     learners=User.objects.filter(is_learner=True,learner_id=learner_id, course_id=course_id).count()
        course_name_list.append(course.name)
    #     learner_count_list.append(learners)
    data= Course.objects.annotate(learner_count=Count('interested_learners')).values('name','learner_count')
    chart_data=[
        {'course_id':item['name'],
        'learner_count':item['learner_count']}
        for item in data
    ]
    context = {'learner':learner, 'course_count':course_count, 'instructor':instructor, 'users':users, 'counts' : [learner,instructor], 'chart_data':chart_data,
    'course_name_list':course_name_list}

    return render(request, 'dashboard/instructor/home.html', context)


class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name', 'course')
    template_name = 'dashboard/Instructor/quiz_add_form.html'


    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(self.request, 'Quiz created, Go A Head And Add Questions')
        return redirect('quiz_change', quiz.pk)

class ListCourseIns(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'dashboard/instructor/list_courses.html'
    context_object_name = 'courses'
    paginated_by = 10


    def get_queryset(self):
        return Course.objects.order_by('-id')

class ListInstructorForInsView(LoginRequiredMixin, ListView):
    model = Learner
    template_name = 'dashboard/instructor/list_instructor.html'
    context_object_name = 'instructors'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class ListLearnerForInsView(LoginRequiredMixin, ListView):
    model = Learner
    template_name = 'dashboard/instructor/list_learners.html'
    context_object_name = 'learners'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class ListUserImmutableInsView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/instructor/list_users_immutable.html'
    context_object_name = 'users'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class QuizUpateView(UpdateView):
    model = Quiz
    fields = ('name', 'course')
    template_name = 'dashboard/instructor/quiz_change_form.html'


    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk', self.object.pk})
        



@login_required
def question_add(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'dashboard/instructor/question_add_form.html', {'quiz': quiz, 'form': form})



@login_required
def question_change(request, quiz_pk, question_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)



    AnswerFormatSet = inlineformset_factory (
        Question,
        Answer,
        formset = BaseAnswerInlineFormSet,
        fields = ('text', 'is_correct'),
        min_num = 2,
        validate_min = True,
        max_num = 10,
        validate_max = True
        )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormatSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                formset.save()
                formset.save()
            messages.success(request, 'Question And Answers Saved Successfully')
            return redirect('quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormatSet(instance=question)
    return render(request, 'dashboard/instructor/question_change_form.html', {
        'quiz':quiz,
        'question':question,
        'form':form,
        'formset':formset
        })        




class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'dashboard/instructor/quiz_change_list.html'


    def get_queryset(self):
        queryset = self.request.user.quizzes \
        .select_related('course') \
        .annotate(questions_count = Count('questions', distinct=True)) \
        .annotate(taken_count = Count('taken_quizzes', distinct=True))
        return queryset    


class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'dashboard/instructor/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)


    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The Question Was Deleted Successfully')
        return super().delete(request, *args, **kwargs)


    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)


    def get_success_url(self):
        question = self.get_object()
        return reverse('quiz_change', kwargs={'pk': question.quiz_id})    



class QuizResultsView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_results.html'


    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes =quiz.taken_quizzes.select_related('learner__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
        'taken_quizzes': taken_quizzes,
        'total_taken_quizzes': total_taken_quizzes,
        'quiz_score':quiz_score
        }

        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)


    def get_queryset(self):
        return self.request.user.quizzes.all()    



class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_delete_confirm.html'
    success_url = reverse_lazy('quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()

@login_required
def question_add(request, pk):
    # By filtering the quiz by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # quiz will be able to add questions to it.
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'dashboard/instructor/question_add_form.html', {'quiz': quiz, 'form': form})


class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ('name', 'course', )
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_change_form.html'


    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk': self.object.pk})




class CreatePost(CreateView):
    form_class = PostForm
    model = Announcement
    template_name = 'dashboard/instructor/post_form.html'
    success_url = reverse_lazy('llchat')


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class TiseList(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/instructor/tise_list.html'

    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')

@login_required
def user_profile(request):
    current_user = request.user
    user_id = current_user.id
    print(user_id)
    users = Profile.objects.filter(user_id=user_id)
    users = {'users':users}
    return render(request, 'dashboard/instructor/user_profile.html', users)

@login_required
def create_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phonenumber = request.POST['phonenumber']
        bio = request.POST['bio']
        city = request.POST['city']
        country = request.POST['country']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id = user_id).create(user_id=user_id,first_name=first_name, last_name=last_name, phonenumber=phonenumber, bio=bio, city=city, country=country, birth_date=birth_date, avatar=avatar)
        messages.success(request, 'Profile was created successfully')
        return redirect('user_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users':users}
        return render(request, 'dashboard/instructor/create_profile.html', users)


@login_required
def tutorial(request):
    courses = Course.objects.only('id', 'name')
    context = {'courses':courses}

    return render(request, 'dashboard/instructor/tutorial.html', context)


@login_required
def publish_tutorial(request):
    if request.method == 'POST':
        title = request.POST['title']
        course_id = request.POST['course_id']
        content = request.POST['content']
        thumb = request.FILES['thumb']
        current_user = request.user
        author_id = current_user.id
        print(author_id)
        print(course_id)
        a = Tutorial(title=title, content=content, thumb=thumb, user_id=author_id, course_id=course_id)
        a.save()
        messages.success(request, 'Tutorial was published successfully!')
        return redirect('tutorial')
    else:
        messages.error(request, 'Tutorial was not published successfully!')
        return redirect('tutorial')


@login_required
def itutorial(request):
   tutorials = Tutorial.objects.all().order_by('-created_at')
   tutorials = {'tutorials':tutorials}
   return render(request, 'dashboard/instructor/list_tutorial.html', tutorials)


class ITutorialDetail(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/instructor/tutorial_detail.html'



class LNotesList(ListView):
    model = Notes
    template_name = 'dashboard/instructor/list_notes.html'
    context_object_name = 'notes'
    paginate_by = 4


    def get_queryset(self):
        return Notes.objects.order_by('-id')


def iadd_notes(request):
    courses = Course.objects.only('id', 'name')
    context = {'courses':courses}
    return render(request, 'dashboard/instructor/add_notes.html', context)


def publish_notes(request):
    if request.method == 'POST':
        title = request.POST['title']
        course_id = request.POST['course_id']
        cover = request.FILES['cover']
        file = request.FILES['file']
        current_user = request.user
        user_id = current_user.id

        a = Notes(title=title, cover=cover, file=file, user_id=user_id, course_id=course_id)
        a.save()
        messages.success = (request, 'Notes Was Published Successfully')
        return redirect('lnotes')
    else:
        messages.error = (request, 'Notes Was Not Published Successfully')
        return redirect('iadd_notes')


def update_file(request, pk):
    if request.method == 'POST':
        file = request.FILES['file']
        file_name = request.FILES['file'].name

        fs = FileSystemStorage()
        file = fs.save(file.name, file)
        fileurl = fs.url(file)
        file = file_name
        print(file)

        Notes.objects.filter(id = pk).update(file = file)
        messages.success = (request, 'Notes was updated successfully!')
        return redirect('lnotes')
    else:
        return render(request, 'dashboard/instructor/update.html')


# Learner Views
@login_required
def home_learner(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course_count = Course.objects.all().count()
    users = User.objects.all().count()
    course_all= Course.objects.all()
    course_name_list=[]
    # learner_count_list=[]
    for course in course_all:
    #     learners=User.objects.filter(is_learner=True,learner_id=learner_id, course_id=course_id).count()
        course_name_list.append(course.name)
    #     learner_count_list.append(learners)
    data= Course.objects.annotate(learner_count=Count('interested_learners')).values('name','learner_count')
    chart_data=[
        {'course_id':item['name'],
        'learner_count':item['learner_count']}
        for item in data
    ]
    context = {'learner':learner, 'course_count':course_count, 'instructor':instructor, 'users':users, 'counts' : [learner,instructor], 'chart_data':chart_data,
    'course_name_list':course_name_list}
    # context = {'learner':learner, 'course':course, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/learner/home.html', context)

class ListUserImmutableLerView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/learner/list_users_immutable.html'
    context_object_name = 'users'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class ListLearnerForLerView(LoginRequiredMixin, ListView):
    model = Learner
    template_name = 'dashboard/learner/list_learners.html'
    context_object_name = 'learners'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class ListInstructorForLerView(LoginRequiredMixin, ListView):
    model = Learner
    template_name = 'dashboard/learner/list_instructor.html'
    context_object_name = 'instructors'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class ListCourseLer(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'dashboard/learner/list_courses.html'
    context_object_name = 'courses'
    paginated_by = 10


    def get_queryset(self):
        return Course.objects.order_by('-id')

class LearnerSignUpView(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        #return redirect('learner')
        return redirect('home')


@login_required
def ltutorial(request):
   tutorials = Tutorial.objects.all().order_by('-created_at')
   tutorials = {'tutorials':tutorials}
   return render(request, 'dashboard/learner/list_tutorial.html', tutorials)


class LLNotesList(ListView):
    model = Notes
    template_name = 'dashboard/learner/list_notes.html'
    context_object_name = 'notes'
    paginate_by = 4


    def get_queryset(self):
        return Notes.objects.order_by('-id')

class CreatePostLearner(CreateView):
    form_class = PostForm
    model = Announcement
    template_name = 'dashboard/learner/post_form.html'
    success_url = reverse_lazy('ilchat')


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

        
class ITiseList(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/learner/tise_list.html'

    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')


@login_required
def luser_profile(request):
    current_user = request.user
    user_id = current_user.id
    print(user_id)
    users = Profile.objects.filter(user_id=user_id)
    users = {'users':users}
    return render(request, 'dashboard/learner/user_profile.html', users)



@login_required
def lcreate_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phonenumber = request.POST['phonenumber']
        bio = request.POST['bio']
        city = request.POST['city']
        country = request.POST['country']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id = user_id).create(user_id=user_id,first_name=first_name, last_name=last_name, phonenumber=phonenumber, bio=bio, city=city, country=country, birth_date=birth_date, avatar=avatar)
        messages.success(request, 'Profile was created successfully')
        return redirect('luser_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users':users}
        return render(request, 'dashboard/learner/create_profile.html', users)


class LTutorialDetail(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/learner/tutorial_detail.html'



class LearnerInterestsView(UpdateView):
    model = Learner
    form_class = LearnerInterestsForm
    template_name = 'dashboard/learner/interests_form.html'
    success_url = reverse_lazy('lquiz_list')

    def get_object(self):
        return self.request.user.learner

    def form_valid(self, form):
        messages.success(self.request, 'Course Was Updated Successfully')
        return super().form_valid(form)



class LQuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'dashboard/learner/quiz_list.html'

    def get_queryset(self):
        learner = self.request.user.learner
        learner_interests = learner.interests.values_list('pk', flat=True)
        taken_quizzes = learner.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(course__in=learner_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset        



class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'dashboard/learner/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.learner.taken_quizzes \
            .select_related('quiz', 'quiz__course') \
            .order_by('quiz__name')
        return queryset




def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    learner = request.user.learner

    if learner.quizzes.filter(pk=pk).exists():
        return render(request, 'dashboard/learner/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = learner.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                learner_answer = form.save(commit=False)
                learner_answer.student = learner
                learner_answer.save()
                if learner.get_unanswered_questions(quiz).exists():
                    return redirect('take_quiz', pk)
                else:
                    correct_answers = learner.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(learner=learner, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
                    return redirect('lquiz_list')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'dashboard/learner/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
    })        

@login_required
def bot_search(request):
    query = request.GET.get('query')
    if not query:
        return render(request,'dashboard/learner//chatbot.html',{'ans':""})

    try:
        client = wolframalpha.Client("KVAR8L-EAWK73U2AL")
        res = client.query(query)
        ans = next(res.results).text
        return render(request, 'dashboard/learner//chatbot.html', {'ans': ans, 'query': query})

    except Exception:
        try:
            ans = wikipedia.summary(query, sentences=10)
            return render(request, 'dashboard/learner/chatbot.html', {'ans': ans, 'query': query})


        except Exception:
            ans = "FOUND NOTHING"
            return render(request, 'dashboard/learner/chatbot.html', {'ans': ans, 'query': query})

# Parent Views
@login_required
def home_parent(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    parent = User.objects.filter(is_parent=True).count()
    course_count = Course.objects.all().count()
    users = User.objects.all().count()
    course_all= Course.objects.all()
    course_name_list=[]
    # learner_count_list=[]
    for course in course_all:
    #     learners=User.objects.filter(is_learner=True,learner_id=learner_id, course_id=course_id).count()
        course_name_list.append(course.name)
    #     learner_count_list.append(learners)
    data= Course.objects.annotate(learner_count=Count('interested_learners')).values('name','learner_count')
    chart_data=[
        {'course_id':item['name'],
        'learner_count':item['learner_count']}
        for item in data
    ]
    context = {'learner':learner, 'course_count':course_count, 'instructor':instructor, 'users':users, 'counts' : [learner,instructor], 'chart_data':chart_data,
    'course_name_list':course_name_list}

    return render(request, 'dashboard/parent/home.html', context)

@login_required
def parent_dashboard(request):
    # Assuming the parent is logged in
    parent = request.user  # You can adjust this based on your authentication system
    try:
        parent_profile = Parent.objects.get(user_id=parent.id)
        learner_linked = parent_profile.learner_linked
        # Retrieve courses linked with the learner using ManyToMany relationship
        learner_interests = learner_linked.interests.all()
    except Parent.DoesNotExist:
        # Handle the case where the parent profile doesn't exist
        learner_linked = None
        learner_interests = []

    context = {
        'learner_linked': learner_linked,
        'learner_interests': learner_interests,
    }

    return render(request, 'dashboard/parent/child_info.html', context)

# class ParentSignUpView(CreateView):
#     model = User
#     form_class = ParentSignUpForm
#     template_name = 'Parent_signup_form.html'

#     def get_context_data(self, **kwargs):
#         kwargs['user_type'] = 'parent'
#         return super().get_context_data(**kwargs)

#     def form_valid(self, form):
#         user = form.save(commit=False)
#         user.is_parent = True

#         learner_name = form.cleaned_data['learner_name']

#         try:
#             learner = Learner.objects.get(user__username=learner_name)
#         except Learner.DoesNotExist:
#             # Handle the case where the Learner with the given name does not exist
#             # You can raise an error or handle it as needed
#             return redirect('error_page')  # Modify this line as needed

#         user.save()  # Save the User object first

#         parent = Parent(user=user, is_parent=True, learner_linked=learner)
#         parent.save()
        
#         connection = LearnerParentConnection(parent=parent, learner=learner)
#         connection.save()

#         login(self.request, user)
#         return redirect('home')

#     # def get_form(self,form_class=None):
#     #     form = super().get_form(form_class)
#     #     # Customize the form to include the dropdown list for learners
#     #     form.fields['linked_learner'].queryset = Learner.objects.all()
#     #     form.fields['linked_learner'].empty_label = "Select your child"  # Add an empty label
#     #     form.fields['linked_learner'].label = "Select you child (ID - Name)"  # Customize the label
#     #     return form

class ParentSignUpView(CreateView):
    model = User
    form_class = ParentSignUpForm
    template_name = 'Parent_signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'parent'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_parent=True
        user.save()

        learner_id = form.cleaned_data['linked_learner']
        learner = Learner.objects.get(user_id=learner_id)
        parent = Parent(user=user,is_parent=True,learner_linked=learner)
        parent.save()
        connection = LearnerParentConnection(parent=parent, learner=learner)
        connection.save()


        login(self.request, user)
        #return redirect('learner')
        return redirect('home')

    def get_form(self,form_class=None):
        form = super().get_form(form_class)
        # Customize the form to include the dropdown list for learners
        form.fields['linked_learner'].queryset = Learner.objects.all()
        form.fields['linked_learner'].empty_label = "Select your child"  # Add an empty label
        form.fields['linked_learner'].label = "Select you child (ID - Name)"  # Customize the label
        return form


class ListUserImmutableParView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/parent/list_users_immutable.html'
    context_object_name = 'users'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class ListLearnerForParView(LoginRequiredMixin, ListView):
    model = Learner
    template_name = 'dashboard/parent/list_learners.html'
    context_object_name = 'learners'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class ListInstructorForParView(LoginRequiredMixin, ListView):
    model = Learner
    template_name = 'dashboard/parent/list_instructor.html'
    context_object_name = 'instructors'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class ListCoursePar(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'dashboard/parent/list_courses.html'
    context_object_name = 'courses'
    paginated_by = 10


    def get_queryset(self):
        return Course.objects.order_by('-id')

@login_required
def view_learner_profile(request,learner_id):
    parent_profile = get_object_or_404(Parent,user=request.user)
    connected_learner = get_object_or_404(parent_profile.connected_learner,pk=learner_id)

    return render(request, 'dashboard/parent/home.html',{
        'learner_linked':connected_learner })


@login_required
def luser_profile_parent(request):
    current_user = request.user
    user_id = current_user.id
    print(user_id)
    users = Profile.objects.filter(user_id=user_id)
    users = {'users':users}
    return render(request, 'dashboard/parent/user_profile.html', users)

@login_required
def lcreate_profile_parent(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phonenumber = request.POST['phonenumber']
        bio = request.POST['bio']
        city = request.POST['city']
        country = request.POST['country']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id = user_id).create(user_id=user_id,first_name=first_name, last_name=last_name, phonenumber=phonenumber, bio=bio, city=city, country=country, birth_date=birth_date, avatar=avatar)
        messages.success(request, 'Profile was created successfully')
        return redirect('luser_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users':users}
        return render(request, 'dashboard/parent/create_profile.html', users)


# For piecharts
@login_required
def dynamic_pieCharts(request):
    learner=Learner.objects.get(user=request.user)
    # all_quizzes = Quiz.objects.all()
    quiz_data=[]
    taken_quizzes=TakenQuiz.objects.filter(learner = learner)
    # questions= Question.objects.all()

    for taken_quiz in taken_quizzes:
        # num_questions = Question.objects.filter(quiz=quiz).count()
        quiz = taken_quiz.quiz
        # score = [taken.score for taken in taken_quizzes]
        score = taken_quiz.score
        num_questions = quiz.num_questions()
        # taken_quiz = TakenQuiz.objects.filter(learner=learner, quiz = quiz).first()

        # if taken_quiz:
        #     score = taken_quiz.score
        # else:
        #     score = 0

        quiz_data.append({
            'name': quiz.name,
            'score': score,
            'nums_questions' : num_questions
        })

        if not quiz_data:
            quiz_data.append({
            'name':'Not attended any quiz',
            'score':None,
            'num_questions': 0
            })
    # context={'quiz_data':quiz_data}
    # print(num_questions)
    return render(request,'dashboard/learner/dynamic_piecharts.html',{'quiz_data':quiz_data, 'learner':learner})

# Piecharts for Parent
@login_required
def dynamic_pieCharts_parent(request):
    learner=Learner.objects.get(user=request.user)
    quiz_data=[]
    quizzes=Quiz.objects.annotate(num_questions=Count('questions'))
    # questions= Question.objects.all()

    for quiz in quizzes:
        taken_quizzes = TakenQuiz.objects.filter(quiz=quiz)
        scores = [taken.score for taken in taken_quizzes]
        # num_questions = Question.objects.filter(quiz=quiz).count()
        num_questions = quiz.num_questions

        quiz_data.append({
            'name': quiz.name,
            'scores': scores,
            'nums_questions' : num_questions
        })
    # context={'quiz_data':quiz_data}
    # print(num_questions)
    return render(request,'dashboard/parent/piecharts.html',{'quiz_data':quiz_data, 'learner':learner})