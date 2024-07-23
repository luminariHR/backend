import re
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from django.conf import settings
from core.vectorstores import VectorDBConnectionManager
from supabase.client import create_client


def process_mentors_descriptions(mentors_descriptions):
    recommendations = []
    for description in mentors_descriptions:
        mentor_name_match = re.search(r"\*\*(.*?) \((ID: \d+)\)\*\*", description)
        recommendation_reason_match = re.search(
            r"\-\s\*\*추천 이유\*\*:\s(.*?)(?=\-\s\*\*점수\*\*)", description, re.DOTALL
        )
        score_match = re.search(r"\-\s\*\*점수\*\*:\s([\d.]+)/5", description)

        if (
            mentor_name_match
            and mentor_name_match.group(1)
            and mentor_name_match.group(2)
        ):
            mentor_name = mentor_name_match.group(1).strip()
            ID = int(mentor_name_match.group(2).split(": ")[1])
        else:
            continue
        if recommendation_reason_match and recommendation_reason_match.group(1):
            recommendation_reason = recommendation_reason_match.group(1).strip()
        else:
            recommendation_reason = "죄송합니다. 충분한 정보가 없습니다."
        if score_match and score_match.group(1):
            score = float(score_match.group(1))
        else:
            score = "N/A"

        recommendation = {
            "mentor_name": mentor_name,
            "ID": ID,
            "recommendation_reason": recommendation_reason,
            "score": score,
        }
        recommendations.append(recommendation)

    output = {"recommendations": recommendations}
    return output


def get_mentor_and_mentee_recommendations(mentee_id):

    # 벡터 스토어 생성 (테스트 되면 --> 멘티 멘토 추가 할때 업데이트에 추가)
    connection_manager = VectorDBConnectionManager()
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY,
        model="text-embedding-3-large",
    )
    supabase_client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
    )
    vector_store = connection_manager.get_connection(
        db_name="postgres_mentorship",
        client=supabase_client,
        embeddings=embeddings,
        table_name="mentorship_documents",
        query_name="mentorship_match_documents",
    )
    retriever = vector_store.as_retriever()

    # 수정된 프롬프트 템플릿
    prompt_template = """
    모든 답변에 대해서 친근하고 부드러운 어조로 대답해주세요.
    당신은 멘토링 추천 시스템입니다.
    주어진 데이터를 바탕으로 정확하게, 여러 사항들을 고려해서 {ID} 멘티에게 추천하는 멘토 반드시 세 명을 알려주세요.
    만약 모르겠으면 만들어내지 마세요.
    멘토인 사람들만 추천해주세요. 멘토의 ID를 이름 옆에 적어주세요.
    추천 이유, 점수, 점수가 5점이 아닌 이유를 각각 설명해주세요.

    # 질문:
    {ID}에게 추천할 멘토를 찾아주세요.

    # 문맥:
    멘토링 추천 시스템

    # 출력 형식:
    1. **[멘토 이름] (ID: X)**
    - **추천 이유**: [추천 이유]
    - **점수**: [점수]/5

    모든 멘토는 이 형식에 맞춰서 추천해 주세요.
    """

    llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )

    prompt_data = prompt_template.format(ID=mentee_id)
    response = qa_chain({"query": prompt_data})

    ids = []
    if len(response["source_documents"]) == 0:
        return {"recommendations": []}
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
    json_output = process_mentors_descriptions(mentors_descriptions)

    return json_output
