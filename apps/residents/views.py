from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .models import Board, Property, Street


class BoardMembersListView(LoginRequiredMixin, TemplateView):
    template_name = 'residents/board_members.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['board'] = Board.objects.all()[0]
        return context


class MainMenuView(LoginRequiredMixin, TemplateView):
    template_name = 'residents/main_menu.html'


class ResidentListView(LoginRequiredMixin, TemplateView):
    template_name = 'residents/residents.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['properties'] = Property.objects.all()
        context['by_street'] = {}

        for street in Street.objects.all():
            context['by_street'][street.street] = Property.objects.filter(street=street)

        return context
