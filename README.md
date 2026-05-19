# JARVIS - Inteligência Artificial Pessoal (100% Gratuito)

O JARVIS é um assistente pessoal avançado, agora atualizado para funcionar de forma totalmente gratuita e com um módulo completo de assistente pessoal.

## 🚀 Novidades da Versão 4.0 (Defesa Massiva)

- **Camada de Defesa Interna**:
  - **Jarvis Defense**: Sistema de detecção de intrusão e auto-bloqueio de IPs maliciosos.
  - **Anti-Reconhecimento**: Honeypots integrados e ofuscação total da estrutura interna da API.
  - **Anti-Fingerprinting**: Remoção de assinaturas de tecnologia em headers e respostas.
  - **Hardening de Infraestrutura**: Containers rodando como non-root, filesystem restritivo e limites de recursos.
  - **Análise Estática (SAST)**: Integração com Bandit e Semgrep para garantir código seguro.
- **Segurança Máxima**: Rate Limiting agressivo, Criptografia AES-256 e Audit Logs detalhados.
- **100% Gratuito**: Google Gemini API e yfinance integrados.
- **Assistente Pessoal Completo**: Gestão de Notas, Lembretes e Tarefas.

## 🛠️ Configuração

1. **Obtenha sua API Key do Gemini**:
   - Acesse [Google AI Studio](https://aistudio.google.com/app/apikey).
   - Crie uma nova API Key gratuita.

2. **Configure o arquivo .env**:
   - Copie o arquivo `.env.example` para `.env`.
   - Insira sua `GEMINI_API_KEY`.

3. **Setup e Hardening**:
   ```bash
   ./setup.sh
   ./security_hardening.sh
   ```

4. **Execução com Docker**:
   ```bash
   docker-compose up --build
   ```

## 📂 Estrutura do Projeto

- `backend/`: API FastAPI com módulos de IA, Finanças e Assistente.
- `frontend/`: Interface minimalista estilo terminal.
- `data/`: Volume para persistência do banco de dados SQLite.

## 🔒 Níveis de Acesso

- **Nível 1 (Comum)**: Assistente factual e prestativo.
- **Nível 2 (Eron/Admin)**: Acesso total, comandos técnicos e gestão do sistema.

---
*Desenvolvido para ser o assistente definitivo, sempre presente e com custo zero.*
