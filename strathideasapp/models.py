from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse
from django.db.models import CharField, IntegerField, Model
from django_mysql.models import ListCharField,ListTextField
# from PIL import Image

# Create your models here.


class Roles(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=30)
    description = models.CharField(max_length=120)

    def __str__(self):
        return "%s" % self.role_name



    # def save(self):
    #     super().save()
    #     img = Image.open(self.image.path)
    #
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)

    # @receiver(post_save, sender=User)
    # def create_profile(sender, instance, created, **kwargs):
    #     if created:
    #         profile = Profile.objects.create(user=instance)
    #         profile.save()
    #
    # @receiver(post_save, sender=User)
    # def save_profile(sender, instance, created, **kwargs):
    #     instance.profile.save()

class Profile(models.Model):
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    )
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    category = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=12)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    role = models.ForeignKey(Roles, default=4, on_delete=models.CASCADE)
    bio = models.CharField(max_length=100, blank=True, null=True)
    has_voted = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.user.username} Profile'



class IdeaManager(models.Manager):
    def create_idea_request(self,*args):
        status, title, problem_statement, executive_summary, objectives, limitations, category, user, image, is_public = args
        idea_request = self.create(
            title=title,
            problem_statement=problem_statement,
            executive_summary=executive_summary,
            objectives=objectives,
            limitations=limitations,
            status=status,
            category=category,
            user=user,
            image=image,
            is_public=is_public,
            )

        return idea_request


class IdeaBalanceManager(models.Manager):
    def handle_status(self, *args):
        ideaid, status, title, problem_statement, executive_summary, objectives, limitations = args
        idea_request = self.create(
            title=title,
            problem_statement=problem_statement,
            executive_summary=executive_summary,
            objectives=objectives,
            limitations=limitations,
            status=status,

            )
        # updates the leave status in the LeaveRequest table for the same instance
        obj_to_update = Ideas.balance_objects.get(idea=ideaid)
        obj_to_update.status = status
        obj_to_update.save()
        return idea_request


class Industry_category(models.Model):
    industry_category_id = models.AutoField(primary_key=True)
    industry_category_name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    image = models.ImageField(default='default.jpg', upload_to='cat_pics')

    def __str__(self):
        return self.industry_category_name


class Ideas(models.Model):
    IDEA_STATUS = (
        ('Approved', 'Approved'),
        ('Pending', 'Pending'),
        ('Declined', 'Declined'),
    )

    objects = IdeaManager()
    balance_objects = IdeaBalanceManager()
    idea = models.AutoField(primary_key=True)
    user = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.CASCADE, related_name = 'person')
    title = models.CharField(max_length=400)
    problem_statement = models.TextField(max_length=2000)
    executive_summary = models.TextField(max_length=2000)
    objectives = models.TextField(max_length=2000)
    status = models.CharField(max_length=100, choices=IDEA_STATUS)
    limitations = models.TextField(max_length=2000)
    date_posted = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, blank=True, related_name='idea_likes')
    image = models.ImageField(upload_to='idea_pics')
    # view_count = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Industry_category, on_delete=models.CASCADE, null=True)
    is_public = models.BooleanField(default=True)
    # role = models.ForeignKey(Roles,on_delete = models.CASCADE)
    # dislikes = models.IntegerField(default = 0)
    approved = models.IntegerField(default=0)
    denied = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    votes = models.IntegerField(default=0)
    voted_id = models.IntegerField(default=0)

    # voted_list = ListTextField(default = 0, base_field=IntegerField(),size=100, null = True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('strathideasapp:idea_detail', kwargs={'idea': self.idea})

    def get_like_url(self):
        return reverse('strathideasapp:idea_like', kwargs={'idea': self.idea})

    def get_api_like_url(self):
        return reverse('strathideasapp:idea_like_api', kwargs={'idea': self.idea})

    @property
    def view_count(self):
        return PostView.objects.filter(idea=self).count()

    @property
    def get_comments(self):
        return self.comments.filter(idea=self, reply=None).order_by('-timestamp')

    @property
    def comment_count(self):
        return Comments.objects.filter(idea=self, reply=None).count()





