#!/usr/bin/env python3
"""
Test suite for knowledge_store.py and seed_knowledge.py.

All tests use a temporary DEV_TEAM_DIR to isolate from the live ~/.dev_team store.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def load_module(name: str):
    """Dynamically load a script module from the scripts directory."""
    path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Base test case with isolated temp storage
# ---------------------------------------------------------------------------


class IsolatedStoreTestCase(unittest.TestCase):
    """Base class that redirects DEV_TEAM_DIR to a fresh temp directory per test."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._orig_env = os.environ.get("DEV_TEAM_DIR")
        os.environ["DEV_TEAM_DIR"] = self._tmpdir.name
        # Re-import with fresh env so KnowledgeStore picks up the new path
        self.ks_mod = load_module("knowledge_store")
        self.store = self.ks_mod.KnowledgeStore()

    def tearDown(self):
        if self._orig_env is None:
            os.environ.pop("DEV_TEAM_DIR", None)
        else:
            os.environ["DEV_TEAM_DIR"] = self._orig_env
        self._tmpdir.cleanup()

    # Helper to add a minimal entry and return its ID
    def _add(
        self,
        title="Test Entry",
        category="convention",
        content="content",
        summary="summary",
        tags=None,
        agent="coder",
        tasks=None,
        confidence="high",
    ):
        return self.store.add_entry(
            title=title,
            category=category,
            content=content,
            summary=summary,
            tags=tags or ["test"],
            agent_author=agent,
            related_tasks=tasks or [],
            confidence=confidence,
        )


# ===========================================================================
# KnowledgeStore — initialisation & storage
# ===========================================================================


class TestKnowledgeStoreInit(IsolatedStoreTestCase):
    def test_knowledge_file_created_on_init(self):
        """Storage file must be created during __init__."""
        self.assertTrue(self.store.knowledge_file.exists())

    def test_empty_store_on_fresh_init(self):
        """A brand-new store should have no entries."""
        self.assertEqual(self.store.list_all(), [])

    def test_dev_team_dir_env_var_respected(self):
        """KnowledgeStore must use DEV_TEAM_DIR env var for storage path."""
        expected = Path(self._tmpdir.name) / "knowledge.json"
        self.assertEqual(self.store.knowledge_file.resolve(), expected.resolve())


# ===========================================================================
# add_entry
# ===========================================================================


class TestAddEntry(IsolatedStoreTestCase):
    def test_add_returns_knowledge_id(self):
        kid = self._add()
        self.assertTrue(kid.startswith("know_"))

    def test_first_id_is_know_001(self):
        kid = self._add()
        self.assertEqual(kid, "know_001")

    def test_second_id_is_know_002(self):
        self._add(title="First")
        kid = self._add(title="Second")
        self.assertEqual(kid, "know_002")

    def test_entry_persisted_to_disk(self):
        kid = self._add(title="Persist Test")
        # Re-create the store from the same path — should still find the entry
        store2 = self.ks_mod.KnowledgeStore()
        entry = store2.get_entry(kid)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["title"], "Persist Test")

    def test_invalid_category_raises(self):
        with self.assertRaises(ValueError):
            self._add(category="not_a_category")

    def test_invalid_confidence_raises(self):
        with self.assertRaises(ValueError):
            self._add(confidence="super-high")

    def test_all_valid_categories_accepted(self):
        for cat in self.ks_mod.KnowledgeStore.VALID_CATEGORIES:
            kid = self._add(title=f"Entry for {cat}", category=cat)
            self.assertTrue(kid.startswith("know_"))

    def test_default_status_is_active(self):
        kid = self._add()
        entry = self.store.get_entry(kid)
        self.assertEqual(entry["status"], "active")

    def test_tags_stored_correctly(self):
        kid = self._add(tags=["alpha", "beta", "gamma"])
        entry = self.store.get_entry(kid)
        self.assertCountEqual(entry["tags"], ["alpha", "beta", "gamma"])

    def test_related_tasks_stored(self):
        kid = self._add(tasks=["task_001", "task_002"])
        entry = self.store.get_entry(kid)
        self.assertIn("task_001", entry["related_tasks"])
        self.assertIn("task_002", entry["related_tasks"])

    def test_empty_related_tasks_default(self):
        kid = self._add()
        entry = self.store.get_entry(kid)
        self.assertEqual(entry["related_tasks"], [])

    def test_monotonic_ids_after_deletion(self):
        """IDs must not reuse after an entry is 'removed' via update to archived."""
        kid1 = self._add(title="A")
        kid2 = self._add(title="B")
        # Deprecate know_001 (simulate a deletion scenario by archiving)
        self.store.update_entry(kid1, status="archived")
        kid3 = self._add(title="C")
        # know_003 must follow know_002, not reuse know_001
        self.assertEqual(kid3, "know_003")


