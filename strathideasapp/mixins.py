from django.core.exceptions import PermissionDenied
from strathideasapp.models import Profile
from django.shortcuts import render, redirect, reverse


class CommitteeRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        current_user = self.request.user
        if Profile.objects.filter(role_id=2, user_id = current_user.id):
            return super().dispatch(request,*args,**kwargs)
        else:
            return redirect('strathideasapp:forbidden')


class IncubatorRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        current_user = self.request.user
        if Profile.objects.filter(role_id=1, user_id = current_user.id):
            return super().dispatch(request,*args,**kwargs)
        else:
            return redirect('strathideasapp:forbidden')


class NormalRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        current_user = self.request.user
        if Profile.objects.filter(role_id=4, user_id = current_user.id):
            return super().dispatch(request,*args,**kwargs)
        else:
            return redirect('strathideasapp:forbidden')
