# Banco de Dados da Oficina
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config_email import EMAIL_CONFIG

# Função para criar o banco de dados
def criar_tabela():
    with sqlite3.connect("oficina.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                nome TEXT,
                contato TEXT,
                carro TEXT,
                placa TEXT PRIMARY KEY,
                status TEXT
            )
        """)

# Função para cadastrar um novo cliente
def cadastrar_cliente():
    nome = input("Digite o nome do cliente: ")
    contato = input("Digite o e-mail do cliente: ")
    carro = input("Digite o nome do carro: ")
    placa = input("Digite a placa do carro: ")
    status = "Na fila"

    with sqlite3.connect("oficina.db") as conn:
        try:
            conn.execute("""
                INSERT INTO clientes (nome, contato, carro, placa, status)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, contato, carro, placa, status))
            conn.commit()
            print("Cliente cadastrado com sucesso!")
        except sqlite3.IntegrityError:
            print("Erro: Já existe um cliente com essa placa.")

# Função para consultar todos os clientes cadastrados
def consultar_clientes():
    cont=0
    with sqlite3.connect("oficina.db") as conn:
        for linha in conn.execute("SELECT * FROM clientes"):
            if linha[4] == "Concluído":
                continue
            print(f"Nome: {linha[0]}")
            print(f"Contato: {linha[1]}")
            print(f"Carro: {linha[2]}")
            print(f"Placa: {linha[3]}")
            print(f"Status: {linha[4]}")
            print("-----------------------------")
            cont+=1
    if cont==0:
        print("Nenhum cliente na fila ou em processo.")

# Função para alterar o status de um cliente
def alterar_status():
    placa = input("Digite a placa do carro para alterar o status: ")

    with sqlite3.connect("oficina.db") as conn:
        cursor = conn.execute("SELECT * FROM clientes WHERE placa = ?", (placa,))
        cliente = cursor.fetchone()

        if cliente:
            status = input("Qual o novo status? (1- Na fila, 2- Trabalhando nele, 3- Concluído): ")
            if status == "1":
                novo_status = "Na fila"
            elif status == "2":
                novo_status = "Em processo"
            elif status == "3":
                novo_status = "Concluído"
            else:
                print("Opção inválida.")
                return

            conn.execute("UPDATE clientes SET status = ? WHERE placa = ?", (novo_status, placa))
            conn.commit()

            enviar_notificacao(cliente[1], f"Seu veículo está: {novo_status}")
            print("Status alterado com sucesso!")
        else:
            print("Cliente não encontrado.")

# Função para enviar notificação ao cliente (via e-mail)
def enviar_notificacao(contato, mensagem):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["email_usuario"]
        msg['To'] = contato
        msg['Subject'] = f"Atualização do Serviço - {EMAIL_CONFIG['nome_oficina']}"

        corpo_email = f"""
        Opa! Tudo bem? Oficina Fubika aqui!

        Só passando pra avisar que o status do seu veículo foi atualizado:

        {mensagem}

        Qualquer dúvida que tiver, é só nos chamar!

        Atenciosamente,
        Equipe do {EMAIL_CONFIG['nome_oficina']}
        """

        msg.attach(MIMEText(corpo_email, 'plain'))

        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["email_usuario"], EMAIL_CONFIG["email_senha"])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG["email_usuario"], contato, text)
        server.quit()

        print(f"Email enviado com sucesso para {contato}")
        return True

    except Exception as e:
        print(f"Erro ao enviar email para {contato}: {str(e)}")
        print("Verifique suas configurações de email no arquivo config_email.py")
        return False

# Loop principal do menu
def menu():
    criar_tabela()
    while True:
        print("---"*20)
        print("\n1 - Cadastrar cliente")
        print("2 - Consultar clientes")
        print("3 - Alterar status")
        print("4 - Sair")
        opcao = input("Escolha uma opção: ")
        print("---"*20) # Linha divisória para melhorar a visualização

        if opcao == "1":
            cadastrar_cliente()
        elif opcao == "2":
            consultar_clientes()
        elif opcao == "3":
            alterar_status()
        elif opcao == "4":
            print("Encerrando o sistema.")
            break
        else:
            print("Opção inválida.")

menu()