# ===========================================================================
# get_entry
# ===========================================================================


class TestGetEntry(IsolatedStoreTestCase):
    def test_get_returns_full_entry(self):
        kid = self._add(title="Get Me")
        entry = self.store.get_entry(kid)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["title"], "Get Me")
        self.assertIn("content", entry)

    def test_get_increments_access_count(self):
        kid = self._add()
        self.store.get_entry(kid)
        self.store.get_entry(kid)
        entry = self.store.get_entry(kid)
        self.assertEqual(entry["access_count"], 3)

    def test_get_nonexistent_returns_none(self):
        result = self.store.get_entry("know_999")
        self.assertIsNone(result)


# ===========================================================================
# update_entry
# ===========================================================================


class TestUpdateEntry(IsolatedStoreTestCase):
    def test_update_title(self):
        kid = self._add(title="Old Title")
        self.store.update_entry(kid, title="New Title")
        self.assertEqual(self.store.get_entry(kid)["title"], "New Title")

    def test_update_summary(self):
        kid = self._add()
        self.store.update_entry(kid, summary="Updated summary")
        self.assertEqual(self.store.get_entry(kid)["summary"], "Updated summary")

    def test_update_content(self):
        kid = self._add(content="old")
        self.store.update_entry(kid, content="new content")
        self.assertEqual(self.store.get_entry(kid)["content"], "new content")

    def test_update_tags(self):
        kid = self._add(tags=["old"])
        self.store.update_entry(kid, tags=["new1", "new2"])
        self.assertCountEqual(self.store.get_entry(kid)["tags"], ["new1", "new2"])

    def test_update_confidence(self):
        kid = self._add(confidence="high")
        self.store.update_entry(kid, confidence="low")
        self.assertEqual(self.store.get_entry(kid)["confidence"], "low")

    def test_update_status_to_archived(self):
        kid = self._add()
        self.store.update_entry(kid, status="archived")
        self.assertEqual(self.store.get_entry(kid)["status"], "archived")

    def test_update_invalid_confidence_raises(self):
        kid = self._add()
        with self.assertRaises(ValueError):
            self.store.update_entry(kid, confidence="extreme")

    def test_update_invalid_status_raises(self):
        kid = self._add()
        with self.assertRaises(ValueError):
            self.store.update_entry(kid, status="in_progress")

    def test_update_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            self.store.update_entry("know_999", title="Nope")

    def test_update_touches_updated_at(self):
        kid = self._add()
        before = self.store.get_entry(kid)["updated_at"]
        import time

        time.sleep(0.01)
        self.store.update_entry(kid, title="Changed")
        after = self.store.get_entry(kid)["updated_at"]
        self.assertGreater(after, before)


# ===========================================================================
# deprecate_entry
# ===========================================================================


class TestDeprecateEntry(IsolatedStoreTestCase):
    def test_deprecate_changes_status(self):
        kid = self._add()
        self.store.deprecate_entry(kid)
        entry = self.store.get_entry(kid)
        self.assertEqual(entry["status"], "deprecated")

    def test_deprecate_with_replacement_sets_replaced_by(self):
        old = self._add(title="Old")
        new = self._add(title="New")
        self.store.deprecate_entry(old, superseded_by=new)
        old_entry = self.store.get_entry(old)
        self.assertEqual(old_entry["replaced_by"], new)

    def test_deprecate_with_replacement_sets_supersedes_on_new(self):
        old = self._add(title="Old")
        new = self._add(title="New")
        self.store.deprecate_entry(old, superseded_by=new)
        new_entry = self.store.get_entry(new)
        self.assertEqual(new_entry["supersedes"], old)

    def test_deprecate_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            self.store.deprecate_entry("know_999")

    def test_deprecate_with_nonexistent_replacement_raises(self):
        kid = self._add()
        with self.assertRaises(ValueError):
            self.store.deprecate_entry(kid, superseded_by="know_999")

    def test_deprecated_entry_excluded_from_default_search(self):
        kid = self._add(title="Deprecated Entry")
        self.store.deprecate_entry(kid)
        results = self.store.search(query="Deprecated Entry")
        ids = [r["knowledge_id"] for r in results]
        self.assertNotIn(kid, ids)


