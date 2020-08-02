from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import reverse


@login_required
def redirect(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('staff:main_menu'))
    else:
        return HttpResponseRedirect(reverse('resident:information'))
