from .hanspell import spell_checker
import re
import pandas as pd
import os
from openai import OpenAI
import json
from transformers import pipeline


summarizer = pipeline(
    "summarization",
    model="aoome123/my_model",
    max_length=600,
    no_repeat_ngram_size=3,
    min_length=150,
    length_penalty=2.0,
    num_beams=1,
)


def hanspell_model(applicant):

    # 질문을 위한 글자수 제한 전처리
    def process_statements_by_char_limit(text, char_limit=400):
        result = []
        current_text = ""

        text = text.strip()

        # 분할되지 않는 경우도 처리
        segments = re.split(r"([.!?])", text)
        if len(segments) == 1:
            if len(text) <= char_limit:
                return [text]
            else:
                for i in range(0, len(text), char_limit):
                    result.append(text[i : i + char_limit].strip())
                return result

        for i in range(0, len(segments) - 1, 2):
            segment = segments[i].strip() + segments[i + 1]

            temp_text = current_text + " " + segment if current_text else segment
            num_chars = len(temp_text)

            if num_chars <= char_limit:
                current_text = temp_text
            else:
                result.append(current_text.strip())
                current_text = segment

        if current_text:
            result.append(current_text.strip())
            current_text = ""

        return result

    Result = {}
    for qa in applicant:
        texts = process_statements_by_char_limit(qa["answer"])
        result = {"errors": 0, "original": "", "checked": "", "words": []}

        original_text = ""
        checked_text = ""

        for text in texts:
            sub_result = spell_checker.check(text.strip())
            result["errors"] += sub_result.errors
            original_text += " " + sub_result.original
            checked_text += " " + sub_result.checked
            for word, error in sub_result.words.items():
                result["words"].append((word, error))

        result["original"] = original_text.strip()
        result["checked"] = checked_text.strip()
        Result[qa["question"]] = result

    return Result


# 자소서 기반 질문, 답변 전처리후 기술 직종 뽑아옴
def job_tech(applicant):

    # 기술, 직종 분류 모델
    # {"techs" : 자소서 기반 사용 가능한 기술들, "jobs" : 이 사람에게 어울리는 직종}
    def sub_job_tech(text):
        data = pd.read_csv(
            "./recruitment/data/output.csv"
        )  # 실제 잡코리아 내에 있는 직종 분류된 데이터
        jobs_list = list(set(data["Inner Text"].tolist()))

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        # 질문 및 응답을 처리할 함수
        def process_question(system_message, user_prompt):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt},
                ],
            )
            try:
                content = json.loads(response.choices[0].message.content.strip())
                return content
            except (json.JSONDecodeError, KeyError):
                return {}

        # 기술과 직종 추출 함수
        def extract_tech_and_jobs():
            system_message = f"""
            You are a recruitment officer.
            You want to know what technical skills this person possesses and determine the specific job roles based only on reading the personal statement this person has provided.
            You must output in the given JSON format.
            The list of possible job roles is as follows:
            - {', '.join(jobs_list)}
            JSON Format:
            {{
              "technical_skills": ["skill1", "skill2", ...],
              "jobs": ["job1", "job2", ...]
            }}
            Respond in Korean.
            """
            user_prompt = f"Please extract the technical skills and specific job roles for this person based on their statement:\n{text}"

            result = process_question(system_message, user_prompt)

            if result:
                return {"techs": result["technical_skills"], "jobs": result["jobs"]}

            return {}

        # 시행 횟수 최대 3번 어쩌다 한번씩 데이터를 안가져옴 3번이면 어지간 하면 다 가져옴
        for _ in range(3):
            result = extract_tech_and_jobs()
            if result["techs"] and result["jobs"]:
                return result

        return {"techs": [], "jobs": []}  # 실패 시

    # 질문을 위한 글자수 제한 전처리(최대 8000자)
    def process_statements_by_char_limit(applicant, char_limit=8000):
        combined_text = ""
        result = []

        for qa in applicant:
            current_sentence = qa["answer"].strip()

            temp_text = (
                combined_text + " " + current_sentence
                if combined_text
                else current_sentence
            )

            if len(temp_text) <= char_limit:
                combined_text = temp_text
            else:
                if combined_text.strip():
                    result.append(combined_text.strip())
                combined_text = current_sentence

        if combined_text:
            if combined_text.strip():
                result.append(combined_text.strip())

        return result

    texts = process_statements_by_char_limit(applicant)
    result = {"techs": [], "jobs": []}
    for text in texts:
        jt = sub_job_tech(text)
        result["techs"] += jt["techs"]
        result["jobs"] += jt["jobs"]
    result["techs"] = list(set(result["techs"]))
    result["jobs"] = list(set(result["jobs"]))
    return result


def summary_model(text):
    sum_text = summarizer(text)
    return sum_text