# ===========================================================================
# add_tags
# ===========================================================================


class TestAddTags(IsolatedStoreTestCase):
    def test_add_new_tags(self):
        kid = self._add(tags=["existing"])
        self.store.add_tags(kid, ["new1", "new2"])
        entry = self.store.get_entry(kid)
        self.assertIn("new1", entry["tags"])
        self.assertIn("new2", entry["tags"])
        self.assertIn("existing", entry["tags"])

    def test_add_tags_deduplicates(self):
        kid = self._add(tags=["dup"])
        self.store.add_tags(kid, ["dup", "dup"])
        entry = self.store.get_entry(kid)
        self.assertEqual(entry["tags"].count("dup"), 1)

    def test_add_tags_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            self.store.add_tags("know_999", ["tag"])


# ===========================================================================
# link_task
# ===========================================================================


class TestLinkTask(IsolatedStoreTestCase):
    def test_link_task_appended(self):
        kid = self._add()
        self.store.link_task(kid, "task_042")
        entry = self.store.get_entry(kid)
        self.assertIn("task_042", entry["related_tasks"])

    def test_link_task_no_duplicates(self):
        kid = self._add()
        self.store.link_task(kid, "task_001")
        self.store.link_task(kid, "task_001")
        entry = self.store.get_entry(kid)
        self.assertEqual(entry["related_tasks"].count("task_001"), 1)

    def test_link_task_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            self.store.link_task("know_999", "task_001")


# ===========================================================================
# search
# ===========================================================================


class TestSearch(IsolatedStoreTestCase):
    def setUp(self):
        super().setUp()
        self._add(
            title="JWT authentication guide",
            category="security",
            content="Use HS256 algorithm for signing JWT tokens.",
            summary="JWT best practices",
            tags=["jwt", "auth", "security"],
            agent="security",
            confidence="high",
        )
        self._add(
            title="Database indexing patterns",
            category="performance",
            content="Create composite indexes for frequently joined columns.",
            summary="Index for performance",
            tags=["database", "index", "sql"],
            agent="coder",
            confidence="high",
        )
        self._add(
            title="Atomic write convention",
            category="convention",
            content="Write to .tmp then rename for atomic file operations.",
            summary="Atomic writes",
            tags=["file-io", "atomic"],
            agent="coder",
            confidence="high",
        )

    def test_search_no_query_returns_all(self):
        results = self.store.search()
        self.assertEqual(len(results), 3)

    def test_search_query_filters_by_relevance(self):
        results = self.store.search(query="JWT authentication")
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0]["title"], "JWT authentication guide")

    def test_search_category_filter(self):
        results = self.store.search(categories=["security"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["category"], "security")

    def test_search_tags_filter(self):
        results = self.store.search(tags=["jwt"])
        self.assertEqual(len(results), 1)
        self.assertIn("jwt", results[0]["tags"])

    def test_search_agent_filter(self):
        results = self.store.search(agent_author="security")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["agent_author"], "security")

    def test_search_task_filter(self):
        kid = self._add(title="Task-linked entry", tasks=["task_007"])
        results = self.store.search(task_id="task_007")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["knowledge_id"], kid)

    def test_search_limit_respected(self):
        results = self.store.search(limit=2)
        self.assertLessEqual(len(results), 2)

    def test_search_excludes_content_by_default(self):
        results = self.store.search()
        for r in results:
            self.assertNotIn("content", r)

    def test_search_include_content(self):
        results = self.store.search(include_content=True)
        for r in results:
            self.assertIn("content", r)

    def test_search_excludes_deprecated_by_default(self):
        kid = self._add(
            title="Deprecated Security Entry", category="security", tags=["jwt"]
        )
        self.store.deprecate_entry(kid)
        results = self.store.search(query="Deprecated Security Entry")
        ids = [r["knowledge_id"] for r in results]
        self.assertNotIn(kid, ids)

    def test_search_relevance_order(self):
        """Title match should rank higher than content-only match."""
        # know_001 has "JWT" in title — should outrank others on jwt query
        results = self.store.search(query="jwt")
        self.assertEqual(results[0]["title"], "JWT authentication guide")


