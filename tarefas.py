import json
import os
import platform

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Instale a biblioteca colorama para usar cores:")
    print("pip install colorama")
    exit()

# Importar prompt_toolkit para autocomplete
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
except ImportError:
    print("Instale prompt_toolkit para usar autocomplete:")
    print("pip install prompt_toolkit")
    exit()

ARQUIVO_TAREFAS = "tarefas.json"
tarefas = []

# ---------- Funções básicas ----------
def carregar_tarefas():
    global tarefas
    if os.path.exists(ARQUIVO_TAREFAS):
        with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
            tarefas = json.load(f)
    else:
        tarefas = []

def salvar_tarefas(_tarefas=None):
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
    salvar_tarefas()
    print(Fore.GREEN + f"Tarefa '{titulo}' adicionada!")

# ---------- Concluir tarefa ----------
def concluir_tarefa(nome):
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        if tarefa["concluida"]:
            print(Fore.YELLOW + f"Tarefa '{nome}' já concluída.")
        else:
            tarefa["concluida"] = True
            salvar_tarefas()
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
            salvar_tarefas()
            print(Fore.GREEN + f"Tarefa '{nome}' marcada como pendente!")
    else:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")

# ---------- Excluir tarefa ----------
def excluir_tarefa(nome):
    global tarefas
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        tarefas.remove(tarefa)
        salvar_tarefas()
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
        salvar_tarefas()
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
    mostrar_historico(nome)
    try:
        n = int(input("Número da nota que deseja editar: "))
        if 1 <= n <= len(tarefa["historico"]):
            nova = input("Nova nota: ").strip()
            if nova:
                tarefa["historico"][n-1] = nova
                salvar_tarefas()
                print(Fore.GREEN + "Nota editada com sucesso!")
            else:
                print(Fore.RED + "Nota vazia não editada.")
        else:
            print(Fore.RED + "Número inválido.")
    except ValueError:
        print(Fore.RED + "Entrada inválida.")

# ---------- Entrar na tarefa via cd ----------
def entrar_tarefa(nome):
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if not tarefa:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")
        return
    print(Fore.CYAN + f"\nEntrando na tarefa: {tarefa['titulo']}")
    while True:
        print("\nComandos dentro da tarefa: hist, addhist, back")
        cmd = input(f"{tarefa['titulo']}> ").strip().lower()
        if cmd == "hist":
            mostrar_historico(tarefa["titulo"])
        elif cmd == "addhist":
            nota = input("Digite a nota: ").strip()
            if nota:
                add_historico(tarefa["titulo"], nota)
        elif cmd == "back":
            break
        else:
            print(Fore.RED + "Comando não reconhecido. Use hist, addhist ou back.")

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
  clear                     - Limpar tela
  help                      - Mostrar ajuda
  exit                      - Sair
""")

# ---------- Loop principal ----------
def terminal():
    carregar_tarefas()
    print(Fore.CYAN + "Sistema de Lista de Tarefas")
    print("Digite 'help' para ver os comandos.\n")

    session = PromptSession()

    while True:
        tarefas_nomes = [t["titulo"] for t in tarefas]
        completer = WordCompleter(tarefas_nomes, ignore_case=True)
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
        elif cmd_lower.startswith("edit hist "):
            nome = comando[10:].strip('"\'')
            editar_historico(nome)
        elif cmd_lower.startswith("addhist "):
            # Comando esperado: addhist 'tarefa' note 'nota a ser escrita'
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
                print(Fore.RED + "Erro ao adicionar histórico:", e)
        elif cmd_lower == "clear":
            os.system("cls" if platform.system() == "Windows" else "clear")
        elif cmd_lower == "help":
            mostrar_ajuda()
        elif cmd_lower == "exit":
            print(Fore.CYAN + "Saindo...")
            break
        else:
            print(Fore.RED + "Comando não reconhecido. Digite 'help' para ajuda.\n")

if __name__ == "__main__":
    terminal()
