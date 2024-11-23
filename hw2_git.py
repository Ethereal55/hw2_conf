import subprocess
import argparse
from graphviz import Digraph


def get_commit_dependencies(repo_path, branch_name):
    """
    Получение зависимостей между коммитами для указанной ветки.

    :param repo_path: Путь к репозиторию.
    :param branch_name: Имя ветки.
    :return: Список пар (коммит, родитель).
    """
    try:
        # Переход в репозиторий и получение списка коммитов и их родителей
        result = subprocess.run(
            ["git", "-C", repo_path, "log", "--format=%H %P", branch_name],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды git: {e}")
        return []

    dependencies = []
    for line in output.splitlines():
        parts = line.split()
        commit = parts[0]
        parents = parts[1:]
        for parent in parents:
            dependencies.append((commit, parent))
    return dependencies


def build_graph(dependencies, output_path):
    """
    Построение графа зависимостей и сохранение в файл.

    :param dependencies: Список пар (коммит, родитель).
    :param output_path: Путь к файлу, куда сохранить граф.
    """
    graph = Digraph(format="png")
    graph.attr(rankdir="LR")  # Размещение коммитов слева направо

    # Добавление узлов и ребер
    for commit, parent in dependencies:
        graph.node(commit, commit[:7])  # Упрощенное имя коммита
        graph.node(parent, parent[:7])
        graph.edge(parent, commit)

    # Сохранение графа
    graph.render(output_path, cleanup=True)
    print(f"Граф зависимостей успешно сохранен в {output_path}.png")


# Разбор аргументов командной строки
parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей для git-репозитория.")
parser.add_argument("--visualizer_path", help="Путь к программе для визуализации графов (не используется в Python).")
parser.add_argument("--repo_path", help="Путь к анализируемому репозиторию.")
parser.add_argument("--output_path", help="Путь к файлу с изображением графа зависимостей.")
parser.add_argument("--branch_name", help="Имя ветки в репозитории.")
args = parser.parse_args()

# Получение зависимостей
dependencies = get_commit_dependencies(args.repo_path, args.branch_name)
if not dependencies:
    print("Не удалось получить зависимости для указанной ветки.")
    exit()

# Построение графа
build_graph(dependencies, args.output_path)

