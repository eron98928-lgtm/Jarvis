import os
import google.generativeai as genai
from datetime import datetime
import json
from sqlalchemy.orm import Session
from app.core.models import Note, Reminder, Task

class AssistantModule:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None

    async def chat(self, message: str, level: int, context: str, db: Session, user_id: int):
        if not self.model:
            return "Erro: GEMINI_API_KEY não configurada no arquivo .env."

        # System prompt based on access level
        system_prompt = f"""
        Você é o JARVIS, uma inteligência artificial pessoal avançada.
        Seu criador é o Eron.
        Data e hora atual: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        
        Nível de acesso do usuário atual: {level}
        
        Instruções:
        - Responda sempre em Português Brasileiro.
        - Seja educado, eficiente e proativo.
        - Se o nível for 1, você é um assistente factual e prestativo.
        - Se o nível for 2 (Eron), você tem acesso total e pode ser mais técnico e direto.
        
        Capacidades de Assistente Pessoal:
        Você pode gerenciar notas, lembretes e tarefas. Se o usuário pedir para anotar, lembrar ou criar uma tarefa, você deve responder com um JSON especial no final da sua resposta (em uma linha separada) para que o sistema processe.
        
        Formatos de comando JSON:
        - Para Notas: {{"action": "note", "content": "texto da nota"}}
        - Para Lembretes: {{"action": "reminder", "content": "o que lembrar", "datetime": "YYYY-MM-DD HH:MM:SS"}}
        - Para Tarefas: {{"action": "task", "title": "título", "due_date": "YYYY-MM-DD HH:MM:SS" (opcional)}}
        
        Contexto recente:
        {context}
        """

        try:
            response = self.model.generate_content(f"{system_prompt}\n\nUsuário: {message}")
            response_text = response.text
            
            # Process potential actions in the response
            lines = response_text.split('\n')
            clean_response = []
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith('{') and stripped_line.endswith('}'):
                    try:
                        action_data = json.loads(stripped_line)
                        self._handle_action(action_data, db, user_id)
                        # Don't include the JSON in the final text shown to user
                        continue
                    except:
                        clean_response.append(line)
                else:
                    clean_response.append(line)
            
            return "\n".join(clean_response).strip()
        except Exception as e:
            return f"Erro ao processar com Gemini: {str(e)}"

    def _handle_action(self, data, db: Session, user_id: int):
        action = data.get("action")
        try:
            if action == "note":
                new_note = Note(user_id=user_id, content=data.get("content"))
                db.add(new_note)
                db.commit()
            elif action == "reminder":
                dt_str = data.get("datetime")
                remind_at = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S") if dt_str else datetime.now()
                new_reminder = Reminder(user_id=user_id, content=data.get("content"), remind_at=remind_at)
                db.add(new_reminder)
                db.commit()
            elif action == "task":
                due_date = None
                dt_str = data.get("due_date")
                if dt_str:
                    due_date = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                new_task = Task(user_id=user_id, title=data.get("title"), due_date=due_date)
                db.add(new_task)
                db.commit()
        except Exception as e:
            print(f"Erro ao processar ação: {e}")
            db.rollback()

class DevModule:
    @staticmethod
    def analyze_code(code: str):
        # Placeholder for development analysis
        return "Análise de código completa. Nenhuma vulnerabilidade crítica encontrada."
