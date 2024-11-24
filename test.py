import unittest
import os
from hw2_git import read_git_object, parse_commit_object, get_commit_dependencies, build_graph

class TestGitDependencyVisualizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Подготовка тестового окружения
        cls.test_repo_path = "./test_repo"  # Укажите путь к тестовому репозиторию
        cls.test_branch_name = "master"    # Укажите название ветки в тестовом репозитории
        cls.output_path = "./test_output"

        # Убедимся, что тестовый репозиторий существуе
        if not os.path.exists(cls.test_repo_path):
            raise FileNotFoundError(f"Тестовый репозиторий не найден: {cls.test_repo_path}")

    def test_read_git_object_loose(self):
        # Тест чтения объекта, хранящегося в loose-формате
        test_hash = "KNOWN_OBJECT_HASH"  # Замените на реальный хэш объекта
        try:
            result = read_git_object(self.test_repo_path, test_hash)
            self.assertIn("tree", result)  # Проверяем наличие ожидаемых данных
        except FileNotFoundError:
            self.fail("Loose object could not be found")

    def test_read_git_object_pack(self):
        # Тест чтения объекта, хранящегося в pack-формате
        test_hash = "PACKED_OBJECT_HASH"  # Замените на реальный хэш объекта
        try:
            result = read_git_object(self.test_repo_path, test_hash)
            self.assertIn("tree", result)  # Проверяем наличие ожидаемых данных
        except FileNotFoundError:
            self.fail("Packed object could not be found")

    def test_parse_commit_object(self):
        # Тест разбора содержимого объекта коммита
        commit_data = (
            "tree TREE_HASH\n"
            "parent PARENT_HASH\n"
            "author Author Name <email@example.com> 1234567890 +0000\n"
            "committer Committer Name <email@example.com> 1234567890 +0000\n\n"
            "Commit message"
        )
        parents = parse_commit_object(commit_data)
        self.assertEqual(parents, ["PARENT_HASH"])

    def test_get_commit_dependencies(self):
         # Тест извлечения зависимостей коммитов из ветки
        try:
            dependencies = get_commit_dependencies(self.test_repo_path, self.test_branch_name)
            self.assertTrue(len(dependencies) > 0)
            for dep in dependencies:
                self.assertEqual(len(dep), 2)  # Каждая зависимость — кортеж (коммит, родитель)
        except ValueError:
            self.fail("Branch not found or no dependencies could be extracted")

    def test_build_graph(self):
        # Тест построения графа из зависимостей
        dependencies = [("COMMIT_1", "COMMIT_2"), ("COMMIT_2", "COMMIT_3")]
        output_file = os.path.join(self.output_path, "test_graph")
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        
        build_graph(dependencies, output_file)
        self.assertTrue(os.path.exists(output_file + ".png"))

    @classmethod
    def tearDownClass(cls):
        # Очистка тестовых файлов
        if os.path.exists(cls.output_path):
            for file in os.listdir(cls.output_path):
                os.remove(os.path.join(cls.output_path, file))
            os.rmdir(cls.output_path)

if __name__ == "__main__":
    unittest.main()
