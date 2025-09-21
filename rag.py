from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from llms import *
from embed import *
from utils import formatar_citacoes

prompt_rag = ChatPromptTemplate.from_messages([
    ("system",
     "Você é um Assistente de Políticas Internas (RH/IT) da empresa Carraro Desenvolvimento. "
     "Responda SOMENTE com base no contexto fornecido. "
     "Se não houver base suficiente, responda apenas 'Não sei'."),

    ("human", "Pergunta: {input}\n\nContexto:\n{context}")
])

document_chain = create_stuff_documents_chain(llm_triagem, prompt_rag)


def perguntar_politica_rag(pergunta: str) -> Dict:
    docs_relacionados = retriever.invoke(pergunta)
    if not docs_relacionados:
        return {"answer": "Não Sei.",
                "citacoes": [],
                "contexto_encontrado": False}
    
    answer = document_chain.invoke({"input": pergunta,
                                    "context": docs_relacionados})
    
    txt = (answer or "").strip()
    if txt.rstrip(".!?") == "Não sei":
        return {"answer": "Não Sei.",
                "citacoes": [],
                "contexto_encontrado": False}
    return {"answer": txt,
                "citacoes": formatar_citacoes(docs_relacionados, pergunta),
                "contexto_encontrado": True}