# ===========================================================================
# get_for_agent
# ===========================================================================


class TestGetForAgent(IsolatedStoreTestCase):
    def setUp(self):
        super().setUp()
        self._add(title="Pattern entry", category="pattern", tags=["pattern"])
        self._add(title="Bug fix entry", category="bug_fix", tags=["bug"])
        self._add(title="Security entry", category="security", tags=["security"])
        self._add(title="DevOps entry", category="devops", tags=["devops"])
        self._add(title="Architecture entry", category="architecture", tags=["arch"])

    def test_coder_gets_pattern_and_bug_fix(self):
        results = self.store.get_for_agent("coder")
        categories = {r["category"] for r in results}
        # coder maps to pattern, bug_fix, convention, performance, testing
        self.assertTrue(categories & {"pattern", "bug_fix"})

    def test_security_agent_gets_security(self):
        results = self.store.get_for_agent("security")
        categories = {r["category"] for r in results}
        self.assertIn("security", categories)

    def test_devops_agent_gets_devops(self):
        results = self.store.get_for_agent("devops")
        categories = {r["category"] for r in results}
        self.assertIn("devops", categories)

    def test_unknown_agent_returns_all_entries(self):
        """Unknown agents receive no category filter — all active entries returned."""
        results = self.store.get_for_agent("unknown_agent", limit=100)
        self.assertEqual(len(results), 5)

    def test_limit_respected(self):
        results = self.store.get_for_agent("coder", limit=1)
        self.assertEqual(len(results), 1)

    def test_keywords_influence_ranking(self):
        # Add a very specific entry
        self._add(
            title="JWT auth patterns for coder",
            category="pattern",
            tags=["jwt", "auth"],
        )
        results = self.store.get_for_agent("coder", context_keywords=["jwt", "auth"])
        # The JWT-specific entry should appear in results
        titles = [r["title"] for r in results]
        self.assertIn("JWT auth patterns for coder", titles)


# ===========================================================================
# list_by_category
# ===========================================================================


class TestListByCategory(IsolatedStoreTestCase):
    def setUp(self):
        super().setUp()
        self._add(title="Conv 1", category="convention")
        self._add(title="Conv 2", category="convention")
        self._add(title="Arch 1", category="architecture")

    def test_list_by_category_returns_correct_entries(self):
        results = self.store.list_by_category("convention")
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r["category"], "convention")

    def test_list_by_category_excludes_content(self):
        results = self.store.list_by_category("convention")
        for r in results:
            self.assertNotIn("content", r)

    def test_list_empty_category_returns_empty(self):
        results = self.store.list_by_category("performance")
        self.assertEqual(results, [])


# ===========================================================================
# list_all
# ===========================================================================


class TestListAll(IsolatedStoreTestCase):
    def test_list_all_returns_all_active(self):
        self._add(title="A")
        self._add(title="B")
        self._add(title="C")
        self.assertEqual(len(self.store.list_all()), 3)

    def test_list_all_excludes_deprecated(self):
        kid = self._add(title="Dep")
        self._add(title="Active")
        self.store.deprecate_entry(kid)
        results = self.store.list_all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Active")

    def test_list_all_pagination(self):
        for i in range(5):
            self._add(title=f"Entry {i}")
        page1 = self.store.list_all(limit=3, offset=0)
        page2 = self.store.list_all(limit=3, offset=3)
        self.assertEqual(len(page1), 3)
        self.assertEqual(len(page2), 2)
        # No overlap
        ids1 = {r["knowledge_id"] for r in page1}
        ids2 = {r["knowledge_id"] for r in page2}
        self.assertTrue(ids1.isdisjoint(ids2))

    def test_list_all_excludes_content(self):
        self._add()
        for r in self.store.list_all():
            self.assertNotIn("content", r)


# ===========================================================================
# get_stats
# ===========================================================================


