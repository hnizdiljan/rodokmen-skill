import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import novy_projekt  # noqa: E402

STUB = (Path(novy_projekt.SKILL) / "template" / "CLAUDE.md").read_text(encoding="utf-8")
VLASTNI = "# Projekt rodokmenu\n\nVlastní pravidla pro Windows: python -I -X utf8.\n"


def pokyny(dst):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        novy_projekt.pokyny(str(dst))
    return out.getvalue()


def zalohy(dst):
    return sorted((Path(dst) / "pracovni").glob("zaloha_pokyny_*/CLAUDE.md"))


class PokynyTests(unittest.TestCase):
    def test_template_claude_md_imports_agents_md(self):
        self.assertIn("@AGENTS.md", STUB)

    def test_old_project_moves_claude_md_to_agents_md_with_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "CLAUDE.md").write_text(VLASTNI, encoding="utf-8")
            pokyny(tmp)
            self.assertEqual((Path(tmp) / "AGENTS.md").read_text(encoding="utf-8"), VLASTNI)
            self.assertEqual((Path(tmp) / "CLAUDE.md").read_text(encoding="utf-8"), STUB)
            [zaloha] = zalohy(tmp)
            self.assertEqual(zaloha.read_text(encoding="utf-8"), VLASTNI)

    def test_second_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "CLAUDE.md").write_text(VLASTNI, encoding="utf-8")
            pokyny(tmp)
            pokyny(tmp)
            self.assertEqual(len(zalohy(tmp)), 1)
            self.assertEqual((Path(tmp) / "AGENTS.md").read_text(encoding="utf-8"), VLASTNI)

    def test_different_claude_and_agents_are_left_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "CLAUDE.md").write_text(VLASTNI, encoding="utf-8")
            (Path(tmp) / "AGENTS.md").write_text("jiný text\n", encoding="utf-8")
            self.assertIn("beze změny", pokyny(tmp))
            self.assertEqual((Path(tmp) / "CLAUDE.md").read_text(encoding="utf-8"), VLASTNI)
            self.assertEqual((Path(tmp) / "AGENTS.md").read_text(encoding="utf-8"), "jiný text\n")
            self.assertEqual(zalohy(tmp), [])

    def test_identical_copies_become_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("CLAUDE.md", "AGENTS.md"):
                (Path(tmp) / name).write_text(VLASTNI, encoding="utf-8")
            pokyny(tmp)
            self.assertEqual((Path(tmp) / "CLAUDE.md").read_text(encoding="utf-8"), STUB)
            self.assertEqual((Path(tmp) / "AGENTS.md").read_text(encoding="utf-8"), VLASTNI)
            self.assertEqual(len(zalohy(tmp)), 1)

    def test_agents_only_project_is_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "AGENTS.md").write_text(VLASTNI, encoding="utf-8")
            pokyny(tmp)   # CLAUDE.md pak doplní šablona v main()
            self.assertFalse((Path(tmp) / "CLAUDE.md").exists())
            self.assertEqual((Path(tmp) / "AGENTS.md").read_text(encoding="utf-8"), VLASTNI)


if __name__ == "__main__":
    unittest.main()
