from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import profile, IncubatorDetailView, IdeaListView, IdeaCreateView, \
    IdeaUpdateView, IdeaDeleteView, IdeaLikeToggle, HomeView, UserIdeaView, ApproveIdeaView,AllIdeasView, IdeaCategory, \
    CategoryListView, SearchView, IncubatorListView,DeclineIdeaView,CommitteeHome,Idea_detail, ForumListView, PostForum,\
    Forum_detail, AllForumsListView, PostInterest, InterestView, InterestListView, forbidden_view, LandingView

app_name = 'strathideasapp'
urlpatterns = [
    # path('', HomeView.as_view(), name='home'),
    path('forbidden', forbidden_view.as_view(), name='forbidden'),
    path('', LandingView.as_view(), name='home'),
    path('profile/', profile, name='profile'),
    path('idea/<int:pk>/forum', ForumListView.as_view(), name='forum'),
    path('idea/<int:pk>/forum/new', PostForum.as_view(template_name='strathideasapp/new_forum_form.html'), name='forum_create'),
    path('idea/<forum>/forum/detail', Forum_detail, name='forum_detail'),
    path('forums', AllForumsListView.as_view(), name='forum_list'),
    path('idea', IdeaListView.as_view(), name='idea_list'),
    path('categories', CategoryListView.as_view(), name='category_list'),
    path('search', SearchView.as_view(), name='Search'),
    path('idea/cat/<int:pk>/', IdeaCategory.as_view(), name='idea_category'),
    path('myideas', UserIdeaView.as_view(), name='myidea_view'),
    path('idea/<idea>/', Idea_detail, name='idea_detail'),
    path('idea/<idea>/like', IdeaLikeToggle.as_view(), name='idea_like'),
    path('idea/new', IdeaCreateView.as_view(template_name='strathideasapp/new_idea_creation.html'), name='idea_create'),
    path('idea/<int:pk>/update/', IdeaUpdateView.as_view(success_url='/'), name='idea_update'),
    path('idea/<int:pk>/delete/', IdeaDeleteView.as_view(success_url='/'), name='idea_delete'),
    # one must be an incubator
    path('incubator', IncubatorListView.as_view(), name='incubator_list'),
    path('incubator/<pk>/', IncubatorDetailView.as_view(), name='incubator_detail'),
    path('idea/<int:pk>/interest', InterestView.as_view(), name='interest'),
    path('idea/<int:pk>/interested', InterestListView.as_view(), name='interested'),
    path('idea/<int:pk>/interest/new', PostInterest.as_view(template_name='strathideasapp/new_interest_form.html'),
         name='interest_create'),
    # one must be a committee member
    path('committeehome', AllIdeasView.as_view(), name='allideas'),
    path('display', CommitteeHome.as_view(), name='comm_home'),
    path('approve/<int:idea>/', ApproveIdeaView.as_view(), name='approve'),
    path('decline/<int:idea>/', DeclineIdeaView.as_view(), name='decline'),

]
