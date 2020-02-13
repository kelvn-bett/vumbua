from django.contrib.auth import login
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)
from django.views.decorators.csrf import csrf_exempt

from strathideasapp.tokens import account_activation_token
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm, CommentsForm, \
    IdeaCreationForm, ForumForm, ForumCommentsForm, InterestForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, RedirectView, TemplateView, FormView, \
    CreateView
from django.shortcuts import get_object_or_404
from .models import Ideas, Comments, Industry_category, PostView, Profile, Roles, Forum, ForumComments, ForumView, \
    Interest
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from strathideasapp.mixins import CommitteeRequiredMixin, IncubatorRequiredMixin, NormalRequiredMixin
from django.http import JsonResponse

# Create your views here.

# Third Party views The -> APIView is a wrapper that allows one to create an API view that accepts certain request
# methods such as get and post.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import IdeaSerializer


class TrialView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        ideas = Ideas.objects.all()
        serializer = IdeaSerializer(ideas, many=True)
        # post = ideas.first()
        # serializer = IdeaSerializer(post)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = IdeaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


def home(request):
    context = {
        'ideas': Ideas.objects.all()
    }
    return render(request, "strathideasapp/new_idea_list.html", context)

class forbidden_view(TemplateView):
    template_name = 'strathideasapp/forbidden.html'


class HomeView(TemplateView):
    template_name = 'strathideasapp/index.html'

class LandingView(ListView):
    model = Ideas
    template_name = 'strathideasapp/home.html'
    context_object_name = 'ideas'


class UserIdeaView(LoginRequiredMixin, ListView):
    model = Ideas
    template_name = 'strathideasapp/ideas_page.html'
    context_object_name = 'ideas'


class IdeaListView(LoginRequiredMixin, ListView, NormalRequiredMixin):
    model = Ideas
    template_name = 'strathideasapp/new_idea_list.html'
    context_object_name = 'ideas'
    ordering = ['-date_posted']
    paginate_by = 5


# --- Incubator Works --- #


class IncubatorListView(IncubatorRequiredMixin, LoginRequiredMixin, ListView):
    model = Ideas
    template_name = 'strathideasapp/vumbua_incubator.html'
    context_object_name = 'ideas'
    ordering = ['-date_posted']


class IncubatorDetailView(IncubatorRequiredMixin, LoginRequiredMixin, DetailView):
    model = Ideas
    template_name = 'strathideasapp/incubator_detail.html'
    context_object_name = 'incubators'


class CategoryListView(LoginRequiredMixin, ListView):
    model = Industry_category
    template_name = 'strathideasapp/categories.html'
    context_object_name = 'categories'


class InterestView(TemplateView):
    template_name = 'strathideasapp/interest.html'


class PostInterest(FormView):
    form_class = InterestForm
    template_name = 'strathideasapp/new_interest_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        idea = Ideas.objects.get(pk=self.kwargs['pk'])
        print(idea.user.user.email)
        form.instance.idea = idea
        form.save()
        # to_email = Ideas.objects.get()
        send_mail('An incubator is Interested in your Idea!',
                  'Hello, An incubator in the Vumbua platform is interested in your Idea. Log into Vumbua and Check out their offer!',
                  'dennis.mwika@strathmore.edu',
                  [idea.user.user.email],
                  fail_silently=False)

        return super(PostInterest, self).form_valid(form)

    def get_success_url(self):
        return reverse('strathideasapp:interest', kwargs={'pk': self.kwargs['pk']})


class InterestListView(LoginRequiredMixin, ListView):
    model = Interest
    template_name = 'strathideasapp/new_interested_list.html'
    context_object_name = 'interests'
    ordering = ['-timestamp']
    paginate_by = 4

    def get_queryset(self):
        self.idea = get_object_or_404(Ideas, pk=self.kwargs['pk'])
        print(self.idea.status)
        return Interest.objects.filter(idea=self.idea)

    def get_context_data(self, **kwargs):
        context = super(InterestListView, self).get_context_data(**kwargs)
        context['idea'] = self.idea
        return context


