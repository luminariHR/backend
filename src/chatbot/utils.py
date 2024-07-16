from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_prompt_template():
    return """
        당신은 질의 응답 작업의 보조자입니다.
        다음 검색된 컨텍스트 조각을 사용하여 질문에 답하세요.
        답을 모르면 모른다고 하면 됩니다.
        딱딱하게 대답하지 말고 친근한 어조로 대답하세요.
        답변을 찾은 문서의 제목과 페이지를 알려주세요.
        한국어로 대답하세요.

        # Question:
        {question}
        # Context:
        {context}

        # Answer:
        """


def create_qa_chain(retriever, prompt_template):
    def qa_chain(input_dict):
        context_docs = retriever.get_relevant_documents(input_dict["query"])
        context_with_metadata = []
        for doc in context_docs:
            context_with_metadata.append(
                f"출처: {doc.metadata['source']} (페이지 {doc.metadata['page']}, 카테고리 {doc.metadata['category']})\n{doc.page_content}\n"
            )

        context = "\n".join(context_with_metadata)
        prompt = prompt_template.format(question=input_dict["query"], context=context)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    return qa_chain


# 사용자의 질문에 따라 해당 카테고리의 문서로 이동하여 질문에 대한 답변 생성
def answer_question_based_on_metadata(retriever, question):
    context_docs = retriever.get_relevant_documents(question)
    if context_docs:
        prompt_template = get_prompt_template()
        qa_chain = create_qa_chain(retriever, prompt_template)
        return qa_chain({"query": question})
    else:
        return "관련된 문서를 찾을 수 없습니다."
