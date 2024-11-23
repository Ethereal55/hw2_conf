import unittest
from unittest.mock import patch, MagicMock
import subprocess
from graphviz import Digraph
from io import StringIO
import hw2_git  # Предполагаем, что ваш код сохранен в hw2_git.py

class TestGitVisualizer(unittest.TestCase):

    @patch("subprocess.run")
    def test_get_commit_dependencies_success(self, mock_run):
        # Мокируем вывод команды git
        mock_run.return_value = MagicMock(stdout="commit1 parent1\ncommit2 parent1 parent2", stderr="", returncode=0)
        
        # Проверяем, что функция возвращает правильные зависимости
        repo_path = "/fake/repo"
        branch_name = "main"
        result = hw2_git.get_commit_dependencies(repo_path, branch_name)
        
        expected = [("commit1", "parent1"), ("commit2", "parent1"), ("commit2", "parent2")]
        self.assertEqual(result, expected)

    @patch("subprocess.run")
    def test_get_commit_dependencies_error(self, mock_run):
        # Мокируем ошибку при выполнении git
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        
        # Проверяем, что функция возвращает пустой список при ошибке
        repo_path = "/fake/repo"
        branch_name = "main"
        result = hw2_git.get_commit_dependencies(repo_path, branch_name)
        self.assertEqual(result, [])

    def test_build_graph(self):
        # Проверяем создание графа (мокируем сам вывод Graphviz)
        dependencies = [("commit1", "parent1"), ("commit2", "parent1")]
        output_path = "test_output"
        
        with patch.object(Digraph, "render", return_value=None) as mock_render:
            hw2_git.build_graph(dependencies, output_path)
            
            # Проверяем, что метод render был вызван
            mock_render.assert_called_once_with(output_path, cleanup=True)

    @patch("subprocess.run")
    def test_get_commit_dependencies_no_commits(self, mock_run):
        # Мокируем случай, когда коммиты не найдены
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        
        # Проверяем, что возвращается пустой список, если нет коммитов
        repo_path = "/fake/repo"
        branch_name = "main"
        result = hw2_git.get_commit_dependencies(repo_path, branch_name)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()
