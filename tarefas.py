import json
import os
import platform
from datetime import datetime

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Instale a biblioteca colorama para usar cores:")
    print("pip install colorama")
    exit()

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
except ImportError:
    print("Instale prompt_toolkit para usar autocomplete:")
    print("pip install prompt_toolkit")
    exit()

ARQUIVO_TAREFAS = "tarefas.json"
PASTA_BACKUP = "backups"
tarefas = []

COMANDOS = [
    "dir", "dir done", "dir pending", "add", "done", "undone", "del",
    "hist", "edit hist", "addhist", "backup export", "backup import", 
    "clear", "cls", "help", "exit"
]

# ---------- Funções de backup ----------
def exportar_backup():
    if not os.path.exists(PASTA_BACKUP):
        os.makedirs(PASTA_BACKUP)
    nome_arquivo = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    caminho = os.path.join(PASTA_BACKUP, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)
    print(Fore.GREEN + f"Backup exportado: {caminho}")

def importar_backup(nome_arquivo):
    global tarefas
    caminho = os.path.join(PASTA_BACKUP, nome_arquivo)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            tarefas = json.load(f)
        salvar_tarefas_local()
        print(Fore.GREEN + f"Backup importado: {caminho}")
    else:
        print(Fore.RED + f"Arquivo de backup não encontrado: {caminho}")

def importar_ultimo_backup():
    """Importa automaticamente o backup mais recente, se existir"""
    if not os.path.exists(PASTA_BACKUP):
        return
    backups = [f for f in os.listdir(PASTA_BACKUP) if f.endswith(".json")]
    if not backups:
        return
    backups.sort(reverse=True)  # O mais recente primeiro
    importar_backup(backups[0])

# ---------- Funções básicas ----------
def carregar_tarefas():
    global tarefas
    if os.path.exists(ARQUIVO_TAREFAS):
        with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
            tarefas = json.load(f)
    else:
        tarefas = []

def salvar_tarefas_local(_tarefas=None):
    """Salva o arquivo de tarefas sem gerar backup automático"""
    global tarefas
    if _tarefas is not None:
        tarefas = _tarefas
    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)

# ---------- Listar tarefas ----------
def listar_tarefas(filtro=None):
    if not tarefas:
        print(Fore.RED + "\nNenhuma tarefa encontrada.\n")
        return
    print("\nTarefas:")
    for i, t in enumerate(tarefas, 1):
        if filtro == "done" and not t["concluida"]:
            continue
        if filtro == "pending" and t["concluida"]:
            continue
        caixa = "[x]" if t["concluida"] else "[ ]"
        cor = Fore.GREEN if t["concluida"] else Fore.YELLOW
        print(f"{i}. {cor}{caixa} {t['titulo']}{Style.RESET_ALL}")
    print()

# ---------- Adicionar tarefa ----------
def adicionar_tarefa(titulo):
    if not titulo:
        print(Fore.RED + "Título inválido.")
        return
    if any(t["titulo"].lower() == titulo.lower() for t in tarefas):
        print(Fore.RED + f"A tarefa '{titulo}' já existe.")
        return
    tarefas.append({"titulo": titulo, "concluida": False, "historico": []})
    salvar_tarefas_local()
    print(Fore.GREEN + f"Tarefa '{titulo}' adicionada!")

# ---------- Concluir tarefa ----------
def concluir_tarefa(nome):
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        if tarefa["concluida"]:
            print(Fore.YELLOW + f"Tarefa '{nome}' já concluída.")
        else:
            tarefa["concluida"] = True
            salvar_tarefas_local()
            print(Fore.GREEN + f"Tarefa '{nome}' marcada como concluída!")
    else:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")

# ---------- Desmarcar tarefa ----------
def desmarcar_tarefa(nome):
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        if not tarefa["concluida"]:
            print(Fore.YELLOW + f"Tarefa '{nome}' já pendente.")
        else:
            tarefa["concluida"] = False
            salvar_tarefas_local()
            print(Fore.GREEN + f"Tarefa '{nome}' marcada como pendente!")
    else:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")

