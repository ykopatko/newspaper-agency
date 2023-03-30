from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic

from agency.forms import RedactorForm, RedactorUpdYearsOfExperienceForm, NewspaperForm
from agency.models import Newspaper, Topic


@login_required
def index(request):
    """View function for the home page of the site."""

    num_redactors = get_user_model().objects.count()
    num_newspapers = Newspaper.objects.count()
    num_topics = Topic.objects.count()
    latest_newspapers = Newspaper.objects.all().order_by("-published_date")[:5]
    featured_redactors = get_user_model().objects.filter(is_featured=True)[:5]

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_redactors": num_redactors,
        "num_newspapers": num_newspapers,
        "num_topics": num_topics,
        "num_visits": num_visits + 1,
        "latest_newspapers": latest_newspapers,
        "featured_redactors": featured_redactors,
    }

    return render(request, "agency/index.html", context=context)


class TopicListView(LoginRequiredMixin, generic.ListView):
    model = Topic
    paginate_by = 5


class TopicCreateView(LoginRequiredMixin, generic.CreateView):
    model = Topic
    fields = "__all__"
    success_url = reverse_lazy("agency:topic-list")


class TopicUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Topic
    fields = "__all__"
    success_url = reverse_lazy("agency:topic-list")


class TopicDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Topic
    success_url = reverse_lazy("agency:topic-list")


class NewspaperListView(LoginRequiredMixin, generic.ListView):
    model = Newspaper
    paginate_by = 5
    queryset = Newspaper.objects.all().select_related("topic")


class NewspaperDetailView(LoginRequiredMixin, generic.DetailView):
    model = Newspaper


class NewspaperCreateView(LoginRequiredMixin, generic.CreateView):
    model = Newspaper
    form_class = NewspaperForm
    success_url = reverse_lazy("agency:newspaper-list")


class NewspaperUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Newspaper
    form_class = NewspaperForm

    def get_success_url(self):
        return reverse_lazy(
            "agency:newspaper-detail",
            kwargs={"pk": self.object.pk}
        )


class NewspaperDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Newspaper
    success_url = reverse_lazy("agency:newspaper-list")


class RedactorListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 5


class RedactorDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.all().prefetch_related("newspapers__topic")


class RedactorCreateView(LoginRequiredMixin, generic.CreateView):
    model = get_user_model()
    form_class = RedactorForm
    success_url = reverse_lazy("agency:redactor-list")


class RedactorUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    form_class = RedactorUpdYearsOfExperienceForm

    def get_success_url(self):
        return reverse_lazy(
            "agency:redactor-detail",
            kwargs={"pk": self.object.pk}
        )


class RedactorDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = get_user_model()
    success_url = reverse_lazy("agency:redactor-list")


@login_required
def assign_redactor(request, pk):
    newspaper = get_object_or_404(Newspaper, pk=pk)

    if request.user in newspaper.redactors.all():
        newspaper.redactors.remove(request.user)
    else:
        newspaper.redactors.add(request.user)

    return HttpResponseRedirect(reverse("agency:newspaper-detail", args=[pk]))
