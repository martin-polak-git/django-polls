from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect

from django.urls import reverse
from django.views import generic

from django.contrib import messages

from .models import Poll, Choice

def index(request):
    context = {'umfragen': Poll.objects.all(), 'titel': "Umfragenseite"}
    return render(request=request, template_name='polls/index.html',
                  context=context)

class PollDetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/umfrage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_can_see_results = False
        if 'voted_polls' in self.request.session:
            if type(self.request.session['voted_polls']) == list:
                if context['object'].id in self.request.session['voted_polls']:
                    user_can_see_results = True
        context['voted'] = user_can_see_results

        return context

class ResultsDetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_can_see_results = False
        if 'voted_polls' in self.request.session:
            if type(self.request.session['voted_polls']) == list:
                if context['object'].id in self.request.session['voted_polls']:
                    user_can_see_results = True
        context['access'] = user_can_see_results

        return context

def vote(request, slug):
    umfrage = get_object_or_404(Poll, slug=slug)
    try:
        ausgewahlte_antwort = umfrage.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, "Fehler: keine bzw. eine ungueltige Antwort ausgewaehlt!")
        return HttpResponseRedirect(reverse('polls:umfrage-detail', args=(umfrage.slug,)))
    else:
        ausgewahlte_antwort.votes += 1
        ausgewahlte_antwort.save()

        if 'voted_polls' in request.session:
            if type(request.session['voted_polls']) == list:
                request.session['voted_polls'].append(umfrage.id)
            else:
                request.session['voted_polls'] = [umfrage.id]
        else:
            request.session['voted_polls'] = [umfrage.id]

        return HttpResponseRedirect(reverse('polls:results', args=(umfrage.slug,)))
