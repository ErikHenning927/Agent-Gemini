from typing  import List, Dict, TypedDict, Optional


class AgentState(TypedDict, total = False):
    pergunta: str
    triagem: Dict
    resposta: Optional[str]
    citacoes: List[dict]
    rag_sucesso: bool
    acao_final: str