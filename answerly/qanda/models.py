from django.conf import settings
from django.db import models
from django.urls.base import reverse
from qanda.service import elasticsearch


class Question(models.Model):
    title = models.CharField(max_length=255)
    question = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("qanda:question_detail", kwargs={"pk": self.id})

    def can_accept_answers(self, user):
        return user == self.user

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
        elasticsearch.upsert(self)


class Answer(models.Model):
    answer = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created",)
