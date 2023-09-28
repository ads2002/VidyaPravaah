from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
# from chatbot.views import telegram_webhook



urlpatterns = [

# Shared URLs
path('', views.home, name='home'),
path('about/', views.about, name='about'),
path('services/', views.services, name='services'),
path('contact/', views.contact, name='contact'),
path('lsign/', views.LearnerSignUpView.as_view(), name='lsign'),
path('psign/', views.ParentSignUpView.as_view(), name='psign'),
path('login_form/', views.login_form, name='login_form'),
path('login/', views.loginView, name='login'),
path('logout/', views.logoutView, name='logout'),

# telegram chatbot
# path('telegram_webhook/', telegram_webhook, name='telegram_webhook'), 

# Admin URLs
path('dashboard/', views.dashboard, name='dashboard'),
path('course/', views.course, name='course'),
path('isign/', views.InstructorSignUpView.as_view(), name='isign'),
path('addlearner/', views.AdminLearner.as_view(), name='addlearner'),
path('apost/', views.AdminCreatePost.as_view(), name='apost'),
path('alpost/', views.AdminListTise.as_view(), name='alpost'),
path('alistalltise/', views.ListAllTise.as_view(), name='alistalltise'),
path('adpost/<int:pk>', views.ADeletePost.as_view(), name='adpost'),
path('aluser/', views.ListUserView.as_view(), name='aluser'),
path('aluserim/', views.ListUserImmutableView.as_view(), name='aluserim'),
path('aluserimins/', views.ListUserImmutableInsView.as_view(), name='aluserimins'),
path('aluserimler/', views.ListUserImmutableLerView.as_view(), name='aluserimler'),
path('allearner/', views.ListLearnerView.as_view(), name='allearner'),
path('allearnerins/', views.ListLearnerForInsView.as_view(), name='allearnerins'),
path('allearnerler/', views.ListLearnerForLerView.as_view(), name='allearnerler'),
path('alins/', views.ListInstructorView.as_view(), name='alins'),
path('alinsins/', views.ListInstructorForInsView.as_view(), name='alinsins'),
path('alinsler/', views.ListInstructorForLerView.as_view(), name='alinsler'),
path('aduser/<int:pk>', views.ADeleteuser.as_view(), name='aduser'),
path('create_user_form/', views.create_user_form, name='create_user_form'),
path('create_user/', views.create_user, name='create_user'),
path('acreate_profile/', views.acreate_profile, name='acreate_profile'),
path('auser_profile/', views.auser_profile, name='auser_profile'),
path('list_course/', views.ListCourse.as_view(), name='list_course'),
path('list_courseins/', views.ListCourseIns.as_view(), name='list_courseins'),
path('list_courseler/', views.ListCourseLer.as_view(), name='list_courseler'),



# Instructor URLs
path('instructor/', views.home_instructor, name='instructor'),
path('quiz_add/', views.QuizCreateView.as_view(), name='quiz_add'),
path('question_add/<int:pk>', views.question_add, name='question_add'),
path('quiz/<int:quiz_pk>/<int:question_pk>/', views.question_change, name='question_change'),
path('llist_quiz/', views.QuizListView.as_view(), name='quiz_change_list'),
path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
path('quiz/<int:pk>/results/', views.QuizResultsView.as_view(), name='quiz_results'),
path('quiz/<int:pk>/delete/', views.QuizDeleteView.as_view(), name='quiz_delete'),
path('quizupdate/<int:pk>/', views.QuizUpdateView.as_view(), name='quiz_change'),
path('ipost/', views.CreatePost.as_view(), name='ipost'),
path('llchat/', views.TiseList.as_view(), name='llchat'),
path('user_profile/', views.user_profile, name='user_profile'),
path('create_profile/', views.create_profile, name='create_profile'),
path('tutorial/', views.tutorial, name='tutorial'),
path('post/',views.publish_tutorial,name='publish_tutorial'),
path('itutorial/',views.itutorial,name='itutorial'),
path('itutorials/<int:pk>/', views.ITutorialDetail.as_view(), name = "itutorial-detail"),
path('listnotes/', views.LNotesList.as_view(), name='lnotes'),
path('iadd_notes/', views.iadd_notes, name='iadd_notes'),
path('publish_notes/', views.publish_notes, name='publish_notes'),
path('update_file/<int:pk>', views.update_file, name='update_file'),




# Learner URl's
path('learner/',views.home_learner,name='learner'),
path('ltutorial/',views.ltutorial,name='ltutorial'),
path('llistnotes/', views.LLNotesList.as_view(), name='llnotes'),
path('ilchat/', views.ITiseList.as_view(), name='ilchat'),
path('ilpost/', views.CreatePostLearner.as_view(), name='ilpost'),
path('luser_profile/', views.luser_profile, name='luser_profile'),
path('lcreate_profile/', views.lcreate_profile, name='lcreate_profile'),
path('tutorials/<int:pk>/', views.LTutorialDetail.as_view(), name = "tutorial-detail"),
path('interests/', views.LearnerInterestsView.as_view(), name='interests'),
path('learner_quiz/', views.LQuizListView.as_view(), name='lquiz_list'),
path('taken/', views.TakenQuizListView.as_view(), name='taken_quiz_list'),
path('quiz/<int:pk>/', views.take_quiz, name='take_quiz'),
path('bot_search/', views.bot_search, name='bot_search'),
path('piecharts/', views.dynamic_pieCharts, name='piecharts'),



# Parent URl's
path('parent/',views.home_parent,name='parent'),
path('parentchild/',views.parent_dashboard,name='parentchild'),
path('luserp/',views.ListUserImmutableParView.as_view(),name='luserp'),
path('llerp/',views.ListLearnerForParView.as_view(),name='llerp'),
path('linstp/',views.ListInstructorForParView.as_view(),name='linstp'),
path('lcoursep/',views.ListCoursePar.as_view(),name='lcoursep'),
path('view_learner_profile/<int:learner_id>/',views.view_learner_profile,name='view_learner_profile'),
path('parent_piecharts/',views.dynamic_pieCharts_parent,name='parent_piecharts'),
path('puser_profile/',views.luser_profile_parent,name='puser_profile'),
path('pcreate_profile/',views.lcreate_profile_parent,name='pcreate_profile'),





































 
]
