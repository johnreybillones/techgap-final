"""Smoke test to verify CI pipeline test discovery and execution."""


def test_ci_pipeline_sanity():
    """Verify standard assertions execute properly in pytest."""
    assert 1 + 1 == 2


def test_project_structure_has_essential_directories():
    """Verify that expected core directories exist."""
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent
    assert (repo_root / "scripts").is_dir()
    assert (repo_root / "tests").is_dir()
    assert (repo_root / "CONTRIBUTING.md").is_file()