class PostForum(FormView):
    form_class = ForumForm
    template_name = 'strathideasapp/new_forum_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        idea = Ideas.objects.get(pk=self.kwargs['pk'])
        form.instance.idea = idea
        form.save()
        return super(PostForum, self).form_valid(form)

    def get_success_url(self):
        return reverse('strathideasapp:forum', kwargs={'pk': self.kwargs['pk']})


class AllForumsListView(LoginRequiredMixin, CommitteeRequiredMixin, ListView):
    model = Forum
    template_name = 'strathideasapp/all_forums.html'
    context_object_name = 'allforums'
    paginate_by = 5


class ForumListView(LoginRequiredMixin, ListView):
    model = Forum
    template_name = 'strathideasapp/new_forum_list.html'
    context_object_name = 'forums'
    ordering = ['-timestamp']
    paginate_by = 5

    def get_queryset(self):
        self.idea = get_object_or_404(Ideas, pk=self.kwargs['pk'])
        return Forum.objects.filter(idea=self.idea)

    def get_context_data(self, **kwargs):
        context = super(ForumListView, self).get_context_data(**kwargs)
        context['idea'] = self.idea
        return context


@login_required
def Forum_detail(request, forum):
    forum = get_object_or_404(Forum, forum=forum)
    comments = ForumComments.objects.filter(reply=None, forum=forum).order_by('-timestamp')

    if request.user.is_authenticated:
        ForumView.objects.get_or_create(user=request.user, forum=forum)

    form = ForumCommentsForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            body = request.POST.get('body')
            reply_id = request.POST.get('comment_ids')
            comment_qs = None
            if reply_id:
                comment_qs = ForumComments.objects.get(comment=reply_id)

            comment = ForumComments.objects.create(forum=forum, user=request.user, body=body, reply=comment_qs)
            comment.save()
            return redirect(reverse("strathideasapp:forum_detail", kwargs={'forum': forum.pk}))
        else:
            form = ForumCommentsForm()

    context = {
        'forum': forum,
        'comments': comments,
        'form': form,
    }
    return render(request, "strathideasapp/new_forum_detail.html", context)


@login_required
def Idea_detail(request, idea):
    idea = get_object_or_404(Ideas, idea=idea)
    comments = Comments.objects.filter(reply=None, idea=idea).order_by("-timestamp")

    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, idea=idea)

    form = CommentsForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            body = request.POST.get('body')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = Comments.objects.get(comment=reply_id)

            comment = Comments.objects.create(idea=idea, user=request.user, body=body, reply=comment_qs)
            comment.save()
            return redirect(reverse("strathideasapp:idea_detail", kwargs={
                'idea': idea.pk
            }))
        else:
            form = CommentsForm()

    context = {'idea': idea, 'comments': comments, 'form': form}
    return render(request, "strathideasapp/new_idea_detail.html", context)


class IdeaLikeToggle(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Ideas, idea=kwargs['idea'])
        url_ = obj.get_absolute_url()
        user = self.request.user
        if user.is_authenticated:
            obj.likes.add(user)
        else:
            obj.likes.remove(user)
        return url_


class IdeaCreateView(LoginRequiredMixin, NormalRequiredMixin, TemplateView):
    template_name = 'strathideasapp/new_idea_creation.html'
    model = Ideas

    def get(self, request, *args, **kwargs):
        form = IdeaCreationForm()
        return super(IdeaCreateView, self).get(request, form=form)

    def post(self, request, *args, **kwargs):
        form = IdeaCreationForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            problem_statement = form.cleaned_data['problem_statement']
            executive_summary = form.cleaned_data['executive_summary']
            objectives = form.cleaned_data['objectives']
            limitations = form.cleaned_data['limitations']
            category = form.cleaned_data['category']
            status = 'Pending'
            user = self.request.user.profile
            image = form.cleaned_data['image']
            is_public = form.cleaned_data['is_public']
            args = status, title, problem_statement, executive_summary, objectives, limitations, category, user, image, is_public
            Ideas.objects.create_idea_request(*args)
            return HttpResponseRedirect('/')
        return super(IdeaCreateView, self).get(request, form=form)


class IdeaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ideas
    template_name = 'strathideasapp/new_idea_creation.html'
    fields = ['title', 'problem_statement', 'executive_summary', 'objectives', 'limitations', 'image', 'is_public']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):  # check is the user updating is the owner of the idea
        idea = self.get_object()
        if self.request.user == idea.user:
            return True
        return False


class IdeaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ideas
    template_name = 'strathideasapp/ideas_confirm_delete.html'

    def test_func(self):
        idea = self.get_object()
        if self.request.user == idea.user:
            return True
        return False


class IdeaCategory(ListView):
    model = Ideas
    template_name = 'strathideasapp/ideas_category.html'

    def get_queryset(self):
        self.category = get_object_or_404(Industry_category, pk=self.kwargs['pk'])
        return Ideas.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super(IdeaCategory, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context


class SearchView(View):
    def get(self, request, *args, **kwargs):
        queryset = Ideas.objects.all()
        query = request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(problem_statement=query)
            ).distinct()
        context = {
            'queryset': queryset
        }
        return render(request, 'strathideasapp/search_results.html', context)


# login view


def login_view(request):
    current_user = request.user
    prof = Profile.objects.filter(user_id=current_user.id)
    if request.user.is_authenticated:
        for profi in prof:
            if profi.role.role_name == 'NormalUser':
                return redirect(reverse("strathideasapp:home"))
            elif profi.role.role_name == 'Industry':
                return redirect(reverse("strathideasapp:home"))
            elif profi.role.role_name == 'Committee':
                return redirect(reverse("strathideasapp:allideas"))
            elif profi.role.role_name == 'Incubator':
                return redirect(reverse("strathideasapp:incubator_list"))
    # next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)



        print(prof)
        for pro in prof:
            if pro.role.role_name == 'NormalUser':
                return redirect('/')
            elif pro.role.role_name == 'Industry':
                return redirect('/index.html')
            elif pro.role.role_name == 'Committee':
                return redirect('/committeehome')
            elif pro.role.role_name == 'Incubator':
                return redirect('/incubator')
            return redirect('/')
    context = {
        'form': form,
    }

    return render(request, "strathideasapp/vumbua_login.html", context)


