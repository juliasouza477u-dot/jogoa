import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-dev-temporaria')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///' + os.path.join(basedir, 'quiz.db')
)
uri = app.config['SQLALCHEMY_DATABASE_URI']
if uri:
    # Corrige URL do tipo postgres:// para postgresql:// (necessário para SQLAlchemy)
    if uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql://', 1)
    # Garante que o driver psycopg2 seja usado explicitamente se for PostgreSQL
    if uri.startswith('postgresql://') and '+' not in uri.split('://')[1].split('/')[0]:
        uri = uri.replace('postgresql://', 'postgresql+psycopg2://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Placar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, default='Anônimo')
    pontuacao = db.Column(db.Integer, nullable=False, default=0)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'nome': self.nome, 'pontuacao': self.pontuacao, 'data': self.data.isoformat()}


class Pergunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enunciado = db.Column(db.Text, nullable=False)
    opcao_a = db.Column(db.String(200), nullable=False)
    opcao_b = db.Column(db.String(200), nullable=False)
    opcao_c = db.Column(db.String(200), nullable=False)
    opcao_d = db.Column(db.String(200), nullable=False)
    resposta_correta = db.Column(db.String(1), nullable=False)
    referencia = db.Column(db.String(100), nullable=True)


PERGUNTAS_SEED = [
    {"enunciado": "De acordo com 1 Coríntios 12:4, o que existe em grande diversidade, mas provém do mesmo e único Espírito?",
     "opcao_a": "Os dons (carismas)", "opcao_b": "Os pecados", "opcao_c": "As igrejas", "opcao_d": "As nações",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:4"},
    {"enunciado": "Segundo 1 Coríntios 12:5, há diversidade de ministérios (serviços), mas quem é o mesmo a quem todos servem?",
     "opcao_a": "O mesmo Senhor (Jesus Cristo)", "opcao_b": "O mesmo apóstolo", "opcao_c": "O mesmo diabo", "opcao_d": "O mesmo anjo",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:5"},
    {"enunciado": "No versículo 6, o texto diz que há diversidade de operações/realizações, mas quem é aquele que opera tudo em todos?",
     "opcao_a": "O mesmo Deus (o Pai)", "opcao_b": "O mesmo homem", "opcao_c": "O mesmo profeta", "opcao_d": "O mesmo rei",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:6"},
    {"enunciado": "De acordo com 1 Coríntios 12:7, para qual finalidade a manifestação do Espírito é dada a cada um?",
     "opcao_a": "Para o bem comum (edificar a comunidade)", "opcao_b": "Para se vangloriar", "opcao_c": "Para ganhar dinheiro", "opcao_d": "Para ficar famoso",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:7"},
    {"enunciado": "No versículo 8, qual é o primeiro dom específico mencionado que é dado a alguém pelo Espírito?",
     "opcao_a": "A palavra de sabedoria", "opcao_b": "O dom de curas", "opcao_c": "O dom de línguas", "opcao_d": "O dom de profecia",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:8"},
    {"enunciado": "Ainda no versículo 8, qual dom aparece logo ao lado da palavra de sabedoria?",
     "opcao_a": "A palavra de ciência (ou conhecimento)", "opcao_b": "O dom de fé", "opcao_c": "O dom de milagres", "opcao_d": "O dom de interpretação",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:8"},
    {"enunciado": "Segundo 1 Coríntios 12:9, qual virtude/dom é concedido a outro pelo mesmo Espírito?",
     "opcao_a": "A fé", "opcao_b": "A riqueza", "opcao_c": "O poder político", "opcao_d": "A beleza física",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:9"},
    {"enunciado": "No versículo 9, qual dom relacionado à restauração da saúde física/espiritual é concedido?",
     "opcao_a": "O dom de curas", "opcao_b": "O dom de línguas", "opcao_c": "O dom de sabedoria", "opcao_d": "O dom de discernimento",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:9"},
    {"enunciado": "No versículo 10, qual dom está associado à realização de sinais extraordinários?",
     "opcao_a": "O dom de operar milagres", "opcao_b": "O dom de interpretar sonhos", "opcao_c": "O dom de cantar", "opcao_d": "O dom de cozinhar",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:10"},
    {"enunciado": "Ainda no versículo 10, qual dom consiste na capacidade de proclamar a palavra inspirada por Deus?",
     "opcao_a": "O dom de profecia", "opcao_b": "O dom de curas", "opcao_c": "O dom de fé", "opcao_d": "O dom de sabedoria",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:10"},
    {"enunciado": "Qual dom citado no versículo 10 dá a capacidade de reconhecer se uma inspiração vem de Deus ou não?",
     "opcao_a": "O dom de discernimento dos espíritos", "opcao_b": "O dom de milagres", "opcao_c": "O dom de línguas", "opcao_d": "O dom de ciência",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:10"},
    {"enunciado": "Ainda no versículo 10, qual é o dom ligado à oração e louvor em linguagem inspirada?",
     "opcao_a": "A diversidade (variedade) de línguas", "opcao_b": "O dom de escrita", "opcao_c": "O dom de liderança", "opcao_d": "O dom de ensino",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:10"},
    {"enunciado": "Para completar a utilidade do dom das línguas na comunidade, qual dom o versículo 10 menciona em seguida?",
     "opcao_a": "A interpretação das línguas", "opcao_b": "O dom de profecia", "opcao_c": "O dom de curas", "opcao_d": "O dom de fé",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:10"},
    {"enunciado": "Conforme 1 Coríntios 12:11, quem é o agente responsável por realizar e distribuir todas essas manifestações?",
     "opcao_a": "Um só e o mesmo Espírito Santo", "opcao_b": "O pastor da igreja", "opcao_c": "O próprio crente", "opcao_d": "O conselho de anciãos",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:11"},
    {"enunciado": "Como o Espírito Santo distribui esses dons a cada pessoa, segundo o final do versículo 11?",
     "opcao_a": "A cada um em particular, como Ele quer (conforme a Sua vontade)", "opcao_b": "Aos que pagam mais", "opcao_c": "Somente aos apóstolos", "opcao_d": "Por ordem de chegada",
     "resposta_correta": "A", "referencia": "1 Coríntios 12:11"},
    {"enunciado": "Segundo Lucas 1:39, qual foi a atitude de Maria logo após saber da gravidez de Isabel?",
     "opcao_a": "Pôs-se a caminho e foi apressadamente à região montanhosa, a uma cidade de Judá", "opcao_b": "Ficou em casa esperando", "opcao_c": "Foi para o Egito", "opcao_d": "Foi ao templo de Jerusalém",
     "resposta_correta": "A", "referencia": "Lucas 1:39"},
    {"enunciado": "De acordo com Lucas 1:40, em cuja casa Maria entrou e a quem ela saudou?",
     "opcao_a": "Entrou na casa de Zacarias e saudou Isabel", "opcao_b": "Entrou na casa de Herodes e saudou a rainha", "opcao_c": "Entrou na casa de Pilatos e saudou a esposa", "opcao_d": "Entrou na casa de João e saudou a mãe",
     "resposta_correta": "A", "referencia": "Lucas 1:40"},
    {"enunciado": "O que aconteceu com a criança no ventre de Isabel assim que ela ouviu a saudação de Maria (v. 41)?",
     "opcao_a": "A criança estremeceu (pulou de alegria) em seu ventre", "opcao_b": "A criança chorou", "opcao_c": "A criança dormiu", "opcao_d": "Não aconteceu nada",
     "resposta_correta": "A", "referencia": "Lucas 1:41"},
    {"enunciado": "O que aconteceu com a própria Isabel quando Maria a saudou (v. 41)?",
     "opcao_a": "Isabel ficou cheia do Espírito Santo", "opcao_b": "Isabel ficou doente", "opcao_c": "Isabel fugiu", "opcao_d": "Isabel ficou surda",
     "resposta_correta": "A", "referencia": "Lucas 1:41"},
    {"enunciado": "Com qual proclamação e em alta voz Isabel acolheu Maria no versículo 42?",
     "opcao_a": "\"Bendita és tu entre as mulheres e bendito é o fruto do teu ventre!\"", "opcao_b": "\"Bem-vinda à nossa casa\"", "opcao_c": "\"Que Deus te abençoe\"", "opcao_d": "\"Tu és a mais humilde\"",
     "resposta_correta": "A", "referencia": "Lucas 1:42"},
    {"enunciado": "Como Isabel chama Maria no versículo 43 ao se admirar com a visita?",
     "opcao_a": "\"A mãe do meu Senhor\"", "opcao_b": "\"Minha irmã\"", "opcao_c": "\"Serva do Senhor\"", "opcao_d": "\"Rainha de Israel\"",
     "resposta_correta": "A", "referencia": "Lucas 1:43"},
    {"enunciado": "Segundo Lucas 1:45, por que Maria é chamada de bem-aventurada (feliz) por Isabel?",
     "opcao_a": "Porque acreditou que se cumpririam as coisas ditas da parte do Senhor", "opcao_b": "Porque era rica", "opcao_c": "Porque era princesa", "opcao_d": "Porque conhecia a lei",
     "resposta_correta": "A", "referencia": "Lucas 1:45"},
    {"enunciado": "Como se inicia o hino de louvor de Maria (o Magnificat) no versículo 46?",
     "opcao_a": "\"A minha alma engrandece o Senhor\"", "opcao_b": "\"Glória a Deus nas alturas\"", "opcao_c": "\"Aleluia\"", "opcao_d": "\"Senhor, tem piedade\"",
     "resposta_correta": "A", "referencia": "Lucas 1:46"},
    {"enunciado": "No versículo 47, onde se alegra o espírito de Maria?",
     "opcao_a": "Em Deus, seu Salvador", "opcao_b": "No templo", "opcao_c": "Em sua casa", "opcao_d": "Em Jerusalém",
     "resposta_correta": "A", "referencia": "Lucas 1:47"},
    {"enunciado": "Por que, segundo Lucas 1:48, todas as gerações chamarão Maria de bem-aventurada?",
     "opcao_a": "Porque Deus olhou para a humilde condição de sua serva e o Todo-Poderoso fez nela grandes coisas", "opcao_b": "Porque ela era famosa", "opcao_c": "Porque era muito estudiosa", "opcao_d": "Porque era de família nobre",
     "resposta_correta": "A", "referencia": "Lucas 1:48"},
    {"enunciado": "De acordo com Lucas 1:50 e 51, sobre quem repousa a misericórdia de Deus e o que Ele faz com os orgulhosos?",
     "opcao_a": "A misericórdia repousa de geração em geração sobre os que o temem, e Ele dispersa os orgulhosos de coração", "opcao_b": "Sobre os ricos, e enriquece os orgulhosos", "opcao_c": "Sobre os reis, e destrói os humildes", "opcao_d": "Sobre os sábios, e confunde os orgulhosos",
     "resposta_correta": "A", "referencia": "Lucas 1:50-51"},
    {"enunciado": "O que Deus faz com os poderosos e com os humildes, segundo Lucas 1:52?",
     "opcao_a": "Derruba os poderosos de seus tronos e eleva os humildes", "opcao_b": "Enobrece os poderosos e humilha os humildes", "opcao_c": "Ignora ambos", "opcao_d": "Faz os poderosos servirem os humildes",
     "resposta_correta": "A", "referencia": "Lucas 1:52"},
    {"enunciado": "Conforme Lucas 1:53, como Deus trata os famintos e os ricos?",
     "opcao_a": "Enche de bens os famintos e despede os ricos de mãos vazias", "opcao_b": "Enche de bens os ricos e deixa os famintos com fome", "opcao_c": "Ignora ambos", "opcao_d": "Tira dos famintos e dá aos ricos",
     "resposta_correta": "A", "referencia": "Lucas 1:53"},
    {"enunciado": "Segundo Lucas 1:54-55, a quem Deus acolheu lembrando-se de sua misericórdia e das promessas feitas aos antepassados?",
     "opcao_a": "A Israel, seu servo, conforme prometera a Abraão e à sua descendência para sempre", "opcao_b": "Aos egípcios", "opcao_c": "Aos romanos", "opcao_d": "Aos filisteus",
     "resposta_correta": "A", "referencia": "Lucas 1:54-55"},
    {"enunciado": "Quanto tempo Maria permaneceu com Isabel antes de voltar para sua casa (v. 56)?",
     "opcao_a": "Cerca de três meses", "opcao_b": "Três dias", "opcao_c": "Um ano", "opcao_d": "Uma semana",
     "resposta_correta": "A", "referencia": "Lucas 1:56"},
    {"enunciado": "Quem escreveu a maior parte das cartas (epístolas) do Novo Testamento?",
     "opcao_a": "Paulo", "opcao_b": "Pedro", "opcao_c": "João", "opcao_d": "Tiago",
     "resposta_correta": "A", "referencia": "Novo Testamento"},
    {"enunciado": "Quantos evangelhos existem no Novo Testamento?",
     "opcao_a": "4", "opcao_b": "3", "opcao_c": "5", "opcao_d": "2",
     "resposta_correta": "A", "referencia": "Novo Testamento"},
    {"enunciado": "Qual é o primeiro livro da Bíblia?",
     "opcao_a": "Gênesis", "opcao_b": "Êxodo", "opcao_c": "Salmos", "opcao_d": "Mateus",
     "resposta_correta": "A", "referencia": "Gênesis 1:1"},
    {"enunciado": "Qual é o último livro da Bíblia?",
     "opcao_a": "Apocalipse", "opcao_b": "Judas", "opcao_c": "Apocalipse", "opcao_d": "Malaquias",
     "resposta_correta": "A", "referencia": "Apocalipse 22:21"},
    {"enunciado": "Em que cidade Jesus nasceu?",
     "opcao_a": "Belém", "opcao_b": "Nazaré", "opcao_c": "Jerusalém", "opcao_d": "Jericho",
     "resposta_correta": "A", "referencia": "Lucas 2:4-7"},
    {"enunciado": "Quantos discípulos (apóstolos) Jesus escolheu?",
     "opcao_a": "12", "opcao_b": "10", "opcao_c": "70", "opcao_d": "7",
     "resposta_correta": "A", "referencia": "Mateus 10:1-4"},
    {"enunciado": "Quem negou Jesus três vezes antes do galo cantar?",
     "opcao_a": "Pedro", "opcao_b": "Judas", "opcao_c": "Tomé", "opcao_d": "João",
     "resposta_correta": "A", "referencia": "Lucas 22:54-62"},
    {"enunciado": "Qual apóstolo duvidou da ressurreição até ver as marcas dos pregos?",
     "opcao_a": "Tomé", "opcao_b": "Pedro", "opcao_c": "André", "opcao_d": "Felipe",
     "resposta_correta": "A", "referencia": "João 20:24-29"},
    {"enunciado": "Qual é o mandamento maior segundo Jesus?",
     "opcao_a": "Amar a Deus sobre todas as coisas e ao próximo como a si mesmo", "opcao_b": "Guardar o sábado", "opcao_c": "Dizimar tudo", "opcao_d": "Fazer peregrinação",
     "resposta_correta": "A", "referencia": "Mateus 22:37-39"},
    {"enunciado": "Quem foi a primeira mulher criada por Deus?",
     "opcao_a": "Eva", "opcao_b": "Maria", "opcao_c": "Sara", "opcao_d": "Raquel",
     "resposta_correta": "A", "referencia": "Gênesis 2:22"},
    {"enunciado": "Quem liderou o povo de Israel na saída do Egito?",
     "opcao_a": "Moisés", "opcao_b": "Aarão", "opcao_c": "Josué", "opcao_d": "Abraão",
     "resposta_correta": "A", "referencia": "Êxodo 3:10"},
    {"enunciado": "Quantos dias e noites Jesus jejuou no deserto?",
     "opcao_a": "40", "opcao_b": "30", "opcao_c": "7", "opcao_d": "14",
     "resposta_correta": "A", "referencia": "Mateus 4:1-2"},
    {"enunciado": "Em que rio Jesus foi batizado por João Batista?",
     "opcao_a": "Rio Jordão", "opcao_b": "Rio Nilo", "opcao_c": "Rio Tigre", "opcao_d": "Rio Eufrates",
     "resposta_correta": "A", "referencia": "Mateus 3:13-17"},
    {"enunciado": "Qual foi o primeiro milagre de Jesus registrado na Bíblia?",
     "opcao_a": "Transformar água em vinho em Caná", "opcao_b": "Curar um cego", "opcao_c": "Multiplicar pães", "opcao_d": "Andar sobre as águas",
     "resposta_correta": "A", "referencia": "João 2:1-11"},
    {"enunciado": "Quem traiu Jesus por trinta moedas de prata?",
     "opcao_a": "Judas Iscariotes", "opcao_b": "Pedro", "opcao_c": "Caifás", "opcao_d": "Herodes",
     "resposta_correta": "A", "referencia": "Mateus 26:14-16"},
    {"enunciado": "Qual é o verso mais conhecido da Bíblia (João 3:16)?",
     "opcao_a": "Porque Deus amou o mundo de tal maneira que deu o Seu Filho unigênito", "opcao_b": "No princípio criou Deus os céus e a terra", "opcao_c": "O Senhor é o meu pastor", "opcao_d": "Não terás outros deuses",
     "resposta_correta": "A", "referencia": "João 3:16"},
    {"enunciado": "Quem foi lançado na cova dos leões e foi protegido por Deus?",
     "opcao_a": "Daniel", "opcao_b": "Jó", "opcao_c": "José", "opcao_d": "Jonas",
     "resposta_correta": "A", "referencia": "Daniel 6"},
    {"enunciado": "Quem foi engolido por um grande peixe por desobedecer a Deus?",
     "opcao_a": "Jonas", "opcao_b": "Daniel", "opcao_c": "Pedro", "opcao_d": "Paulo",
     "resposta_correta": "A", "referencia": "Jonas 1:17"},
    {"enunciado": "Qual é o fruto do Espírito listado em Gálatas 5:22-23 que começa com 'A'?",
     "opcao_a": "Amor", "opcao_b": "Aleluia", "opcao_c": "Arrependimento", "opcao_d": "Arqueta",
     "resposta_correta": "A", "referencia": "Gálatas 5:22-23"},
    {"enunciado": "Quem interpretou os sonhos do faraó no Egito?",
     "opcao_a": "José", "opcao_b": "Moisés", "opcao_c": "Daniel", "opcao_d": "Samuel",
     "resposta_correta": "A", "referencia": "Gênesis 41"},
    {"enunciado": "Quem morreu e foi ressuscitado por Jesus quatro dias após a morte?",
     "opcao_a": "Lázaro", "opcao_b": "Jairo", "opcao_c": "Tabita", "opcao_d": "Estêvão",
     "resposta_correta": "A", "referencia": "João 11"},
    {"enunciado": "Quem foi o primeiro mártir cristão?",
     "opcao_a": "Estêvão", "opcao_b": "Tiago", "opcao_c": "Pedro", "opcao_d": "Paulo",
     "resposta_correta": "A", "referencia": "Atos 7:54-60"},
    {"enunciado": "Em que cidade o Espírito Santo desceu sobre os apóstolos no dia de Pentecostes?",
     "opcao_a": "Jerusalém", "opcao_b": "Antioquia", "opcao_c": "Roma", "opcao_d": "Éfeso",
     "resposta_correta": "A", "referencia": "Atos 2:1-4"},
    {"enunciado": "Quem escreveu o livro de Apocalipse?",
     "opcao_a": "João", "opcao_b": "Paulo", "opcao_c": "Pedro", "opcao_d": "Marcos",
     "resposta_correta": "A", "referencia": "Apocalipse 1:1"},
    {"enunciado": "Qual profeta foi levado ao céu em um carro de fogo?",
     "opcao_a": "Elias", "opcao_b": "Eliseu", "opcao_c": "Isaías", "opcao_d": "Jeremias",
     "resposta_correta": "A", "referencia": "2 Reis 2:11"},
    {"enunciado": "Quem foi o primeiro rei de Israel?",
     "opcao_a": "Saul", "opcao_b": "Davi", "opcao_c": "Salomão", "opcao_d": "Samuel",
     "resposta_correta": "A", "referencia": "1 Samuel 9-10"},
    {"enunciado": "Quem foi o rei conhecido pela sabedoria e que construiu o templo?",
     "opcao_a": "Salomão", "opcao_b": "Davi", "opcao_c": "Ezequias", "opcao_d": "Josias",
     "resposta_correta": "A", "referencia": "1 Reis 3-8"},
    {"enunciado": "Qual é o livro bíblico que contém principalmente canções e orações?",
     "opcao_a": "Salmos", "opcao_b": "Provérbios", "opcao_c": "Eclesiastes", "opcao_d": "Jó",
     "resposta_correta": "A", "referencia": "Salmos"},
    {"enunciado": "Quem foi lançado na fornalha de fogo ardente com dois amigos?",
     "opcao_a": "Daniel (e Sadraque, Mesaque e Abede-Nego)", "opcao_b": "José", "opcao_c": "Moisés", "opcao_d": "Josué",
     "resposta_correta": "A", "referencia": "Daniel 3"},
    {"enunciado": "Qual discípulo era coletor de impostos antes de seguir Jesus?",
     "opcao_a": "Mateus", "opcao_b": "Pedro", "opcao_c": "Tiago", "opcao_d": "André",
     "resposta_correta": "A", "referencia": "Mateus 9:9"},
    {"enunciado": "Quem foi a mãe de Jesus?",
     "opcao_a": "Maria", "opcao_b": "Isabel", "opcao_c": "Marta", "opcao_d": "Maria Madalena",
     "resposta_correta": "A", "referencia": "Lucas 1:26-38"},
    {"enunciado": "Quem foi o pai terreno de Jesus?",
     "opcao_a": "José", "opcao_b": "Zacarias", "opcao_c": "Joachim", "opcao_d": "Deus (pai celestial)",
     "resposta_correta": "D", "referencia": "Mateus 1:18-25"},
    {"enunciado": "Qual anjo anunciou a Maria que ela seria mãe de Jesus?",
     "opcao_a": "Gabriel", "opcao_b": "Miguel", "opcao_c": "Lucas", "opcao_d": "Rafael",
     "resposta_correta": "A", "referencia": "Lucas 1:26-38"},
    {"enunciado": "Quantos dias Jesus permaneceu na terra após a ressurreição antes de subir ao céu?",
     "opcao_a": "40", "opcao_b": "3", "opcao_c": "7", "opcao_d": "12",
     "resposta_correta": "A", "referencia": "Atos 1:3"},
    {"enunciado": "Qual é a última palavra da Bíblia?",
     "opcao_a": "Amém", "opcao_b": "Graça", "opcao_c": "Jesus", "opcao_d": "Fim",
     "resposta_correta": "A", "referencia": "Apocalipse 22:21"},
    {"enunciado": "Quem escreveu o Salmo 23 ('O Senhor é o meu pastor')?",
     "opcao_a": "Davi", "opcao_b": "Moisés", "opcao_c": "Salomão", "opcao_d": "Asafe",
     "resposta_correta": "A", "referencia": "Salmo 23"},
    {"enunciado": "Qual profeta foi comido por um grande peixe depois de fugir de Deus?",
     "opcao_a": "Jonas", "opcao_b": "Jeremias", "opcao_c": "Isaías", "opcao_d": "Ezequiel",
     "resposta_correta": "A", "referencia": "Jonas 1-2"},
    {"enunciado": "Quem foi o primeiro homem criado por Deus?",
     "opcao_a": "Adão", "opcao_b": "Noé", "opcao_c": "Abraão", "opcao_d": "Abel",
     "resposta_correta": "A", "referencia": "Gênesis 2:7"},
    {"enunciado": "Qual foi o primeiro filho de Adão e Eva?",
     "opcao_a": "Caim", "opcao_b": "Abel", "opcao_c": "Sete", "opcao_d": "Enos",
     "resposta_correta": "A", "referencia": "Gênesis 4:1"},
    {"enunciado": "Quem construiu a arca para sobreviver ao dilúvio?",
     "opcao_a": "Noé", "opcao_b": "Abraão", "opcao_c": "Moisés", "opcao_d": "Josué",
     "resposta_correta": "A", "referencia": "Gênesis 6-9"},
    {"enunciado": "Quantas pessoas da família de Noé entraram na arca?",
     "opcao_a": "8", "opcao_b": "4", "opcao_c": "6", "opcao_d": "12",
     "resposta_correta": "A", "referencia": "1 Pedro 3:20"},
    {"enunciado": "Quem foi chamado de 'amigo de Deus'?",
     "opcao_a": "Abraão", "opcao_b": "Moisés", "opcao_c": "Davi", "opcao_d": "Jó",
     "resposta_correta": "A", "referencia": "Tiago 2:23"},
    {"enunciado": "Qual é o significado do nome 'Jesus'?",
     "opcao_a": "Deus salva", "opcao_b": "Deus está conosco", "opcao_c": "Messias", "opcao_d": "Salvador do mundo",
     "resposta_correta": "A", "referencia": "Mateus 1:21"},
    {"enunciado": "Quem foi o sumo sacerdote que interrogou Jesus?",
     "opcao_a": "Caifás", "opcao_b": "Anás", "opcao_c": "Herodes", "opcao_d": "Pilatos",
     "resposta_correta": "A", "referencia": "Mateus 26:57"},
    {"enunciado": "Quem lavou os pés dos discípulos na Última Ceia?",
     "opcao_a": "Jesus", "opcao_b": "Pedro", "opcao_c": "João", "opcao_d": "Um servo",
     "resposta_correta": "A", "referencia": "João 13:1-17"},
    {"enunciado": "Qual é o livro do Novo Testamento que começa com 'No princípio era o Verbo'?",
     "opcao_a": "João", "opcao_b": "Mateus", "opcao_c": "Lucas", "opcao_d": "Marcos",
     "resposta_correta": "A", "referencia": "João 1:1"},
    {"enunciado": "Quem foi a mulher de Abraão?",
     "opcao_a": "Sara", "opcao_b": "Raquel", "opcao_c": "Rebeca", "opcao_d": "Lia",
     "resposta_correta": "A", "referencia": "Gênesis 17:15-19"},
    {"enunciado": "Qual foi o filho da promessa de Abraão e Sara?",
     "opcao_a": "Isaque", "opcao_b": "Ismael", "opcao_c": "Jacó", "opcao_d": "Esaú",
     "resposta_correta": "A", "referencia": "Gênesis 21:1-3"},
    {"enunciado": "Quem vendeu seu primogenitura por um prato de lentilhas?",
     "opcao_a": "Esaú", "opcao_b": "Jacó", "opcao_c": "Isaque", "opcao_d": "Judá",
     "resposta_correta": "A", "referencia": "Gênesis 25:29-34"},
    {"enunciado": "Qual é o nome da esposa de Jacó que ele amava mais?",
     "opcao_a": "Raquel", "opcao_b": "Lia", "opcao_c": "Zilpa", "opcao_d": "Bilha",
     "resposta_correta": "A", "referencia": "Gênesis 29:18-30"},
    {"enunciado": "Quem interpretou a escrita na parede no banquete de Belsazar?",
     "opcao_a": "Daniel", "opcao_b": "Ezequiel", "opcao_c": "Jeremias", "opcao_d": "Isaías",
     "resposta_correta": "A", "referencia": "Daniel 5"},
    {"enunciado": "Qual profeta profetizou o nascimento de Jesus em Belém?",
     "opcao_a": "Miqueias", "opcao_b": "Isaías", "opcao_c": "Jeremias", "opcao_d": "Oseias",
     "resposta_correta": "A", "referencia": "Miqueias 5:2"},
    {"enunciado": "Quem foi o escriba que copiou e preservou a Lei após o exílio?",
     "opcao_a": "Esdras", "opcao_b": "Neemias", "opcao_c": "Malaquias", "opcao_d": "Zacarias",
     "resposta_correta": "A", "referencia": "Esdras 7:6"},
    {"enunciado": "Quem reconstruiu os muros de Jerusalém?",
     "opcao_a": "Neemias", "opcao_b": "Esdras", "opcao_c": "Zorobabel", "opcao_d": "Josué",
     "resposta_correta": "A", "referencia": "Neemias 2-6"},
    {"enunciado": "Qual é o significado de 'Messias'?",
     "opcao_a": "O ungido", "opcao_b": "O rei", "opcao_c": "O profeta", "opcao_d": "O sacerdote",
     "resposta_correta": "A", "referencia": "João 1:41"},
    {"enunciado": "Quem batizou Jesus?",
     "opcao_a": "João Batista", "opcao_b": "Pedro", "opcao_c": "João (apóstolo)", "opcao_d": "Jesus mesmo",
     "resposta_correta": "A", "referencia": "Mateus 3:13-17"},
    {"enunciado": "Quantas vezes Pedro negou Jesus?",
     "opcao_a": "3", "opcao_b": "1", "opcao_c": "7", "opcao_d": "12",
     "resposta_correta": "A", "referencia": "Lucas 22:54-62"},
    {"enunciado": "Qual é o nome do lugar onde Jesus foi crucificado?",
     "opcao_a": "Gólgota (Calvário)", "opcao_b": "Betenita", "opcao_c": "Monte Sião", "opcao_d": "Monte das Oliveiras",
     "resposta_correta": "A", "referencia": "João 19:17"},
    {"enunciado": "Quem ajudou Jesus a carregar a cruz?",
     "opcao_a": "Simão de Cirene", "opcao_b": "Pedro", "opcao_c": "José de Arimateia", "opcao_d": "Nicodemos",
     "resposta_correta": "A", "referencia": "Mateus 27:32"},
    {"enunciado": "Quem pediu o corpo de Jesus a Pilatos para sepultá-lo?",
     "opcao_a": "José de Arimateia", "opcao_b": "Nicodemos", "opcao_c": "Simão de Cirene", "opcao_d": "Maria Madalena",
     "resposta_correta": "A", "referencia": "Mateus 27:57-60"},
    {"enunciado": "Qual foi a primeira pessoa a ver Jesus ressuscitado?",
     "opcao_a": "Maria Madalena", "opcao_b": "Pedro", "opcao_c": "João", "opcao_d": "Maria, mãe de Jesus",
     "resposta_correta": "A", "referencia": "João 20:11-18"},
    {"enunciado": "Quem escreveu os Atos dos Apóstolos?",
     "opcao_a": "Lucas", "opcao_b": "Paulo", "opcao_c": "Pedro", "opcao_d": "João",
     "resposta_correta": "A", "referencia": "Atos 1:1"},
    {"enunciado": "Qual é o versículo que diz 'todas as coisas cooperam para o bem'?",
     "opcao_a": "Romanos 8:28", "opcao_b": "Filipenses 4:13", "opcao_c": "Salmo 23:1", "opcao_d": "João 14:6",
     "resposta_correta": "A", "referencia": "Romanos 8:28"},
    {"enunciado": "Quem foi apedrejado até a morte enquanto via os céus abertos e Jesus à direita de Deus?",
     "opcao_a": "Estêvão", "opcao_b": "Tiago", "opcao_c": "Paulo", "opcao_d": "Pedro",
     "resposta_correta": "A", "referencia": "Atos 7:55-60"},
    {"enunciado": "Qual é o fruto do Espírito que significa domínio próprio?",
     "opcao_a": "Domínio próprio", "opcao_b": "Aleluia", "opcao_c": "Certeza", "opcao_d": "Fé",
     "resposta_correta": "A", "referencia": "Gálatas 5:22-23"},
    {"enunciado": "Quem escreveu a maior parte dos Salmos?",
     "opcao_a": "Davi", "opcao_b": "Salomão", "opcao_c": "Moisés", "opcao_d": "Asafe",
     "resposta_correta": "A", "referencia": "Salmos"},
    {"enunciado": "Qual é o nome do anjo que anunciou o nascimento de João Batista a Zacarias?",
     "opcao_a": "Gabriel", "opcao_b": "Miguel", "opcao_c": "Uriel", "opcao_d": "Rafael",
     "resposta_correta": "A", "referencia": "Lucas 1:11-20"},
    {"enunciado": "Quem foi o pai de João Batista?",
     "opcao_a": "Zacarias", "opcao_b": "José", "opcao_c": "Herodes", "opcao_d": "Eli",
     "resposta_correta": "A", "referencia": "Lucas 1:5-25"},
    {"enunciado": "Qual é o significado de 'Emmanuel'?",
     "opcao_a": "Deus conosco", "opcao_b": "Deus salva", "opcao_c": "O ungido", "opcao_d": "Senhor dos exércitos",
     "resposta_correta": "A", "referencia": "Mateus 1:23"},
    {"enunciado": "Quem disse 'Eis aqui a serva do Senhor; faça-se em mim segundo a tua palavra'?",
     "opcao_a": "Maria", "opcao_b": "Isabel", "opcao_c": "Ana", "opcao_d": "Débora",
     "resposta_correta": "A", "referencia": "Lucas 1:38"},
    {"enunciado": "Qual é o nome da sogra de Rute?",
     "opcao_a": "Noemi", "opcao_b": "Rut", "opcao_c": "Orfa", "opcao_d": "Débora",
     "resposta_correta": "A", "referencia": "Rute 1"},
    {"enunciado": "Quem foi a juíza e profetisa de Israel?",
     "opcao_a": "Débora", "opcao_b": "Rute", "opcao_c": "Ester", "opcao_d": "Miriã",
     "resposta_correta": "A", "referencia": "Juízes 4-5"},
    {"enunciado": "Qual rainha arriscou a vida para salvar seu povo na Pérsia?",
     "opcao_a": "Ester", "opcao_b": "Vasti", "opcao_c": "Bate-Seba", "opcao_d": "Débora",
     "resposta_correta": "A", "referencia": "Ester 4-7"},
    {"enunciado": "Quem foi o profeta que confrontou o rei Acabe e os profetas de Baal?",
     "opcao_a": "Elias", "opcao_b": "Eliseu", "opcao_c": "Samuel", "opcao_d": "Isaías",
     "resposta_correta": "A", "referencia": "1 Reis 18"},
    {"enunciado": "Qual é o menor livro do Antigo Testamento?",
     "opcao_a": "Obadias", "opcao_b": "Jonas", "opcao_c": "Ageu", "opcao_d": "Malaquias",
     "resposta_correta": "A", "referencia": "Obadias"},
    {"enunciado": "Quem foi o faraó que não conhecia José e escravizou Israel?",
     "opcao_a": "Um novo faraó sobre o Egito", "opcao_b": "Faraó Necao", "opcao_c": "Faraó Tutancâmon", "opcao_d": "Faraó Ramsés",
     "resposta_correta": "A", "referencia": "Êxodo 1:8"},
    {"enunciado": "Qual é o nome do maná que Deus deu no deserto?",
     "opcao_a": "Maná", "opcao_b": "Pão do céu", "opcao_c": "Quinua", "opcao_d": "Manna",
     "resposta_correta": "A", "referencia": "Êxodo 16"},
]
# ---------------------------------------------------------------------------
# INICIALIZAÇÃO DO BANCO E SEED
# ---------------------------------------------------------------------------
def init_db():
    with app.app_context():
        db.create_all()
        if Pergunta.query.count() == 0:
            for p in PERGUNTAS_SEED:
                db.session.add(Pergunta(**p))
            db.session.commit()
            print(f"Seed de {len(PERGUNTAS_SEED)} perguntas inserido.")


# ---------------------------------------------------------------------------
# ROTAS
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    session.clear()
    session['indice'] = 0
    session['pontuacao'] = 0
    total = Pergunta.query.count()
    return render_template('index.html', total=total)


@app.route('/quiz')
def quiz():
    indice = session.get('indice', 0)
    pontuacao = session.get('pontuacao', 0)
    pergunta = Pergunta.query.offset(indice).first()
    if not pergunta:
        return redirect(url_for('gameover'))
    total = Pergunta.query.count()
    return render_template('quiz.html', pergunta=pergunta, indice=indice + 1,
                           total=total, pontuacao=pontuacao)


@app.route('/responder', methods=['POST'])
def responder():
    resposta = request.form.get('resposta')
    indice = session.get('indice', 0)
    pontuacao = session.get('pontuacao', 0)
    pergunta = Pergunta.query.offset(indice).first()

    if not pergunta:
        return redirect(url_for('gameover'))

    correta = (resposta == pergunta.resposta_correta)

    if correta:
        pontuacao += 1
        session['pontuacao'] = pontuacao
        session['indice'] = indice + 1
        return redirect(url_for('quiz'))
    else:
        return redirect(url_for('gameover', pontuacao=pontuacao))


@app.route('/gameover')
def gameover():
    pontuacao = request.args.get('pontuacao', session.get('pontuacao', 0))
    try:
        pontuacao = int(pontuacao)
    except ValueError:
        pontuacao = 0
    session['pontuacao_final'] = pontuacao
    return render_template('gameover.html', pontuacao=pontuacao)


@app.route('/salvar', methods=['POST'])
def salvar():
    nome = request.form.get('nome', 'Anônimo').strip() or 'Anônimo'
    pontuacao = session.get('pontuacao_final', 0)
    placar = Placar(nome=nome, pontuacao=pontuacao)
    db.session.add(placar)
    db.session.commit()
    return redirect(url_for('ranking'))


@app.route('/ranking')
def ranking():
    tops = Placar.query.order_by(Placar.pontuacao.desc(), Placar.data.asc()).limit(10).all()
    return render_template('ranking.html', tops=tops)


@app.route('/api/pergunta/<int:indice>')
def api_pergunta(indice):
    p = Pergunta.query.offset(indice).first()
    if not p:
        return jsonify({'fim': True})
    return jsonify({
        'id': p.id,
        'enunciado': p.enunciado,
        'opcoes': {
            'A': p.opcao_a,
            'B': p.opcao_b,
            'C': p.opcao_c,
            'D': p.opcao_d,
        },
        'referencia': p.referencia
    })


if __name__ == '__main__':
    init_db()
    app.run(debug=True)