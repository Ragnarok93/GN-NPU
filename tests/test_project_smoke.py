from pathlib import Path


def test_project_documents_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "README.md").is_file()
    assert (root / "docs" / "architecture.md").is_file()
    assert (root / "docs" / "data-schema.md").is_file()
