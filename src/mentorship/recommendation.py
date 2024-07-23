import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

from langchain.docstore.document import Document
from django.conf import settings
import re
import json
import os
from .models import Mentor, Mentee  # Django 모델 가져오기
from langchain_postgres.vectorstores import PGVector
from .vectorstores import VectorDBConnectionManager
from supabase.client import create_client


openai.api_key = os.environ["OPENAI_API_KEY"]


def process_mentors_descriptions(mentors_descriptions):
    recommendations = []
    for description in mentors_descriptions:
        mentor_name_match = re.search(r"\*\*(.*?) \((ID: \d+)\)\*\*", description)
        recommendation_reason_match = re.search(
            r"\-\s\*\*추천 이유\*\*:\s(.*?)(?=\-\s\*\*점수\*\*)", description, re.DOTALL
        )
        score_match = re.search(r"\-\s\*\*점수\*\*:\s([\d.]+)/5", description)
        score_explanation_match = re.search(
            r"\-\s\*\*점수가 5점이 아닌 이유\*\*:\s(.*)", description
        )

        recommendation = {
            "mentor_name": mentor_name_match.group(1).strip(),
            "ID": int(mentor_name_match.group(2).split(": ")[1]),
            "recommendation_reason": recommendation_reason_match.group(1).strip(),
            "score": float(score_match.group(1)),
            "score_explanation": score_explanation_match.group(1).strip(),
        }
        recommendations.append(recommendation)

    output = {"recommendations": recommendations}
    json_output = json.dumps(output, ensure_ascii=False, indent=2)
    return json_output


import json


def get_mentor_and_mentee_recommendations(mentee_id):
    # Django 데이터베이스에서 Mentor와 Mentee 데이터를 가져오기
    mentors = Mentor.objects.select_related("employee").values(
        "employee__id",
        "employee__first_name",
        "employee__last_name",
        "employee__job_title",
        "employee__location",
        "employee__mbti",
        "employee__hobbies__name",
    )
    mentees = Mentee.objects.select_related("employee").values(
        "employee__id",
        "employee__first_name",
        "employee__last_name",
        "employee__job_title",
        "employee__location",
        "employee__mbti",
        "employee__hobbies__name",
    )

    combined_data = []
    for mentor in mentors:
        combined_data.append(
            {
                "id": mentor["employee__id"],
                "name": f"{mentor['employee__first_name']} {mentor['employee__last_name']}",
                "role": "mentor",
                "job_title": mentor["employee__job_title"],
                "location": mentor["employee__location"],
                "mbti": mentor["employee__mbti"],
                "hobbies": mentor["employee__hobbies__name"],
            }
        )
    for mentee in mentees:
        combined_data.append(
            {
                "id": mentee["employee__id"],
                "name": f"{mentee['employee__first_name']} {mentee['employee__last_name']}",
                "role": "mentee",
                "job_title": mentee["employee__job_title"],
                "location": mentee["employee__location"],
                "mbti": mentee["employee__mbti"],
                "hobbies": mentee["employee__hobbies__name"],
            }
        )

    # 데이터를 LangChain 문서로 변환
    combined_docs = [
        {"content": json.dumps(data, ensure_ascii=False)} for data in combined_data
    ]

    # 문서 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    split_texts = []
    for doc in combined_docs:
        split_texts.extend(text_splitter.split_text(doc["content"]))

    documents = [Document(page_content=text) for text in split_texts]

    # 벡터 스토어 생성 (테스트 되면 --> 멘티 멘토 추가 할때 업데이트에 추가)
    connection_manager = VectorDBConnectionManager()
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY,
        model="text-embedding-3-small",
    )
    supabase_client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
    )
    vector_store = connection_manager.get_connection(
        db_name="postgres",
        client=supabase_client,
        embeddings=embeddings,
    )
    vector_store.add_documents(documents)

    retriever = vector_store.as_retriever()
    print(retriever)
    # 수정된 프롬프트 템플릿
    prompt_template = """
    모든 답변에 대해서 친근하고 부드러운 어조로 대답해주세요.
    당신은 멘토링 추천 시스템입니다.
    주어진 데이터를 바탕으로 정확하게, 여러 사항들을 고려해서 {id} 멘티에게 추천하는 멘토 반드시 세 명을 알려주세요.
    만약 2명 이하의 사람이라면 왜 부족하게 추천 해줬는지 설명해주세요.
    멘토인 사람들만 추천해주세요. 멘토의 ID를 이름 옆에 적어주세요
    추천 이유, 5점 만점에 몇 점인지, 점수가 5점이 아닌 경우 이유를 각각 설명해주세요

    # 질문:
    {id}에게 추천할 멘토를 찾아주세요.

    # 문맥:
    멘토링 추천 시스템
    """

    llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )

    prompt_data = prompt_template.format(id=mentee_id)
    response = qa_chain({"query": prompt_data})

    ids = []

    for document in response["source_documents"]:
        page_content = document.page_content

        lines = page_content.split("\n")
        id_line = next((line for line in lines if line.startswith("ID:")), None)

        if id_line:
            id_value = id_line.split(":")[-1].strip()
            ids.append(id_value)

    mentors_descriptions = []
    text = response["result"]
    split_text = text.split("\n\n")

    for st in range(1, len(split_text) - 1):
        mentors_descriptions.append(split_text[st])
    print(mentors_descriptions)
    json_output = process_mentors_descriptions(mentors_descriptions)

    return json_output
