import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.models import Context

class ContextManager:
    def __init__(self, db: Session):
        self.db = db
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None

    def add_interaction(self, user_id: int, content: str):
        new_context = Context(user_id=user_id, content=content)
        self.db.add(new_context)
        self.db.commit()
        
        # Gatilho de compressão baseado em volume de caracteres (~15.000)
        # Isso evita estouro de memória (OOM) se as mensagens forem muito grandes
        total_chars = self.db.query(func.sum(func.length(Context.content))).filter(
            Context.user_id == user_id, 
            Context.is_compressed == False
        ).scalar() or 0

        if total_chars > 15000:
            self.compress_context(user_id)

    def get_active_context(self, user_id: int):
        # Retorna as últimas 10 interações para manter a janela de contexto imediata
        contexts = self.db.query(Context).filter(
            Context.user_id == user_id
        ).order_by(Context.created_at.desc()).limit(10).all()
        
        return "\n".join([c.content for c in reversed(contexts)])

    def compress_context(self, user_id: int):
        if not self.model:
            return

        # Busca interações não comprimidas para resumir
        uncompressed = self.db.query(Context).filter(
            Context.user_id == user_id, 
            Context.is_compressed == False
        ).order_by(Context.created_at.asc()).all()
        
        if len(uncompressed) < 2:
            return

        # Mantém as últimas 5 mensagens fora da compressão para fluidez da conversa
        to_compress = uncompressed[:-5]
        if not to_compress:
            return

        full_text = "\n".join([c.content for c in to_compress])
        
        prompt = f"Resuma as seguintes interações de chat mantendo os pontos principais e o contexto para uma IA: \n\n{full_text}"
        
        try:
            response = self.model.generate_content(prompt)
            summary = response.text
            
            # Marca contextos antigos como comprimidos
            for c in to_compress:
                c.is_compressed = True
            
            # Adiciona o resumo como um novo contexto comprimido
            summary_context = Context(
                user_id=user_id, 
                content=f"[RESUMO DE CONTEXTO]: {summary}", 
                is_compressed=True
            )
            self.db.add(summary_context)
            self.db.commit()
        except Exception as e:
            print(f"Erro na compressão de contexto: {e}")
            self.db.rollback()
