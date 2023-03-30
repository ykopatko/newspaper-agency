from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic

from agency.forms import (
    RedactorForm,
    RedactorUpdYearsOfExperienceForm,
    NewspaperForm,
    NewspaperSearchForm,
    RedactorSearchForm,
    TopicSearchForm,
)
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
    queryset = Topic.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TopicListView, self).get_context_data(**kwargs)

        name = self.request.GET.get("name", "")

        context["search_form"] = TopicSearchForm(initial={
            "name": name
        })

        return context

    def get_queryset(self) -> QuerySet:
        form = TopicSearchForm(self.request.GET)

        if form.is_valid():
            return Topic.objects.filter(
                name__icontains=form.cleaned_data["name"]
            )

        return self.queryset


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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(NewspaperListView, self).get_context_data(**kwargs)

        title = self.request.GET.get("title", "")

        context["search_form"] = NewspaperSearchForm(initial={
            "title": title
        })

        return context

    def get_queryset(self) -> QuerySet:
        form = NewspaperSearchForm(self.request.GET)

        if form.is_valid():
            return Newspaper.objects.filter(
                title__icontains=form.cleaned_data["title"]
            )

        return self.queryset


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
    queryset = get_user_model().objects.prefetch_related("newspapers__topic")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RedactorListView, self).get_context_data(**kwargs)

        username = self.request.GET.get("username", "")

        context["search_form"] = RedactorSearchForm(initial={
            "username": username
        })

        return context

    def get_queryset(self) -> QuerySet:
        form = RedactorSearchForm(self.request.GET)

        if form.is_valid():
            return get_user_model().objects.filter(
                username__icontains=form.cleaned_data["username"]
            )

        return self.queryset


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