# ---------- Excluir tarefa ----------
def excluir_tarefa(nome):
    global tarefas
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        tarefas.remove(tarefa)
        salvar_tarefas_local()
        print(Fore.RED + f"Tarefa '{nome}' excluída!")
    else:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")

# ---------- Histórico ----------
def mostrar_historico(nome):
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        if tarefa["historico"]:
            print(f"\nHistórico de '{nome}':")
            for i, nota in enumerate(tarefa["historico"], 1):
                print(f"{i}. {nota}")
        else:
            print("Sem histórico.")
    else:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")

def add_historico(nome, nota):
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        tarefa["historico"].append(nota)
        salvar_tarefas_local()
        print(Fore.GREEN + f"Nota adicionada à tarefa '{nome}'.")
    else:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")

# ---------- Mostrar ajuda ----------
def mostrar_ajuda():
    print("""
Comandos:
  dir                       - Listar tarefas
  dir done/pending          - Listar concluídas/pendentes
  add "tarefa"              - Adicionar tarefa
  done "tarefa"             - Concluir tarefa
  undone "tarefa"           - Desmarcar tarefa
  del "tarefa"              - Excluir tarefa
  hist "tarefa"             - Mostrar histórico
  edit hist "tarefa"        - Editar nota do histórico
  addhist 'tarefa' note 'nota' - Adicionar nota diretamente
  backup export             - Exportar backup manualmente
  backup import NOME_ARQUIVO - Importar backup específico da pasta backups
  clear ou cls              - Limpar tela
  help                      - Mostrar ajuda
  exit                      - Sair (faz backup automaticamente ao sair)
""")

# ---------- Loop principal ----------
def terminal():
    carregar_tarefas()
    importar_ultimo_backup()  # Importa automaticamente o último backup

    print(Fore.CYAN + "Sistema de Lista de Tarefas")
    print("Digite 'help' para ver os comandos.\n")

    session = PromptSession()
    
    while True:
        # Comandos + nomes de tarefas para autocomplete
        nomes_e_comandos = COMANDOS + [t["titulo"] for t in tarefas]
        completer = WordCompleter(nomes_e_comandos, ignore_case=True)
        
        try:
            comando = session.prompt("> ", completer=completer).strip()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        if not comando:
            continue
        
        cmd_lower = comando.lower()
        if cmd_lower.startswith("dir"):
            filtro = None
            if "done" in cmd_lower:
                filtro = "done"
            elif "pending" in cmd_lower:
                filtro = "pending"
            listar_tarefas(filtro)
        elif cmd_lower.startswith("add "):
            nome = comando[4:].strip('"\'')
            adicionar_tarefa(nome)
        elif cmd_lower.startswith("done "):
            nome = comando[5:].strip('"\'')
            concluir_tarefa(nome)
        elif cmd_lower.startswith("undone "):
            nome = comando[7:].strip('"\'')
            desmarcar_tarefa(nome)
        elif cmd_lower.startswith("del "):
            nome = comando[4:].strip('"\'')
            excluir_tarefa(nome)
        elif cmd_lower.startswith("hist "):
            nome = comando[5:].strip('"\'')
            mostrar_historico(nome)
        elif cmd_lower.startswith("backup export"):
            exportar_backup()
        elif cmd_lower.startswith("backup import "):
            nome_arquivo = comando[len("backup import "):].strip('"\'')
            importar_backup(nome_arquivo)
        elif cmd_lower == "clear" or cmd_lower == "cls":
            os.system("cls" if platform.system() == "Windows" else "clear")
        elif cmd_lower == "help":
            mostrar_ajuda()
        elif cmd_lower == "exit":
            print(Fore.CYAN + "Saindo... Fazendo backup automático antes de sair.")
            exportar_backup()  # Backup automático ao fechar
            break
        else:
            print(Fore.RED + "Comando não reconhecido. Digite 'help' para ajuda.\n")

if __name__ == "__main__":
    terminal()
