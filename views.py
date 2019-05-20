from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView
from allauth.socialaccount.models import (
    SocialAccount, SocialApp, SocialToken
)
import facepy

class IndexView(TemplateView):

    template_name = 'index.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:

            social_token = SocialToken.objects.filter(
                account__user=self.request.user
            ).last()

            if social_token:
                graph = facepy.GraphAPI(social_token.token)
                context['data'] = graph.get('me?fields=name,picture.type(large)')

        return context


class DeAuthView(View):

    def post(self, request, *args, **kwargs):

        signed_request = request.POST.get('signed_request')

        # Get facebook secret
        secret = SocialApp.objects.filter(provider='facebook') \
            .first().secret

        # Parse the signed request
        try:
            obj = facepy.SignedRequest(signed_request, secret)
        except facepy.exceptions.SignedRequestError as e:
            return HttpResponse(status=400, content=str(e))

        # Fetch the user
        try:
            social_account = SocialAccount.objects.get(uid=obj.user.id)
        except SocialAccount.DoesNotExist:
            return HttpResponse(status=400, content="User does not exist")

        # Mark user as inactive
        user = social_account.user
        user.is_active = False
        user.save()

        return HttpResponse(status=200)