class TestGetStats(IsolatedStoreTestCase):
    def test_stats_empty_store(self):
        stats = self.store.get_stats()
        self.assertEqual(stats["total_entries"], 0)
        self.assertEqual(stats["active_entries"], 0)

    def test_stats_counts_correctly(self):
        self._add(category="convention", agent="coder", confidence="high")
        self._add(category="convention", agent="architect", confidence="medium")
        self._add(category="security", agent="security", confidence="high")
        stats = self.store.get_stats()
        self.assertEqual(stats["total_entries"], 3)
        self.assertEqual(stats["active_entries"], 3)
        self.assertEqual(stats["by_category"]["convention"], 2)
        self.assertEqual(stats["by_category"]["security"], 1)

    def test_stats_by_status(self):
        kid = self._add()
        self._add(title="B")
        self.store.deprecate_entry(kid)
        stats = self.store.get_stats()
        self.assertEqual(stats["by_status"]["active"], 1)
        self.assertEqual(stats["by_status"]["deprecated"], 1)

    def test_stats_most_accessed(self):
        kid1 = self._add(title="Less accessed")
        kid2 = self._add(title="More accessed")
        self.store.get_entry(kid2)
        self.store.get_entry(kid2)
        stats = self.store.get_stats()
        self.assertEqual(stats["most_accessed"]["knowledge_id"], kid2)

    def test_stats_most_accessed_none_when_empty(self):
        stats = self.store.get_stats()
        self.assertIsNone(stats["most_accessed"])


# ===========================================================================
# _next_id (monotonic ID generation)
# ===========================================================================


class TestNextId(IsolatedStoreTestCase):
    def test_first_id(self):
        self.assertEqual(self.store._next_id({}), "know_001")

    def test_sequential_ids(self):
        knowledge = {"know_001": {}, "know_002": {}}
        self.assertEqual(self.store._next_id(knowledge), "know_003")

    def test_gap_does_not_reuse(self):
        """After know_001 is removed, the next ID must be know_003 not know_002."""
        knowledge = {"know_002": {}}
        self.assertEqual(self.store._next_id(knowledge), "know_003")

    def test_large_id_pads_correctly(self):
        knowledge = {f"know_{i:03d}": {} for i in range(1, 100)}
        self.assertEqual(self.store._next_id(knowledge), "know_100")


# ===========================================================================
# _tokenise
# ===========================================================================


class TestTokenise(IsolatedStoreTestCase):
    def test_lowercase(self):
        tokens = self.store._tokenise("Hello World")
        self.assertIn("hello", tokens)

    def test_stop_words_removed(self):
        tokens = self.store._tokenise("this is a test")
        self.assertNotIn("this", tokens)
        self.assertNotIn("is", tokens)
        self.assertNotIn("a", tokens)
        self.assertIn("test", tokens)

    def test_punctuation_stripped(self):
        tokens = self.store._tokenise("file-safety, json.")
        self.assertIn("file", tokens)
        self.assertIn("safety", tokens)
        self.assertIn("json", tokens)

    def test_empty_string_returns_empty_set(self):
        self.assertEqual(self.store._tokenise(""), set())


# ===========================================================================
# CLI — subprocess tests
# ===========================================================================


