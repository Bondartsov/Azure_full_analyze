import os
import pytest

from core.utils.cache import (
    CACHE_DIR,
    get_cache_path,
    clear_cache_for_repo,
    clear_project_summary_cache
)

@pytest.fixture
def fake_cache_dir(tmp_path, monkeypatch):
    """
    Фикстура, которая перенаправляет CACHE_DIR в tmp_path,
    чтобы никакие реальные файлы не пострадали.
    """
    # Подменяем значение CACHE_DIR
    monkeypatch.setattr("core.utils.cache.CACHE_DIR", str(tmp_path))
    return tmp_path

def test_clear_cache_for_repo(fake_cache_dir):
    """
    Тест: создаём фейковый файл кэша одного репозитория
    и проверяем, что функция clear_cache_for_repo удаляет его.
    """
    project_name = "TestProject"
    repo_name = "TestRepo"
    # Генерируем путь к фейковому файлу
    cache_file = get_cache_path(project_name, repo_name)

    # Создаём папку, если не создана
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    # Создаём "фейковый" JSON-файл
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write('{"fake": "data"}')

    assert os.path.exists(cache_file), "Файл кэша репозитория не был создан!"

    # Вызываем функцию очистки кэша
    clear_cache_for_repo(project_name, repo_name)

    # Проверяем, что файл удалён
    assert not os.path.exists(cache_file), "Файл кэша репозитория не был удалён!"

def test_clear_project_summary_cache(fake_cache_dir):
    """
    Тест: создаём фейковый файл сводного кэша проекта
    и проверяем, что функция clear_project_summary_cache удаляет его.
    """
    project_name = "TestProject"
    # Генерируем путь к сводному файлу
    cache_file = get_cache_path(project_name)

    # Создаём папку, если не создана
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    # Создаём "фейковый" JSON-файл
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write('{"fake_summary": "data"}')

    assert os.path.exists(cache_file), "Сводный файл кэша проекта не был создан!"

    # Вызываем функцию очистки кэша для проекта
    clear_project_summary_cache(project_name)

    # Проверяем, что файл удалён
    assert not os.path.exists(cache_file), "Сводный файл кэша проекта не был удалён!"
