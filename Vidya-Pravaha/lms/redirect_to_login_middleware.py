from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

class RedirectToLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define a list of protected URLs
        protected_urls = [
            '//',  # Add the URLs you want to protect
            '/about/',
            '/services/',
            '/contact/',
            '/lsign/',
            '/psign/',
            # '/login_form/',
            # '/login/',
            '/logout/'
                    # Add more URLs as needed
        ]

        # Check if the user is not authenticated and the requested URL is in the list of protected URLs
        if not request.user.is_authenticated and request.path in protected_urls:
            # Display a message to the user
            messages.warning(request, "Log in first to view the page.")
            
            # Redirect to the login page
            return HttpResponseRedirect(reverse('login_form'))

        # Continue with the request
        response = self.get_response(request)
        return response
