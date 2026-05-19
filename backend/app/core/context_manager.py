import os
import google.generativeai as genai
from sqlalchemy.orm import Session
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
        
        # Check if compression is needed (every 50 interactions)
        count = self.db.query(Context).filter(Context.user_id == user_id, Context.is_compressed == False).count()
        if count > 50:
            self.compress_context(user_id)

    def get_active_context(self, user_id: int):
        contexts = self.db.query(Context).filter(
            Context.user_id == user_id
        ).order_by(Context.created_at.desc()).limit(10).all()
        
        return "\n".join([c.content for c in reversed(contexts)])

    def compress_context(self, user_id: int):
        if not self.model:
            return

        uncompressed = self.db.query(Context).filter(
            Context.user_id == user_id, 
            Context.is_compressed == False
        ).limit(40).all()
        
        if not uncompressed:
            return

        full_text = "\n".join([c.content for c in uncompressed])
        
        prompt = f"Resuma as seguintes interações de chat mantendo os pontos principais e o contexto para uma IA: \n\n{full_text}"
        
        try:
            response = self.model.generate_content(prompt)
            summary = response.text
            
            # Mark old contexts as compressed
            for c in uncompressed:
                c.is_compressed = True
            
            # Add summary context
            summary_context = Context(
                user_id=user_id, 
                content=f"[RESUMO]: {summary}", 
                is_compressed=True
            )
            self.db.add(summary_context)
            self.db.commit()
        except Exception as e:
            print(f"Erro na compressão de contexto: {e}")
            self.db.rollback()
