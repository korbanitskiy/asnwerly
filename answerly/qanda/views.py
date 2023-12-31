from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DayArchiveView,
    DetailView,
    RedirectView,
    TemplateView,
    UpdateView,
)
from qanda.forms import AnswerAcceptanceForm, AnswerForm, QuestionForm
from qanda.models import Answer, Question
from qanda.service.elasticsearch import search_for_questions


class AskQuestionView(LoginRequiredMixin, CreateView):
    form_class = QuestionForm
    template_name = "qanda/ask.html"

    def get_initial(self) -> Dict[str, Any]:
        return {
            "user": self.request.user.id,
        }

    def form_valid(self, form):
        action = self.request.POST.get("action")
        if action == "SAVE":
            return super().form_valid(form)
        elif action == "PREVIEW":
            preview = Question(
                question=form.cleaned_data["question"],
                title=form.cleaned_data["title"],
            )
            ctx = self.get_context_data(preview=preview)
            return self.render_to_response(context=ctx)

        return HttpResponseBadRequest()


class QuestionDetailView(DetailView):
    model = Question
    ACCEPT_FORM = AnswerAcceptanceForm(initial={"accepted": True})
    REJECT_FORM = AnswerAcceptanceForm(initial={"accepted": False})

    def get_context_data(self, **kwargs: Any):
        ctx = super().get_context_data(**kwargs)
        ctx["answer_form"] = AnswerForm(
            initial={
                "user": self.request.user.id,
                "question": self.object.id,
            }
        )

        if self.object.can_accept_answers(self.request.user):
            ctx["accept_form"] = self.ACCEPT_FORM
            ctx["reject_form"] = self.REJECT_FORM

        return ctx


class CreateAnswerView(LoginRequiredMixin, CreateView):
    form_class = AnswerForm
    template_name = "qanda/create_answer.html"

    def get_initial(self):
        return {
            "question": self.get_question().id,
            "user": self.request.user.id,
        }

    def get_context_data(self, **kwargs: Any):
        return super().get_context_data(question=self.get_question(), **kwargs)

    def get_success_url(self) -> str:
        return self.object.question.get_absolute_url()

    def form_valid(self, form):
        action = self.request.POST.get("action")
        if action == "SAVE":
            return super().form_valid(form)
        elif action == "PREVIEW":
            ctx = self.get_context_data(preview=form.cleaned_data["answer"])
            return self.render_to_response(ctx)

        return HttpResponseBadRequest()

    def get_question(self):
        return Question.objects.get(pk=self.kwargs["pk"])


class UpdateAnswerAcceptance(LoginRequiredMixin, UpdateView):
    form_class = AnswerAcceptanceForm
    queryset = Answer.objects.all()

    def get_success_url(self) -> str:
        return self.object.question.get_absolute_url()

    def form_invalid(self, form):
        return HttpResponseRedirect(redirect_to=self.object.question.get_absolute_url())


class DailyQuestionList(DayArchiveView):
    queryset = Question.objects.all()
    date_field = "created"
    month_format = "%m"
    allow_empty = True


class TodaysQuestionList(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        today = timezone.now()
        return reverse(
            "qanda:daily_questions",
            kwargs={
                "day": today.day,
                "month": today.month,
                "year": today.year,
            },
        )


class SearchView(TemplateView):
    template_name = "qanda/search.html"

    def get_context_data(self, **kwargs: Any):
        query = self.request.GET.get("q")
        ctx = super().get_context_data(query=query, **kwargs)
        if query:
            ctx["hits"] = search_for_questions(query)

        return ctx
