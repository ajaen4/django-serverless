from django.http import HttpResponse, Http404
from django.shortcuts import render

from .models import Question


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {
        "latest_question_list": latest_question_list,
    }
    return render(request, "polls/index.html", context)


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
        return render(request, "polls/detail.html", {"question": question})
    except Question.DoesNotExist:
        raise Http404("Question does not exist")


def results(_, question_id):
    return HttpResponse(f"You're looking at the results of question {question_id}")


def vote(_, question_id):
    return HttpResponse(f"You're voting on question {question_id}")