class Forum(models.Model):
    forum = models.AutoField(primary_key = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    idea = models.ForeignKey(Ideas, on_delete = models.CASCADE)
    title = models.CharField(max_length = 100)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def view_count(self):
        return ForumView.objects.filter(forum=self).count()

    @property
    def comment_count(self):
        return ForumComments.objects.filter(forum=self, reply = None).count()

    @property
    def get_comments(self):
        return self.comments.filter(forum = self, reply=None).order_by('-timestamp')


class ForumComments(models.Model):
    comment = models.AutoField(primary_key = True)
    reply = models.ForeignKey('ForumComments', null = True, blank = True, related_name = "replies", on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    forum = models.ForeignKey(Forum,related_name='comments', on_delete = models.CASCADE)
    body = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        return self.body


class ForumView(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    forum = models. ForeignKey(Forum, on_delete= models.CASCADE)

    def __str__(self):
        return self.user.username


class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Ideas, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Incubator(models.Model):
    incubator = models.AutoField(primary_key=True)
    incubator_name = models.CharField(max_length=30)
    idea = models.ForeignKey(Ideas, on_delete=models.CASCADE)
    incubator_description = models.CharField(max_length=120)
    incubator_expertise = models.CharField(max_length=100)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.incubator_name


class Incubatees(models.Model):
    incubator = models.ForeignKey(Incubator, on_delete=models.CASCADE)
    idea = models.OneToOneField(Ideas, on_delete=models.CASCADE)

    def __str__(self):
        return self.idea


# class Voting(models.Model):
#     member = models.ForeignKey(Profile, on_delete=models.CASCADE)
#     ideas = models.ForeignKey(Ideas, on_delete=models.CASCADE, related_name='votes')
#     votes = models.IntegerField(default=0)
#     has_voted = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.votes


class Company(models.Model):
    company = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=40)
    industry = models.ForeignKey(Industry_category, on_delete=models.CASCADE)
    description = models.CharField(max_length=120)
    interested_department = models.CharField(max_length=40)

    def __str__(self):
        return self.company_name


class Comments(models.Model):
    comment = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Ideas, on_delete=models.CASCADE, related_name='comments')
    reply = models.ForeignKey('Comments', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    body = models.CharField(max_length=2000)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return self.body


class Industry_committee(models.Model):
    committee = models.AutoField(primary_key=True)
    committee_name = models.CharField(max_length=30)
    industry = models.OneToOneField(Industry_category, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE)

    def __str__(self):
        return self.committee_name


# class ThumbsSignal(models.Model):
#     signal = models.AutoField(primary_key=True)
#     user = models.ForeignKey(Profile, on_delete=models.CASCADE)
#     idea = models.ForeignKey(Ideas, on_delete=models.CASCADE)
#     #thumbs_up = models.BooleanField(default = False)
#     #thumbs_down = models.BooleanField(default = False)
#     value = models.IntegerField()
#     date = models.DateTimeField(auto_now=True)


class OpinionPolls(models.Model):
    idea = models.ForeignKey(Ideas, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    comment = models.OneToOneField(Comments, on_delete=models.CASCADE)
    comment_reply = models.CharField(max_length=200)

    def __str__(self):
        return self.comment


class Industry_request_category(models.Model):
    industry_request_cat = models.AutoField(primary_key = True)
    industry_request_cat_name = models.CharField(max_length = 30)


class Industry_request(models.Model):
    industry_request = models.AutoField(primary_key = True)
    industry_request_cat = models.ForeignKey(Industry_request_category, on_delete = models.CASCADE)
    user = models.ForeignKey(Profile, on_delete = models.CASCADE)
    industry = models.ForeignKey(Industry_category, on_delete=models.CASCADE)
    cost = models.IntegerField()
    description = models.TextField()
    duration = models.IntegerField()
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.industry_request_cat


class Interest(models.Model):
    interest = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Ideas, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
