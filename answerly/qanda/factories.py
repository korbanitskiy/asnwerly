from unittest.mock import patch

import factory
from factory.django import DjangoModelFactory
from qanda.models import Question
from user.factories import UserFactory


class QuestionFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Question {n}")
    question = "What is the question?"
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Question

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with patch("qanda.service.elasticsearch.Elasticsearch"):
            return super()._create(model_class, *args, **kwargs)
