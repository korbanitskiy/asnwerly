from datetime import date

from django.test import RequestFactory, TestCase
from qanda.factories import QuestionFactory
from qanda.views import DailyQuestionList
from user.factories import UserFactory

QUESTION_CREATED_STRFTIME = "%Y-%m-%d %H:%M"


class DailyQUestionListTestCase(TestCase):
    NEEDLE_TEMPLATE = """
    <li>
      <a href="/q/{id}">{title}</a> by {username} on {date}
    </li>
    """
    REQUEST = RequestFactory().get(path="/q/2030-12-31")
    TODAY = date.today()

    def test_GET_on_day_with_many_questions(self):
        todays_questions = [QuestionFactory() for _ in range(10)]
        response = DailyQuestionList.as_view()(
            self.REQUEST,
            year=self.TODAY.year,
            month=self.TODAY.month,
            day=self.TODAY.day,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["object_list"].count(), 10)
        content = response.rendered_content
        for q in todays_questions:
            needle = self.NEEDLE_TEMPLATE.format(
                id=q.id, title=q.title, username=q.user.username, date=q.created.strftime(QUESTION_CREATED_STRFTIME)
            )
            self.assertInHTML(needle, content)


class QuestionDetailViewTestCase(TestCase):
    LOGIN_TO_POST_ANSWERS = "Login to post answer."
    NO_ANSWERS_SNIPPET = "No answers yet!"
    QUESTION_SNIPPET = """
    <div class="question">
      <div class="meta col-sm-12">
        <h1>{title}</h1>
        Asked by {user} on {date}
      </div>
      <div class="body col-sm-12">
        <p>{body}</p>
      </div>
    </div>
    """

    def test_logged_in_user_can_post_answers(self):
        question = QuestionFactory()
        logged_in = self.client.login(
            username=question.user.username,
            password=UserFactory.password,
        )
        self.assertTrue(logged_in)
        response = self.client.get("/q/{}".format(question.id))
        content = response.rendered_content

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(self.NO_ANSWERS_SNIPPET, content)
        template_names = [t.name for t in response.templates]
        self.assertIn("qanda/common/post_answer.html", template_names)

        question_needle = self.QUESTION_SNIPPET.format(
            title=question.title,
            user=question.user.username,
            date=question.created.strftime(QUESTION_CREATED_STRFTIME),
            body=QuestionFactory.question,
        )
        self.assertInHTML(question_needle, content)
