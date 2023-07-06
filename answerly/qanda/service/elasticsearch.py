import logging

from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

FAILED_TO_LOAD_ERROR = "FAILED to load {}: {!r}"

logger = logging.getLogger(__name__)


def get_client():
    return Elasticsearch(
        hosts=[
            {"host": settings.ES_HOST, "port": settings.ES_PORT},
        ]
    )


def _question_to_dict(question):
    return {
        "_id": question.id,
        "_type": "doc",
        "text": f"{question.title}\n{question.question}",
        "question_body": question.question,
        "title": question.title,
        "id": question.id,
        "created": question.created,
    }


def bulk_load(questions):
    all_ok = True
    es_questions = (_question_to_dict(q) for q in questions)
    stream = streaming_bulk(
        get_client(),
        es_questions,
        index=settings.ES_INDEX,
        raise_on_error=False,
    )
    for ok, result in stream:
        if not ok:
            all_ok = False
            _, result = result.popitem()
            logger.error(FAILED_TO_LOAD_ERROR.format(result["_id"], result))

    return all_ok


def search_for_questions(query):
    client = get_client()
    result = client.search(
        index=settings.ES_INDEX,
        body={
            "query": {
                "match": {"text": query},
            }
        },
    )
    return (h["_source"] for h in result["hits"]["hits"])


def upsert(question):
    client = get_client()
    question_as_dict = _question_to_dict(question)
    question_as_dict.pop("_type")
    question_as_dict.pop("_id")
    response = client.update(
        index=settings.ES_INDEX,
        id=question.id,
        body={
            "doc": question_as_dict,
            "doc_as_upsert": True,
        },
    )
    return response
