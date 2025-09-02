import json
import os
import platform
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Instale a biblioteca colorama: pip install colorama")
    exit()

ARQUIVO_TAREFAS = "tarefas.json"
PASTA_BACKUP = "backups"
tarefas = []

# ---------- Funções de backup ----------
def exportar_backup():
    if not os.path.exists(PASTA_BACKUP):
        os.makedirs(PASTA_BACKUP)
    nome_arquivo = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    caminho = os.path.join(PASTA_BACKUP, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)
    print(Fore.GREEN + f"Backup exportado: {caminho}")

def importar_backup(caminho):
    global tarefas
    if not os.path.exists(caminho):
        caminho_backup = os.path.join(PASTA_BACKUP, caminho)
        if not os.path.exists(caminho_backup):
            print(Fore.RED + f"Arquivo de backup não encontrado: {caminho}")
            return
        caminho = caminho_backup
    with open(caminho, "r", encoding="utf-8") as f:
        tarefas[:] = json.load(f)
    salvar_tarefas()
    print(Fore.GREEN + f"Backup importado: {caminho}")

# ---------- Funções básicas ----------
def carregar_tarefas():
    global tarefas
    if os.path.exists(ARQUIVO_TAREFAS):
        with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
            tarefas[:] = json.load(f)
    else:
        tarefas[:] = []

def salvar_tarefas():
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
    print(Fore.GREEN + f"Tarefa '{titulo}' adicionada!")

# ---------- Concluir tarefa ----------
def concluir_tarefa(nome):
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        if tarefa["concluida"]:
            print(Fore.YELLOW + f"Tarefa '{nome}' já concluída.")
        else:
            tarefa["concluida"] = True
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
            print(Fore.GREEN + f"Tarefa '{nome}' marcada como pendente!")
    else:
        print(Fore.RED + f"Tarefa '{nome}' não encontrada.")

# ---------- Excluir tarefa ----------
def excluir_tarefa(nome):
    tarefa = next((t for t in tarefas if t["titulo"].lower() == nome.lower()), None)
    if tarefa:
        confirmar = input(Fore.YELLOW + f"Confirma exclusão de '{nome}'? (y/n): ").strip().lower()
        if confirmar == "y":
            tarefas.remove(tarefa)
            print(Fore.RED + f"Tarefa '{nome}' excluída!")
        else:
            print(Fore.CYAN + "Exclusão cancelada.")
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
                print(Fore.GREEN + "Nota editada com sucesso!")
            else:
                print(Fore.RED + "Nota vazia não editada.")
        else:
            print(Fore.RED + "Número inválido.")
    except ValueError:
        print(Fore.RED + "Entrada inválida.")

# ---------- Pesquisa ----------
def pesquisar_palavra(chave):
    chave = chave.lower()
    resultados = []
    for t in tarefas:
        if chave in t['titulo'].lower() or any(chave in h.lower() for h in t['historico']):
            resultados.append(t)
    if resultados:
        print(Fore.CYAN + f"\nResultados da pesquisa por '{chave}':")
        for i, t in enumerate(resultados, 1):
            status = "[x]" if t['concluida'] else "[ ]"
            cor = Fore.GREEN if t['concluida'] else Fore.YELLOW
            print(f"{i}. {cor}{status} {t['titulo']}{Style.RESET_ALL}")
            for h in t['historico']:
                if chave in h.lower():
                    print(f"   - {h}")
    else:
        print(Fore.RED + f"Nenhuma tarefa encontrada contendo '{chave}'.")

# ---------- Ajuda ----------
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
  backup import 'arquivo'   - Importar backup específico
  busca 'palavra'           - Pesquisar por palavra-chave
  clear ou cls              - Limpar tela
  help                      - Mostrar ajuda
  exit                      - Sair

Atalhos de teclado:
  Ctrl + A   - Adicionar tarefa
  Ctrl + D   - Excluir tarefa
  Ctrl + E   - Editar nota do histórico
  Ctrl + F   - Pesquisar palavra-chave
  Ctrl + L   - Limpar tela
  Ctrl + B   - Exportar backup
  Ctrl + I   - Importar backup
  Ctrl + Q   - Sair com backup automático e salvar
""")


# ---------- Terminal ----------
def terminal():
    carregar_tarefas()
    print(Fore.CYAN + "Sistema de Lista de Tarefas")
    print("Digite 'help' para ver os comandos.\n")

    comandos = [
        'dir', 'dir done', 'dir pending', 'add', 'done', 'undone',
        'del', 'hist', 'edit hist', 'addhist', 'backup export', 'backup import',
        'busca', 'clear', 'cls', 'help', 'exit'
    ]

    session = PromptSession()
    bindings = KeyBindings()

    # ---------- Atalhos ----------
    @bindings.add('c-d')
    def deletar_tecla(event):
        event.app.current_buffer.insert_text('del ')

    @bindings.add('c-e')
    def editar_tecla(event):
        event.app.current_buffer.insert_text('edit hist ')

    @bindings.add('c-a')
    def adicionar_tecla(event):
        event.app.current_buffer.insert_text('add ')

    @bindings.add('c-f')
    def pesquisar_tecla(event):
        event.app.current_buffer.insert_text('busca ')

    @bindings.add('c-l')
    def limpar_tecla(event):
        event.app.current_buffer.insert_text('cls')

    @bindings.add('c-b')
    def backup_tecla(event):
        event.app.current_buffer.insert_text('backup export')

    @bindings.add('c-i')
    def importar_tecla(event):
        event.app.current_buffer.insert_text('backup import ')

    @bindings.add('c-q')
    def sair_tecla(event):
        print(Fore.CYAN + "\nSaindo com backup automático...")
        salvar_tarefas()
        exportar_backup()
        event.app.exit(result=None)

    while True:
        tarefas_nomes = [t["titulo"] for t in tarefas]
        completer = WordCompleter(comandos + tarefas_nomes, ignore_case=True)
        try:
            comando = session.prompt("> ", completer=completer, key_bindings=bindings)
            if comando is None:
                break
            comando = comando.strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not comando:
            continue
        cmd_lower = comando.lower()

        # ---------- Comandos ----------
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
                        print(Fore.RED + "Uso correto: addhist 'tarefa' note 'nota'")
                else:
                    print(Fore.RED + "Uso correto: addhist 'tarefa' note 'nota'")
            except Exception as e:
                print(Fore.RED + "Erro:", e)
        elif cmd_lower.startswith("backup export"):
            exportar_backup()
        elif cmd_lower.startswith("backup import "):
            caminho = comando[len("backup import "):].strip('"\'')
            importar_backup(caminho)
        elif cmd_lower.startswith("busca "):
            termo = comando[len("busca "):].strip('"\'')
            pesquisar_palavra(termo)
        elif cmd_lower in ["clear", "cls"]:
            os.system("cls" if platform.system() == "Windows" else "clear")
        elif cmd_lower == "help":
            mostrar_ajuda()
        elif cmd_lower == "exit":
            print(Fore.CYAN + "Saindo...")
            salvar_tarefas()
            exportar_backup()
            break
        else:
            print(Fore.RED + "Comando não reconhecido. Digite 'help' para ajuda.\n")

if __name__ == "__main__":
    terminal()
