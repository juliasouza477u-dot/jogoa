# Quiz Bíblico — Flask + Neon (PostgreSQL) + Render

## Estrutura do projeto
```
aaa11/
├── app.py                # Aplicação Flask, modelos, 107 perguntas e rotas
├── requirements.txt      # Dependências Python
├── render.yaml           # Especificação de deploy no Render
├── .env.example          # Variáveis de ambiente (copie para .env em desenvolvimento)
├── DEPLOY.md             # Este arquivo
├── static/
│   ├── style.css         # CSS otimizado para celular (mobile-first, touch-friendly)
│   └── app.js            # Evita zoom em duplo-toque no celular
└── templates/
    ├── base.html
    ├── index.html        # Tela inicial
    ├── quiz.html         # Pergunta com 4 alternativas (grandes, para toque)
    ├── gameover.html     # "Você errou" + campo para digitar o nome no placar
    └── ranking.html      # Top 10 placar
```

## Como funciona o jogo
1. O jogador começa no `/` e clica em "Começar Quiz".
2. A cada acerto, avança para a próxima pergunta e soma 1 ponto.
3. **Se errar qualquer pergunta, o jogo acaba ("morre")** e ele é levado à tela de game over.
4. Na tela de game over, aparece a pontuação final e um campo para **digitar o nome** para salvar no placar.
5. O placar (`/ranking`) exibe os 10 melhores scores.

## Banco de dados no Neon (PostgreSQL)
1. Acesse [https://neon.tech](https://neon.tech) e crie uma conta.
2. Crie um projeto e, dentro dele, um banco de dados (PostgreSQL).
3. No painel do Neon, copie a **connection string** (exemplo):
   `postgresql://usuario:senha@ep-xxx.us-east-1.aws.neon.tech/bancodedados?sslmode=require`
4. Essa URL é o valor da variável de ambiente `DATABASE_URL`.

## Deploy no Render.com
1. Acesse [https://render.com](https://render.com) e crie uma conta.
2. Conecte seu repositório GitHub (ou faça upload dos arquivos).
3. Crie um novo **Web Service**.
4. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Em **Environment Variables**, adicione:
   - `SECRET_KEY`: qualquer string aleatória longa (ex: `openssl rand -hex 32`)
   - `DATABASE_URL`: a connection string do Neon copiada no passo 3
6. O Render instalará as dependências (incluindo `psycopg2-binary` para PostgreSQL) e iniciará o app com Gunicorn.

### Usando o render.yaml
O arquivo `render.yaml` já está pronto. No Render, você pode usar "Infrastructure as Code" e importar esse arquivo. Como o banco fica no Neon (não no Render), deixe `databases: []` e defina `DATABASE_URL` manualmente nas variáveis de ambiente do serviço.

## Desenvolvimento local (SQLite)
Se não quiser usar Neon agora, basta não definir `DATABASE_URL`. O app usará automaticamente um banco SQLite local (`quiz.db`) e funcionará normalmente para testes.

```bash
pip install -r requirements.txt
python app.py
# Acesse http://127.0.0.1:5000
```

## Otimizações para celular
- `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">`
- Botões grandes (altura mínima ~48px) e fáceis de tocar
- Cores escuras com contraste para leitura ao ar livre
- JavaScript que impede zoom indesejado em duplo-toque
- Layout de coluna única com `max-width: 480px`, centralizado