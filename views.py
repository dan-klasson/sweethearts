from django.http import HttpResponse
from django.views import View
import facepy
from allauth.socialaccount.models import SocialAccount, SocialApp

class DeAuthView(View):

    def post(self, request, *args, **kwargs):

        signed_request = request.POST.get('signed_request')
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
            return HttpResponse(status=200)

        # Mark user as inactive
        user = social_account.user
        user.is_active = False
        user.save()

        return HttpResponse(status=200)
