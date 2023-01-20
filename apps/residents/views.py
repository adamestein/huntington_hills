from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .models import Board, BoardTerm, Property, Street


class BoardMembersListView(LoginRequiredMixin, TemplateView):
    template_name = 'residents/board_members.html'

    def get_context_data(self, **kwargs):
        board = Board.objects.all()[0]

        context = super().get_context_data(**kwargs)
        context['is_staff'] = self.request.user.is_staff

        for position in BoardTerm.POSITIONS:
            office = position[1].lower().replace(' ', '_')
            person = getattr(board, office)

            try:
                start_year = BoardTerm.objects.filter(person=person).first().elected_date.year
            except AttributeError:
                start_year = 'N/A'

            context[office] = {'start_year': start_year, 'person': person}
        
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
