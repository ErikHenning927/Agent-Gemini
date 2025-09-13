import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing  import Literal, List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from load_documents import *
from utils import *
load_dotenv()


gemini_key = os.getenv('GEMINI_API_KEY')


# resp_test = llm.invoke("Quem é você? Seja criativo")


TRIAGEM_PROMPT = (
    "Você é um triador de Service Desk para políticas internas da empresa Carraro Desenvolvimento. "
    "Dada a mensagem do usuário, retorne SOMENTE um JSON com:\n"
    "{\n"
    '  "decisao": "AUTO_RESOLVER" | "PEDIR_INFO" | "ABRIR_CHAMADO",\n'
    '  "urgencia": "BAIXA" | "MEDIA" | "ALTA",\n'
    '  "campos_faltantes": ["..."]\n'
    "}\n"
    "Regras:\n"
    '- **AUTO_RESOLVER**: Perguntas claras sobre regras ou procedimentos descritos nas políticas (Ex: "Posso reembolsar a internet do meu home office?", "Como funciona a política de alimentação em viagens?").\n'
    '- **PEDIR_INFO**: Mensagens vagas ou que faltam informações para identificar o tema ou contexto (Ex: "Preciso de ajuda com uma política", "Tenho uma dúvida geral").\n'
    '- **ABRIR_CHAMADO**: Pedidos de exceção, liberação, aprovação ou acesso especial, ou quando o usuário explicitamente pede para abrir um chamado (Ex: "Quero exceção para trabalhar 5 dias remoto.", "Solicito liberação para anexos externos.", "Por favor, abra um chamado para o RH.").'
    "Analise a mensagem e decida a ação mais apropriada."
)

class TriagemOut(BaseModel):
    decisao: Literal["AUTO_RESOLVER", "PEDIR_INFO", "ABRIR_CHAMADO"]
    urgencia: Literal["BAIXA", "MEDIA", "ALTA"]
    campos_faltantes: List[str] = Field(default_factory=list)

llm_triagem = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.0, 
    api_key=gemini_key
)

triagem_chain = llm_triagem.with_structured_output(TriagemOut)

def triagem(mensagem: str) -> Dict:
    saida: TriagemOut = triagem_chain.invoke([
        SystemMessage(content=TRIAGEM_PROMPT),
        HumanMessage(content=mensagem)
    ])

    return saida.model_dump()


testes = [
    'Posso reembolsar a internet?',
    'Quero mais 5 dias de trabalho remoto. Como faço?',
    'Quantas capiravas tem no parque barigui',
]

# for msg_teste in testes:
#     print(f"Pergunta: {msg_teste}\n -> Resposta: {triagem(msg_teste)}\n")


chunks = load_docs()
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=gemini_key
)


vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(
                                search_type="similarity_score_threshold", 
                                search_kwargs={"score_threshold": 0.3, "k": 4}
                            )

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


for msg_teste in testes:
    resposta = perguntar_politica_rag(msg_teste)
    print(f"PERGUNTA: {msg_teste}")
    print(f"RESPOSTA: {resposta['answer']}")
    if resposta['contexto_encontrado']:
        print("CITAÇÕES:")
        for c in resposta['citacoes']:
            print(f" - Documento: {c['documento']}, Página: {c['pagina']}")
            print(f"   Trecho: {c['trecho']}")
        print("------------------------------------")