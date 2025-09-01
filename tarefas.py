import json
import os
import platform
from datetime import datetime

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Instale a biblioteca colorama: pip install colorama")
    exit()

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
except ImportError:
    print("Instale prompt_toolkit: pip install prompt_toolkit")
    exit()

ARQUIVO_TAREFAS = "tarefas.json"
PASTA_BACKUP = "backups"
tarefas = []

COMANDOS = ["dir", "add", "done", "undone", "del", "hist", "edit hist", "addhist",
            "backup export", "backup import", "clear", "cls", "help", "exit"]

# ---------- Funções de backup ----------
def exportar_backup():
    if not os.path.exists(PASTA_BACKUP):
        os.makedirs(PASTA_BACKUP)
    nome_arquivo = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    caminho = os.path.join(PASTA_BACKUP, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)
    print(Fore.GREEN + f"Backup exportado: {caminho}")

def importar_backup(arquivo):
    global tarefas
    caminho = os.path.join(PASTA_BACKUP, arquivo)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            tarefas = json.load(f)
        salvar_tarefas(False)  # salva no arquivo principal sem criar backup extra
        print(Fore.GREEN + f"Backup importado: {caminho}")
    else:
        print(Fore.RED + f"Arquivo de backup não encontrado: {caminho}")

# ---------- Funções básicas ----------
def carregar_tarefas():
    global tarefas
    if os.path.exists(ARQUIVO_TAREFAS):
        with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
            tarefas = json.load(f)
    else:
        tarefas = []

def salvar_tarefas(fazer_backup=True):
    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)
    if fazer_backup:
        exportar_backup()

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
    salvar_tarefas(False)
    print(Fore.GREEN + f"Tarefa '{titulo}' adicionada!")

# ---------- Concluir tarefa ----------
def concluir_tarefa(nome):
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        if tarefa["concluida"]:
            print(Fore.YELLOW + f"Tarefa '{nome}' já concluída.")
        else:
            tarefa["concluida"] = True
            salvar_tarefas(False)
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
            salvar_tarefas(False)
            print(Fore.GREEN + f"Tarefa '{nome}' marcada como pendente!")
    else:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")

# ---------- Excluir tarefa ----------
def excluir_tarefa(nome):
    global tarefas
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        tarefas.remove(tarefa)
        salvar_tarefas(False)
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
        salvar_tarefas(False)
        print(Fore.GREEN + f"Nota adicionada à tarefa '{nome}'.")
    else:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")

def editar_historico(nome):
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if not tarefa:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")
        return
    if not tarefa["historico"]:
        print("Sem notas para editar.")
        return
    for i, nota in enumerate(tarefa["historico"], 1):
        print(f"{i}. {nota}")
    try:
        n = int(input("Número da nota que deseja editar: "))
        if 1 <= n <= len(tarefa["historico"]):
            nova = input("Nova nota: ").strip()
            if nova:
                tarefa["historico"][n-1] = nova
                salvar_tarefas(False)
                print(Fore.GREEN + "Nota editada com sucesso!")
            else:
                print(Fore.RED + "Nota vazia não editada.")
        else:
            print(Fore.RED + "Número inválido.")
    except ValueError:
        print(Fore.RED + "Entrada inválida.")

# ---------- Autocomplete Inteligente ----------
class TarefasCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lower()

        # Comandos que precisam do nome da tarefa
        for cmd in ["done", "undone", "del", "hist", "edit hist"]:
            if text.startswith(cmd + " "):
                parte = text.split(" ", 1)[1] if " " in text else ""
                for t in tarefas:
                    if t["titulo"].lower().startswith(parte):
                        yield Completion(t["titulo"], start_position=-len(parte))
                return

        # Comando addhist
        if text.startswith("addhist "):
            partes = text.split(" ", 2)
            if len(partes) == 1:
                for t in tarefas:
                    yield Completion(t["titulo"], start_position=0)
            elif len(partes) == 2:
                if not partes[1].startswith("note"):
                    yield Completion("note", start_position=0)
            return

        # Comando backup import
        if text.startswith("backup import "):
            if os.path.exists(PASTA_BACKUP):
                arquivos = [f for f in os.listdir(PASTA_BACKUP) if f.endswith(".json")]
                prefixo = text[len("backup import "):]
                for f in arquivos:
                    if f.lower().startswith(prefixo.lower()):
                        yield Completion(f, start_position=-len(prefixo))
            return

        # Comandos gerais
        for cmd in COMANDOS:
            if cmd.startswith(text):
                yield Completion(cmd, start_position=-len(text))

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
  backup import arquivo     - Importar backup específico da pasta backups
  clear ou cls              - Limpar tela
  help                      - Mostrar ajuda
  exit                      - Sair
""")

# ---------- Loop principal ----------
def terminal():
    carregar_tarefas()
    print(Fore.CYAN + "Sistema de Lista de Tarefas")
    print("Digite 'help' para ver os comandos.\n")

    session = PromptSession(completer=TarefasCompleter())

    while True:
        try:
            comando = session.prompt("> ").strip()
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
        elif cmd_lower.startswith("edit hist "):
            nome = comando[10:].strip('"\'')
            editar_historico(nome)
        elif cmd_lower.startswith("addhist "):
            try:
                cmd_body = comando[8:].strip()
                if " note " in cmd_body.lower():
                    partes = cmd_body.split(" note ", 1)
                    tarefa_nome = partes[0].strip().strip("'\"")
                    nota = partes[1].strip().strip("'\"")
                    if tarefa_nome and nota:
                        add_historico(tarefa_nome, nota)
                    else:
                        print(Fore.RED + "Uso correto: addhist 'tarefa' note 'nota a ser escrita'")
                else:
                    print(Fore.RED + "Uso correto: addhist 'tarefa' note 'nota a ser escrita'")
            except Exception as e:
                print(Fore.RED + f"Erro ao adicionar histórico: {e}")
        elif cmd_lower.startswith("backup export"):
            exportar_backup()
        elif cmd_lower.startswith("backup import "):
            arquivo = comando[len("backup import "):].strip('"\'')
            importar_backup(arquivo)
        elif cmd_lower in ["clear", "cls"]:
            os.system("cls" if platform.system() == "Windows" else "clear")
        elif cmd_lower == "help":
            mostrar_ajuda()
        elif cmd_lower == "exit":
            salvar_tarefas(fazer_backup=True)  # faz backup final ao sair
            print(Fore.CYAN + "Saindo...")
            break
        else:
            print(Fore.RED + "Comando não reconhecido. Digite 'help' para ajuda.\n")

if __name__ == "__main__":
    terminal()
