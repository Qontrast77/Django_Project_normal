from django.views.generic import TemplateView
from .models import Tournament, Match

class ShowTournamentsView(TemplateView):
    template_name = "tournaments/show_tournaments.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tournaments'] = Tournament.objects.all()
        context['matches'] = Match.objects.all()
        return context