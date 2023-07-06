from django.urls.conf import path
from qanda import views

app_name = "qanda"

urlpatterns = [
    path("q/<int:pk>", views.QuestionDetailView.as_view(), name="question_detail"),
    path("q/<int:pk>/answer", views.CreateAnswerView.as_view(), name="answer_question"),
    path("q/search", views.SearchView.as_view(), name="question_search"),
    path("", views.TodaysQuestionList.as_view(), name="todays_questions"),
    path("a/<int:pk>/accept", views.UpdateAnswerAcceptance.as_view(), name="update_answer_acceptance"),
    path("daily/<int:year>/<int:month>/<int:day>/", views.DailyQuestionList.as_view(), name="daily_questions"),
    path("ask", views.AskQuestionView.as_view(), name="ask"),
]
