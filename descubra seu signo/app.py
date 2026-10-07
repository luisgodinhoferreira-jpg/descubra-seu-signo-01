import sqlite3
from datetime import datetime, timezone, timedelta

# ==========================================
# CONFIGURAÇÃO DE FUSO HORÁRIO (BRASIL)
# ==========================================
# Cria o fuso horário de Brasília (UTC-3)
FUSO_BRASIL = timezone(timedelta(hours=-3))

# ==========================================
# CONFIGURAÇÃO DO BANCO
# ==========================================
DB_NAME = "signos.db"

def conectar():
    return sqlite3.connect(DB_NAME, timeout=10)

def obter_horario_brasil():
    """Retorna a data e hora atual no fuso horário do Brasil."""
    return datetime.now(FUSO_BRASIL).strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# CRIAÇÃO E POPULAÇÃO DO BANCO
# ==========================================
def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    # 1. TABELAS (SEM o DEFAULT CURRENT_TIMESTAMP)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(30),
            data_nascimento DATE,
            email VARCHAR(50),
            data_cadastro DATETIME
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signo (
            id_signo INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_signo VARCHAR(30),
            dia_inicio INTEGER,
            mes_inicio INTEGER,
            dia_fim INTEGER,
            mes_fim INTEGER,
            elemento VARCHAR(20),
            planeta_regente VARCHAR(20)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caracteristica (
            id_caracteristica INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT,
            tipo VARCHAR(30),
            id_signo INTEGER,
            FOREIGN KEY (id_signo) REFERENCES signo(id_signo)
        )
    """)

    # 2. POPULA SE ESTIVER VAZIO
    cursor.execute("SELECT COUNT(*) FROM signo")
    if cursor.fetchone()[0] == 0:
        print("🌱 Populando banco de dados pela primeira vez...")

        signos = [
            ('Áries', 21, 3, 19, 4, 'Fogo', 'Marte'),
            ('Touro', 20, 4, 20, 5, 'Terra', 'Vênus'),
            ('Gêmeos', 21, 5, 20, 6, 'Ar', 'Mercúrio'),
            ('Câncer', 21, 6, 22, 7, 'Água', 'Lua'),
            ('Leão', 23, 7, 22, 8, 'Fogo', 'Sol'),
            ('Virgem', 23, 8, 22, 9, 'Terra', 'Mercúrio'),
            ('Libra', 23, 9, 22, 10, 'Ar', 'Vênus'),
            ('Escorpião', 23, 10, 21, 11, 'Água', 'Plutão'),
            ('Sagitário', 22, 11, 21, 12, 'Fogo', 'Júpiter'),
            ('Capricórnio', 22, 12, 19, 1, 'Terra', 'Saturno'),
            ('Aquário', 20, 1, 18, 2, 'Ar', 'Urano'),
            ('Peixes', 19, 2, 20, 3, 'Água', 'Netuno')
        ]
        cursor.executemany("""
            INSERT INTO signo (nome_signo, dia_inicio, mes_inicio, dia_fim, mes_fim, elemento, planeta_regente) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, signos)

        caracteristicas = [
            ('Corajoso, aventureiro e impulsivo.', 'Personalidade', 1),
            ('Paciente, persistente e confiável.', 'Personalidade', 2),
            ('Comunicativo, curioso e ágil.', 'Personalidade', 3),
            ('Emotivo, protetor e intuitivo.', 'Personalidade', 4),
            ('Carismático, líder e criativo.', 'Personalidade', 5),
            ('Analítico, perfeccionista e detalhista.', 'Personalidade', 6),
            ('Diplomático, sociável e busca equilíbrio.', 'Personalidade', 7),
            ('Intenso, misterioso e determinado.', 'Personalidade', 8),
            ('Otimista, explorador e filosófico.', 'Personalidade', 9),
            ('Disciplinado, ambicioso e responsável.', 'Personalidade', 10),
            ('Independente, original e humanitário.', 'Personalidade', 11),
            ('Empático, sonhador e artístico.', 'Personalidade', 12)
        ]
        cursor.executemany("""
            INSERT INTO caracteristica (descricao, tipo, id_signo) 
            VALUES (?, ?, ?)
        """, caracteristicas)

        conn.commit()
        print("✅ Banco populado com sucesso!\n")

    conn.close()

# ==========================================
# LÓGICA DE DESCOBRIR O SIGNO
# ==========================================
def descobrir_signo(dia, mes):
    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT s.nome_signo, s.elemento, s.planeta_regente, c.descricao 
        FROM signo s
        JOIN caracteristica c ON s.id_signo = c.id_signo
        WHERE 
            (s.mes_inicio = ? AND s.dia_inicio <= ?)
            OR
            (s.mes_fim = ? AND s.dia_fim >= ?)
            OR
            (s.mes_inicio < s.mes_fim AND ? > s.mes_inicio AND ? < s.mes_fim)
            OR
            (s.nome_signo = 'Capricórnio' AND (
                (? = 12 AND ? >= 22) OR
                (? = 1 AND ? <= 19)
            ))
    """
    parametros = (mes, dia, mes, dia, mes, mes, mes, dia, mes, dia)
    cursor.execute(query, parametros)
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# ==========================================
# CADASTRO DO USUÁRIO
# ==========================================
def cadastrar_usuario():
    print("=" * 45)
    print("   🔮 DESCOBRA O SEU SIGNO 🔮")
    print("=" * 45)

    nome = input("Digite seu nome: ")
    email = input("Digite seu email: ")

    while True:
        try:
            data_str = input("Digite sua data de nascimento (DD/MM/AAAA): ")
            dia, mes, ano = map(int, data_str.split('/'))
            if 1 <= dia <= 31 and 1 <= mes <= 12 and ano > 1900:
                break
            else:
                print("⚠️ Data inválida. Tente novamente.")
        except ValueError:
            print("⚠️ Formato inválido. Use DD/MM/AAAA (ex: 15/08/2000).")

    # SALVA NO BANCO COM O HORÁRIO DO BRASIL
    conn = conectar()
    cursor = conn.cursor()
    data_formatada = f"{ano}-{mes:02d}-{dia:02d}"
    
    # Pega o horário exato de Brasília (UTC-3)
    horario_brasil = obter_horario_brasil()
    
    cursor.execute("""
        INSERT INTO usuario (nome, data_nascimento, email, data_cadastro) 
        VALUES (?, ?, ?, ?)
    """, (nome, data_formatada, email, horario_brasil))
    conn.commit()
    conn.close()

    print("\n✅ Usuário salvo no banco de dados 'signos.db'!")
    print(f"🕒 Horário do cadastro (Brasília): {horario_brasil}")

    # DESCOBRE O SIGNO
    resultado = descobrir_signo(dia, mes)

    print("\n" + "=" * 45)
    print(f"   RESULTADO PARA {nome.upper()}")
    print("=" * 45)

    if resultado:
        nome_signo, elemento, planeta, descricao = resultado
        print(f"✨ Signo: {nome_signo}")
        print(f"🔥 Elemento: {elemento}")
        print(f"🪐 Planeta Regente: {planeta}")
        print(f"📝 Característica: {descricao}")
    else:
        print("❌ Não foi possível determinar o signo.")

    print("=" * 45)

# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================
if __name__ == "__main__":
    inicializar_banco()

    while True:
        cadastrar_usuario()
        continuar = input("\nDeseja cadastrar outro usuário? (s/n): ").lower()
        if continuar != 's':
            print("\n👋 Encerrando o programa. Até logo!")
            break