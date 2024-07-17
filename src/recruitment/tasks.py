from celery import shared_task
from .models import *
from summarization import *


@shared_task
def summarize(posting_id, applicant_name, applicant_email):
    try:
        job_posting = JobPosting.objects.get(id=posting_id)
        answers = EssayAnswer.objects.filter(job_posting=job_posting)

        content = []
        for answer in answers:
            content.append(
                {
                    "question": answer.question.pk,
                    "answer": answer.answer_text,
                }
            )

        summarys = []

        for text in content:
            summ_text = summary_model(text["asnwer"])
            summarys.append(
                {
                    "qeustion": text["question"],
                    "summary": summ_text[0]["summary_text"],
                }
            )

        spell_result = hanspell_model(content)
        questions = []

        for question_id, details in spell_result.items():
            spelled_text = display_colored_text(details["words"])
            question = EssayQuestion.objects.get(id=question_id)
            questions.append(
                {
                    "question_id": question_id,
                    "question": details["original"],
                    "content": question.question_text,
                    "spelling": spelled_text,
                    "wrong_num": details["errors"],
                }
            )

        job_tech_result = job_tech(content)

        techs = job_tech_result["techs"]
        jobs = job_tech_result["jobs"]

        summary_instance = Summary(
            job_posting=job_posting,
            applicant_name=applicant_name,
            applicant_email=applicant_email,
            summarys=summarys,
            techs=techs,
            jobs=jobs,
            questions=questions,
        )
        summary_instance.save()
    except JobPosting.DoesNotExist:
        pass


def color_text(text, color):
    return f"<span style='color:{color}'>{text}</span>"


def display_colored_text(result):
    colored_text = ""
    for word, e in result["words"]:
        if e == 0:
            colored_text += color_text(word, "black") + " "
        elif e == 1:
            colored_text += color_text(word, "red") + " "
        elif e == 2:
            colored_text += color_text(word, "blue") + " "
        elif e == 3:
            colored_text += color_text(word, "green") + " "
        elif e == 4:
            colored_text += color_text(word, "orange") + " "

    return colored_text
