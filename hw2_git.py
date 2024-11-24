import os
import zlib
from graphviz import Digraph
from struct import unpack


def read_git_object(repo_path, object_hash):
    """
    Считывает объект из папки .git/objects, включая pack-файлы.
    """
    # Проверка наличия объекта в каталоге
    obj_path = os.path.join(repo_path, ".git", "objects", object_hash[:2], object_hash[2:])
    if os.path.exists(obj_path):
        with open(obj_path, "rb") as f:
            compressed_data = f.read()
        return zlib.decompress(compressed_data).decode()

    # Если объект не найден, ищем в pack-файлах
    pack_dir = os.path.join(repo_path, ".git", "objects", "pack")
    for pack_file in os.listdir(pack_dir):
        if pack_file.endswith(".idx"):  # Индексный файл pack-файла
            pack_index_path = os.path.join(pack_dir, pack_file)
            pack_data_path = pack_index_path.replace(".idx", ".pack")
            if os.path.exists(pack_data_path):
                result = read_from_pack(pack_index_path, pack_data_path, object_hash)
                if result:
                    return result

    raise FileNotFoundError(f"Объект {object_hash} не найден в {repo_path}")


def read_from_pack(index_path, pack_path, object_hash):
    """
    Извлекает объект из pack-файла с использованием индекса.
    """
    with open(index_path, "rb") as idx, open(pack_path, "rb") as pack:
        idx.seek(0)
        header = idx.read(4)
        if header != b"\xfftOc":  # Проверяем магическое число
            raise ValueError("Неверный формат файла .idx")

        idx_version = unpack(">I", idx.read(4))[0]
        if idx_version != 2:
            raise ValueError("Поддерживается только версия индекса 2")

        # Пропускаем фантомные данные (256 хэшей)
        idx.seek(8 + 256 * 4)

        # Считываем количество объектов
        num_objects = unpack(">I", idx.read(4))[0]
        print(f"Число объектов в .idx файле: {num_objects}")
        if num_objects > 1_000_000:  # Ограничение на разумное количество объектов
            raise ValueError(f"Неверное количество объектов: {num_objects}.")

        # Считываем 20-байтные SHA1 хэши объектов
        object_hashes = [idx.read(20).hex() for _ in range(num_objects)]

        # Считываем смещения объектов в pack-файле
        offsets = []
        for _ in range(num_objects):
            offset_bytes = idx.read(4)
            offsets.append(int.from_bytes(offset_bytes, "big"))

        # Найдите нужный объект
        try:
            object_index = object_hashes.index(object_hash)
        except ValueError:
            return None

        # Получаем смещение в pack-файле
        object_offset = offsets[object_index]
        pack.seek(object_offset)
        # Для демонстрации упрощаем обработку объекта
        return f"Объект с хэшем {object_hash} найден в pack-файле."  # Заглушка


def parse_commit_object(data):
    """
    Разбирает содержимое объекта коммита и извлекает его зависимости (родительские коммиты).
    """
    lines = data.split("\n")
    parents = [line.split(" ")[1] for line in lines if line.startswith("parent")]
    return parents


def get_commit_dependencies(repo_path, branch_name):
    """
    Извлекает зависимости коммитов из репозитория.
    """
    # Определяем последний коммит указанной ветки
    head_path = os.path.join(repo_path, ".git", "refs", "heads", branch_name)
    if not os.path.exists(head_path):
        raise ValueError(f"Ветка {branch_name} не найдена в {repo_path}")
    with open(head_path, "r") as f:
        current_commit = f.read().strip()

    dependencies = []
    visited = set()

    # Рекурсивно обходим коммиты
    stack = [current_commit]
    while stack:
        commit_hash = stack.pop()
        if commit_hash in visited:
            continue
        visited.add(commit_hash)

        # Читаем объект коммита
        commit_data = read_git_object(repo_path, commit_hash)
        parents = parse_commit_object(commit_data)

        # Добавляем зависимости и продолжаем обход
        for parent in parents:
            dependencies.append((commit_hash, parent))
            stack.append(parent)

    return dependencies


def build_graph(dependencies, output_path):
    """
    Строит граф зависимостей коммитов.
    """
    graph = Digraph(format="png")
    graph.attr(rankdir="LR")  # Размещение узлов слева направо

    for commit, parent in dependencies:
        graph.node(commit, commit[:7])  # Сокращенный хэш
        graph.node(parent, parent[:7])
        graph.edge(parent, commit)

    graph.render(output_path, cleanup=True)
    print(f"Граф сохранен в {output_path}.png")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей для git-репозитория.")
    parser.add_argument("--repo_path", required=True, help="Путь к анализируемому репозиторию.")
    parser.add_argument("--output_path", required=True, help="Путь к файлу для сохранения графа.")
    parser.add_argument("--branch_name", required=True, help="Имя ветки в репозитории.")
    args = parser.parse_args()

    dependencies = get_commit_dependencies(args.repo_path, args.branch_name)
    if not dependencies:
        print("Не удалось найти зависимости для указанной ветки.")
    else:
        build_graph(dependencies, args.output_path)