class TestCLI(unittest.TestCase):
    """Test the CLI entry point via subprocess with an isolated DEV_TEAM_DIR."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._env = {**os.environ, "DEV_TEAM_DIR": self._tmpdir.name}
        self._script = str(SCRIPTS_DIR / "knowledge_store.py")

    def tearDown(self):
        self._tmpdir.cleanup()

    def _run(self, *args, expect_success=True):
        result = subprocess.run(
            [sys.executable, self._script, *args],
            capture_output=True,
            text=True,
            env=self._env,
        )
        if expect_success:
            self.assertEqual(
                result.returncode, 0, f"CLI failed: {result.stdout}\n{result.stderr}"
            )
        return result

    def test_cli_no_args_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, self._script],
            capture_output=True,
            text=True,
            env=self._env,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_cli_add(self):
        result = self._run(
            "add",
            "CLI Title",
            "convention",
            "CLI content",
            "CLI summary",
            "tag1,tag2",
            "coder",
        )
        self.assertIn("know_001", result.stdout)

    def test_cli_get(self):
        self._run("add", "Get Test", "convention", "content", "summary", "t", "coder")
        result = self._run("get", "know_001")
        data = json.loads(result.stdout)
        self.assertEqual(data["title"], "Get Test")

    def test_cli_get_nonexistent_exits_nonzero(self):
        result = self._run("get", "know_999", expect_success=False)
        self.assertNotEqual(result.returncode, 0)

    def test_cli_stats(self):
        result = self._run("stats")
        data = json.loads(result.stdout)
        self.assertIn("total_entries", data)

    def test_cli_list_empty(self):
        result = self._run("list")
        data = json.loads(result.stdout)
        self.assertEqual(data, [])

    def test_cli_list_after_add(self):
        self._run("add", "A", "convention", "c", "s", "t", "coder")
        self._run("add", "B", "architecture", "c", "s", "t", "architect")
        result = self._run("list")
        data = json.loads(result.stdout)
        self.assertEqual(len(data), 2)

    def test_cli_list_with_category_filter(self):
        self._run("add", "A", "convention", "c", "s", "t", "coder")
        self._run("add", "B", "architecture", "c", "s", "t", "architect")
        result = self._run("list", "--category", "convention")
        data = json.loads(result.stdout)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["category"], "convention")

    def test_cli_update(self):
        self._run("add", "Old", "convention", "c", "s", "t", "coder")
        self._run("update", "know_001", "--title", "New")
        result = self._run("get", "know_001")
        data = json.loads(result.stdout)
        self.assertEqual(data["title"], "New")

    def test_cli_deprecate(self):
        self._run("add", "Old", "convention", "c", "s", "t", "coder")
        self._run("add", "New", "convention", "c", "s", "t", "coder")
        result = self._run("deprecate", "know_001", "know_002")
        self.assertIn("Deprecated", result.stdout)

    def test_cli_tag(self):
        self._run("add", "T", "convention", "c", "s", "old", "coder")
        self._run("tag", "know_001", "newtag1,newtag2")
        result = self._run("get", "know_001")
        data = json.loads(result.stdout)
        self.assertIn("newtag1", data["tags"])

    def test_cli_link_task(self):
        self._run("add", "T", "convention", "c", "s", "t", "coder")
        self._run("link-task", "know_001", "task_007")
        result = self._run("get", "know_001")
        data = json.loads(result.stdout)
        self.assertIn("task_007", data["related_tasks"])

    def test_cli_for_agent(self):
        self._run("add", "Pattern thing", "pattern", "c", "s", "t", "coder")
        result = self._run("for-agent", "coder")
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)

    def test_cli_search(self):
        self._run("add", "Atomic writes", "convention", "c", "s", "atomic", "coder")
        result = self._run("search", "atomic")
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)
        self.assertTrue(any("Atomic" in r["title"] for r in data))

    def test_cli_search_with_category(self):
        self._run("add", "Sec entry", "security", "c", "s", "sec", "security")
        self._run("add", "Conv entry", "convention", "c", "s", "conv", "coder")
        result = self._run("search", "", "--category", "security")
        data = json.loads(result.stdout)
        self.assertTrue(all(r["category"] == "security" for r in data))

    def test_cli_unknown_command_exits_nonzero(self):
        result = self._run("foobar", expect_success=False)
        self.assertNotEqual(result.returncode, 0)


# ===========================================================================
# seed_knowledge tests
# ===========================================================================


class TestSeedKnowledge(unittest.TestCase):
    """Tests for seed_knowledge.py seeding logic."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._orig_env = os.environ.get("DEV_TEAM_DIR")
        os.environ["DEV_TEAM_DIR"] = self._tmpdir.name
        self._seed_mod = load_module("seed_knowledge")
        self._ks_mod = load_module("knowledge_store")
        self._store = self._ks_mod.KnowledgeStore()

    def tearDown(self):
        if self._orig_env is None:
            os.environ.pop("DEV_TEAM_DIR", None)
        else:
            os.environ["DEV_TEAM_DIR"] = self._orig_env
        self._tmpdir.cleanup()

    def _fresh_store(self):
        return self._ks_mod.KnowledgeStore()

    def test_seed_populates_store(self):
        count = self._seed_mod.seed(dry_run=False, force=False)
        expected = len(self._seed_mod.SEED_ENTRIES)
        self.assertEqual(count, expected)
        all_entries = self._fresh_store().list_all(limit=1000)
        self.assertEqual(len(all_entries), expected)

    def test_seed_dry_run_does_not_write(self):
        count = self._seed_mod.seed(dry_run=True, force=False)
        expected = len(self._seed_mod.SEED_ENTRIES)
        self.assertEqual(count, expected)
        # Nothing actually written
        all_entries = self._fresh_store().list_all(limit=1000)
        self.assertEqual(len(all_entries), 0)

    def test_seed_skips_when_already_populated(self):
        # First seed
        self._seed_mod.seed(dry_run=False, force=False)
        # Second seed without force — should skip
        count = self._seed_mod.seed(dry_run=False, force=False)
        self.assertEqual(count, 0)

    def test_seed_force_adds_more_entries(self):
        self._seed_mod.seed(dry_run=False, force=False)
        initial = len(self._fresh_store().list_all(limit=1000))
        # Force re-seed adds more (duplicates are allowed by design)
        self._seed_mod.seed(dry_run=False, force=True)
        after_force = len(self._fresh_store().list_all(limit=1000))
        self.assertGreater(after_force, initial)

    def test_seed_entries_are_valid(self):
        """Every seed entry must be accepted by add_entry without raising."""
        self._seed_mod.seed(dry_run=False, force=False)
        all_entries = self._fresh_store().list_all(limit=1000)
        self.assertEqual(len(all_entries), len(self._seed_mod.SEED_ENTRIES))

    def test_seed_entries_have_required_fields(self):
        for entry in self._seed_mod.SEED_ENTRIES:
            for field in (
                "title",
                "category",
                "content",
                "summary",
                "tags",
                "agent_author",
            ):
                self.assertIn(
                    field,
                    entry,
                    f"Missing field '{field}' in seed entry: {entry['title']}",
                )

    def test_seed_entries_all_have_valid_categories(self):
        valid = self._ks_mod.KnowledgeStore.VALID_CATEGORIES
        for entry in self._seed_mod.SEED_ENTRIES:
            self.assertIn(
                entry["category"],
                valid,
                f"Invalid category in seed entry: {entry['title']}",
            )

    def test_seed_entries_all_have_valid_confidence(self):
        valid = self._ks_mod.KnowledgeStore.VALID_CONFIDENCES
        for entry in self._seed_mod.SEED_ENTRIES:
            conf = entry.get("confidence", "high")
            self.assertIn(
                conf, valid, f"Invalid confidence in seed entry: {entry['title']}"
            )

    def test_seed_entries_tags_are_lists(self):
        for entry in self._seed_mod.SEED_ENTRIES:
            self.assertIsInstance(
                entry["tags"], list, f"Tags must be a list in: {entry['title']}"
            )

    def test_seed_returns_correct_count(self):
        count = self._seed_mod.seed(dry_run=False, force=False)
        self.assertEqual(count, len(self._seed_mod.SEED_ENTRIES))

    def test_seed_dry_run_returns_correct_count(self):
        count = self._seed_mod.seed(dry_run=True, force=False)
        self.assertEqual(count, len(self._seed_mod.SEED_ENTRIES))


class TestSeedKnowledgeCLI(unittest.TestCase):
    """Test seed_knowledge.py CLI flags via subprocess."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._env = {**os.environ, "DEV_TEAM_DIR": self._tmpdir.name}
        self._script = str(SCRIPTS_DIR / "seed_knowledge.py")

    def tearDown(self):
        self._tmpdir.cleanup()

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, self._script, *args],
            capture_output=True,
            text=True,
            env=self._env,
        )

    def test_cli_seed_exits_zero(self):
        result = self._run()
        self.assertEqual(result.returncode, 0)

    def test_cli_dry_run_flag(self):
        result = self._run("--dry-run")
        self.assertIn("DRY RUN", result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_cli_dry_run_prints_would_add(self):
        result = self._run("--dry-run")
        self.assertIn("Would add", result.stdout)

    def test_cli_already_seeded_exits_zero(self):
        self._run()  # first seed
        result = self._run()  # second — should skip, still exit 0
        self.assertEqual(result.returncode, 0)

    def test_cli_force_flag_exits_zero(self):
        self._run()  # seed once
        result = self._run("--force")
        self.assertEqual(result.returncode, 0)

    def test_cli_help_flag(self):
        result = self._run("--help")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(len(result.stdout) > 0)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
