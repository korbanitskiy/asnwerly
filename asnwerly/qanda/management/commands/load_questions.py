from django.core.management import BaseCommand
from qanda.models import Question
from qanda.service import elasticsearch


class Command(BaseCommand):
    help = "Load all questions into Elasticsearch"

    def handle(self, *args, **kwargs):
        qs = Question.objects.all()
        all_loaded = elasticsearch.bulk_load(qs)
        if all_loaded:
            self.stdout.write(self.style.SUCCESS("Successfully loaded"))
        else:
            self.stdout.write(self.style.WARNING("Some questions not loaded. See logged errors."))