# sign up


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.username = request.POST['username']
            user.email = request.POST['email']
            user.is_active = False
            user.refresh_from_db()
            user.profile.gender = user_form.cleaned_data.get('gender')
            user.profile.category = user_form.cleaned_data.get('category')
            user.profile.phone_number = user_form.cleaned_data.get('phone_number')
            user.profile.bio = user_form.cleaned_data.get('bio')
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your Vumbua account.'
            message = render_to_string('strathideasapp/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = user_form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'strathideasapp/user_confirmation.html')
        # else:
        #     # for msg in user_form.error_messages:
        #     #     messages.error(request, f'{msg}')
    else:
        user_form = UserRegistrationForm()
    return render(request, "strathideasapp/vumbua_signup.html", context={"user_form": user_form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'strathideasapp/user_app.html')
    else:
        return HttpResponse('Activation link is invalid!')


@login_required
def profile(request):
    if request.method == 'POST':
        user_update_form = UserUpdateForm(request.POST, instance=request.user)
        profile_update_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_update_form.is_valid() and profile_update_form.is_valid():
            user_update_form.save()
            profile_update_form.save()
            messages.success(request, f'Your account has been updated')
            return redirect('profile')
    else:
        user_update_form = UserUpdateForm(instance=request.user)
        profile_update_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_update_form': user_update_form,
        'profile_update_form': profile_update_form,
    }
    return render(request, 'strathideasapp/vumbua_profile.html', context)


# ----COMMITTEE WORK---- #
class CommitteeHome(LoginRequiredMixin, CommitteeRequiredMixin, ListView):
    model = Ideas
    template_name = 'strathideasapp/vumbua_committee.html'
    context_object_name = 'ideas'
    ordering = ['-date_posted']
    paginate_by = 10


class AllIdeasView(LoginRequiredMixin, CommitteeRequiredMixin, ListView):
    model = Ideas
    template_name = 'strathideasapp/new_committee_home.html'
    context_object_name = 'ideas'
    ordering = ['-date_posted']

    @staticmethod
    def committee_work(request, pk):
        committee = request.profile.role


class ApproveIdeaView(LoginRequiredMixin, CommitteeRequiredMixin, TemplateView):
    template_name = 'strathideasapp/new_idea_detail.html'

    def get(self, request, *args, **kwargs):
        idea_id = self.kwargs.get('idea')
        idea_obj = Ideas.objects.get(idea=idea_id)
        title = idea_obj.title
        problem_statement = idea_obj.problem_statement
        executive_summary = idea_obj.executive_summary
        limitations = idea_obj.limitations
        objectives = idea_obj.objectives
        idea_id = idea_obj.idea
        user = idea_obj.user

        if idea_obj.status == 'Approved':
            messages.info(request, 'You can\'t approve an idea twice')

        elif idea_obj.status == 'declined':
            messages.info(request, 'You can\'t approve an already declined idea')

        else:
            # ideas = get_object_or_404(Ideas, idea=self.kwargs['idea'])
            # vote_number = Voting.objects.get(ideas=idea_id)  # no of votes for a particular idea
            # print(vote_number.votes)

            total_profiles = Profile.objects.filter(role=2)
            print("Total committee members: ", total_profiles.count())  # total committee members

            # print(vote_number.member.role.role_id)
            # number_of_voters = # number of voters for a particular idea
            # if vote_number > (0.5 * ): # coming up with a quorum

            #Profile.person
            obj_to_update = Ideas.balance_objects.get(idea=idea_id)
            person = Profile.objects.get(user=request.user)
            # voted_id = []
            # # if person.has_voted is False:
            if person.has_voted is False :
                obj_to_update.votes = obj_to_update.votes + 1
                # obj_to_update.has_voted = True
                print("Total Votes: ", obj_to_update.votes)
                obj_to_update.approved = obj_to_update.approved + 1
                obj_to_update.total = obj_to_update.total + 1
            #     loggedin_ID = request.user.id
            #     # voted_id.append(loggedin_ID)
            #     # print(type(obj_to_update.voted_list))
            #     # obj_to_update.voted_list = obj_to_update.voted_list.append(loggedin_ID)
            #     # idea_obj.user.has_voted = True
                person.has_voted = True
                person.save()
                obj_to_update.save()

            # else:
            #     print("You have already voted for this idea")

            if obj_to_update.approved / obj_to_update.total > obj_to_update.denied / obj_to_update.total and obj_to_update.votes / total_profiles.count() > 0.5  :
                status = 'Approved'
                obj_to_update.status = status
                obj_to_update.save()
                send_mail('Your Idea Has been Approved!',
                      'Hello Innovator! Good News! Your Idea has been Approved by the Committee Members! It is ready  for the next step. Now interested Incubators can see your Idea.',
                      'dennis.mwika@strathmore.edu',
                      [idea_obj.user.user.email],
                      fail_silently=False)
        return redirect('strathideasapp:comm_home')


class DeclineIdeaView(LoginRequiredMixin, TemplateView):
    template_name = 'strathideasapp/vumbua_committee.html'

    def get(self, request, *args, **kwargs):
        idea_id = self.kwargs.get('idea')
        idea_obj = Ideas.objects.get(idea=idea_id)
        idea_id = idea_obj.idea
        user = idea_obj.user
        if idea_obj.status == 'Declined':
            messages.info(request, 'You can\'t decline an idea twice')

        elif idea_obj.status == 'Approved':
            messages.info(request, 'You can\'t decline an approved idea')
        else:
            status = 'Declined'
            obj_to_update = Ideas.balance_objects.get(idea=idea_id)
            obj_to_update.status = status
            obj_to_update.save()
            send_mail('Your Idea Has been Declined!',
                      'Hello Innovator! Your Idea was declined by the committee members, please try submitting it next time',
                      'dennis.mwika@strathmore.edu',
                      [idea_obj.user.user.email],
                      fail_silently=False)
        return redirect('strathideasapp:comm_home')
