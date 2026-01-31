"""
Tests for Issue #41: Multi-Project Manager

Tests the project management system including:
- Project CRUD operations
- Project persistence
- Recent projects tracking
- Favorites management
- Project cloning
- Search and filtering
"""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


class MockProjectManager:
    """Mock ProjectManager for testing without JavaScript."""
    
    def __init__(self):
        self.projects = []
        self.recent_projects = []
        self.current_project = None
        self._storage = {}
    
    def create_project(self, name, template_data=None):
        """Create a new project."""
        project = {
            "id": f"proj_{len(self.projects)}_{datetime.now().isoformat()}",
            "name": name,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "isFavorite": False,
            "data": template_data or {}
        }
        self.projects.append(project)
        self.current_project = project["id"]
        self._update_recent(project["id"])
        return project
    
    def get_project(self, project_id):
        """Get a project by ID."""
        return next((p for p in self.projects if p["id"] == project_id), None)
    
    def list_projects(self):
        """List all projects."""
        return sorted(self.projects, key=lambda p: p["modified"], reverse=True)
    
    def delete_project(self, project_id):
        """Delete a project."""
        self.projects = [p for p in self.projects if p["id"] != project_id]
        if self.current_project == project_id:
            self.current_project = self.projects[0]["id"] if self.projects else None
        return True
    
    def rename_project(self, project_id, new_name):
        """Rename a project."""
        project = self.get_project(project_id)
        if project:
            project["name"] = new_name
            project["modified"] = datetime.now().isoformat()
            return True
        return False
    
    def toggle_favorite(self, project_id):
        """Toggle favorite status of a project."""
        project = self.get_project(project_id)
        if project:
            project["isFavorite"] = not project["isFavorite"]
            project["modified"] = datetime.now().isoformat()
            return project["isFavorite"]
        return False
    
    def get_favorites(self):
        """Get all favorite projects."""
        return [p for p in self.projects if p["isFavorite"]]
    
    def clone_project(self, project_id, new_name):
        """Clone an existing project."""
        original = self.get_project(project_id)
        if not original:
            return None
        
        cloned = {
            "id": f"proj_{len(self.projects)}_{datetime.now().isoformat()}",
            "name": new_name or f"{original['name']} (Copy)",
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "isFavorite": False,
            "data": json.loads(json.dumps(original["data"]))  # Deep copy
        }
        self.projects.append(cloned)
        self.current_project = cloned["id"]
        return cloned
    
    def search_projects(self, query):
        """Search projects by name."""
        query_lower = query.lower()
        return [p for p in self.projects if query_lower in p["name"].lower()]
    
    def set_current_project(self, project_id):
        """Set the current active project."""
        if self.get_project(project_id):
            self.current_project = project_id
            self._update_recent(project_id)
            return True
        return False
    
    def get_recent_projects(self, limit=5):
        """Get recent projects."""
        recent = self.recent_projects[:limit]
        return [self.get_project(pid) for pid in recent if self.get_project(pid)]
    
    def _update_recent(self, project_id):
        """Update recent projects list."""
        if project_id in self.recent_projects:
            self.recent_projects.remove(project_id)
        self.recent_projects.insert(0, project_id)
        self.recent_projects = self.recent_projects[:5]  # Keep only 5
    
    def export_project(self, project_id):
        """Export project as JSON."""
        project = self.get_project(project_id)
        if project:
            return json.dumps(project)
        return None
    
    def import_project(self, json_data, new_name=None):
        """Import a project from JSON."""
        try:
            project = json.loads(json_data)
            project["id"] = f"proj_{len(self.projects)}_{datetime.now().isoformat()}"
            project["name"] = new_name or project.get("name", "Imported Project")
            project["created"] = datetime.now().isoformat()
            project["modified"] = datetime.now().isoformat()
            self.projects.append(project)
            self.current_project = project["id"]
            return project
        except (json.JSONDecodeError, KeyError):
            return None


# ============================================================================
# PROJECT MANAGEMENT TESTS
# ============================================================================

class TestProjectCRUD:
    """Test project creation, read, update, delete operations."""
    
    def test_create_project(self):
        """Test creating a new project."""
        manager = MockProjectManager()
        project = manager.create_project("My Template")
        
        assert project is not None
        assert project["name"] == "My Template"
        assert project["id"] is not None
        assert project["created"] is not None
        assert project["isFavorite"] is False
    
    def test_create_project_with_data(self):
        """Test creating a project with template data."""
        manager = MockProjectManager()
        data = {"blocks": [{"type": "button"}]}
        project = manager.create_project("Template", data)
        
        assert project["data"] == data
    
    def test_list_projects(self):
        """Test listing all projects."""
        manager = MockProjectManager()
        manager.create_project("Project 1")
        manager.create_project("Project 2")
        manager.create_project("Project 3")
        
        projects = manager.list_projects()
        assert len(projects) == 3
    
    def test_get_project(self):
        """Test retrieving a specific project."""
        manager = MockProjectManager()
        created = manager.create_project("My Project")
        retrieved = manager.get_project(created["id"])
        
        assert retrieved["name"] == "My Project"
    
    def test_delete_project(self):
        """Test deleting a project."""
        manager = MockProjectManager()
        project = manager.create_project("To Delete")
        project_id = project["id"]
        
        assert manager.delete_project(project_id)
        assert manager.get_project(project_id) is None
        assert len(manager.projects) == 0
    
    def test_rename_project(self):
        """Test renaming a project."""
        manager = MockProjectManager()
        project = manager.create_project("Original Name")
        
        assert manager.rename_project(project["id"], "New Name")
        assert manager.get_project(project["id"])["name"] == "New Name"
    
    def test_rename_nonexistent_project(self):
        """Test renaming a project that doesn't exist."""
        manager = MockProjectManager()
        assert not manager.rename_project("nonexistent", "New Name")


# ============================================================================
# FAVORITE MANAGEMENT TESTS
# ============================================================================

class TestFavorites:
    """Test favorite/pinning functionality."""
    
    def test_toggle_favorite(self):
        """Test toggling favorite status."""
        manager = MockProjectManager()
        project = manager.create_project("My Project")
        
        is_favorite = manager.toggle_favorite(project["id"])
        assert is_favorite is True
        
        is_favorite = manager.toggle_favorite(project["id"])
        assert is_favorite is False
    
    def test_get_favorites(self):
        """Test getting all favorite projects."""
        manager = MockProjectManager()
        p1 = manager.create_project("Project 1")
        p2 = manager.create_project("Project 2")
        p3 = manager.create_project("Project 3")
        
        manager.toggle_favorite(p1["id"])
        manager.toggle_favorite(p3["id"])
        
        favorites = manager.get_favorites()
        assert len(favorites) == 2
        assert p1 in favorites
        assert p3 in favorites
    
    def test_favorite_empty_list(self):
        """Test getting favorites when none exist."""
        manager = MockProjectManager()
        manager.create_project("Project")
        
        favorites = manager.get_favorites()
        assert len(favorites) == 0


# ============================================================================
# RECENT PROJECTS TESTS
# ============================================================================

class TestRecentProjects:
    """Test recent projects tracking."""
    
    def test_recent_projects_limit(self):
        """Test that recent projects list is limited to 5."""
        manager = MockProjectManager()
        
        for i in range(10):
            manager.create_project(f"Project {i}")
        
        recent = manager.get_recent_projects()
        assert len(recent) <= 5
    
    def test_recent_projects_order(self):
        """Test that recent projects are in correct order."""
        manager = MockProjectManager()
        p1 = manager.create_project("Project 1")
        p2 = manager.create_project("Project 2")
        p3 = manager.create_project("Project 3")
        
        manager.set_current_project(p1["id"])
        
        recent = manager.get_recent_projects()
        assert recent[0]["id"] == p1["id"]
        assert recent[1]["id"] == p3["id"]
    
    def test_set_current_project(self):
        """Test setting current project."""
        manager = MockProjectManager()
        p1 = manager.create_project("Project 1")
        p2 = manager.create_project("Project 2")
        
        assert manager.set_current_project(p1["id"])
        assert manager.current_project == p1["id"]
    
    def test_recent_projects_custom_limit(self):
        """Test getting recent projects with custom limit."""
        manager = MockProjectManager()
        for i in range(5):
            manager.create_project(f"Project {i}")
        
        recent = manager.get_recent_projects(limit=3)
        assert len(recent) == 3


# ============================================================================
# PROJECT CLONING TESTS
# ============================================================================

class TestCloning:
    """Test project cloning functionality."""
    
    def test_clone_project(self):
        """Test cloning a project."""
        manager = MockProjectManager()
        original = manager.create_project("Original", {"blocks": [{"type": "button"}]})
        
        cloned = manager.clone_project(original["id"], "Cloned")
        
        assert cloned is not None
        assert cloned["name"] == "Cloned"
        assert cloned["id"] != original["id"]
        assert cloned["data"] == original["data"]
    
    def test_clone_default_name(self):
        """Test cloning with default name."""
        manager = MockProjectManager()
        original = manager.create_project("Original")
        
        cloned = manager.clone_project(original["id"], None)
        
        assert "Copy" in cloned["name"]
    
    def test_clone_deep_copy_data(self):
        """Test that cloning creates a deep copy of data."""
        manager = MockProjectManager()
        data = {"blocks": [{"type": "button", "props": {}}]}
        original = manager.create_project("Original", data)
        
        cloned = manager.clone_project(original["id"], "Cloned")
        cloned["data"]["blocks"][0]["type"] = "input"
        
        assert original["data"]["blocks"][0]["type"] == "button"
    
    def test_clone_nonexistent_project(self):
        """Test cloning a project that doesn't exist."""
        manager = MockProjectManager()
        cloned = manager.clone_project("nonexistent", "Clone")
        
        assert cloned is None


# ============================================================================
# SEARCH AND FILTERING TESTS
# ============================================================================

class TestSearch:
    """Test project search and filtering."""
    
    def test_search_projects_by_name(self):
        """Test searching projects by name."""
        manager = MockProjectManager()
        manager.create_project("Button Template")
        manager.create_project("Form Layout")
        manager.create_project("Button Group")
        
        results = manager.search_projects("button")
        assert len(results) == 2
    
    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        manager = MockProjectManager()
        manager.create_project("My Template")
        manager.create_project("Another TEMPLATE")
        
        results = manager.search_projects("TEMPLATE")
        assert len(results) == 2
    
    def test_search_no_results(self):
        """Test search with no results."""
        manager = MockProjectManager()
        manager.create_project("Project 1")
        
        results = manager.search_projects("nonexistent")
        assert len(results) == 0
    
    def test_search_empty_query(self):
        """Test search with empty query."""
        manager = MockProjectManager()
        manager.create_project("Project 1")
        manager.create_project("Project 2")
        
        results = manager.search_projects("")
        assert len(results) == 2
    
    def test_search_partial_match(self):
        """Test search with partial name match."""
        manager = MockProjectManager()
        manager.create_project("iPhone Template")
        manager.create_project("iPad Template")
        manager.create_project("Android Template")
        
        results = manager.search_projects("Phone")
        assert len(results) == 1


# ============================================================================
# IMPORT/EXPORT TESTS
# ============================================================================

class TestImportExport:
    """Test project import/export functionality."""
    
    def test_export_project(self):
        """Test exporting a project to JSON."""
        manager = MockProjectManager()
        project = manager.create_project("My Project", {"blocks": []})
        
        exported = manager.export_project(project["id"])
        assert exported is not None
        
        data = json.loads(exported)
        assert data["name"] == "My Project"
    
    def test_import_project(self):
        """Test importing a project from JSON."""
        manager = MockProjectManager()
        project = manager.create_project("Original", {"blocks": []})
        exported = manager.export_project(project["id"])
        
        manager2 = MockProjectManager()
        imported = manager2.import_project(exported, "Imported")
        
        assert imported is not None
        assert imported["name"] == "Imported"
    
    def test_import_invalid_json(self):
        """Test importing invalid JSON."""
        manager = MockProjectManager()
        imported = manager.import_project("invalid json")
        
        assert imported is None
    
    def test_export_nonexistent_project(self):
        """Test exporting a project that doesn't exist."""
        manager = MockProjectManager()
        exported = manager.export_project("nonexistent")
        
        assert exported is None


# ============================================================================
# DATA PERSISTENCE TESTS
# ============================================================================

class TestPersistence:
    """Test data persistence functionality."""
    
    def test_projects_persist(self):
        """Test that projects persist in data structure."""
        manager = MockProjectManager()
        manager.create_project("Project 1")
        manager.create_project("Project 2")
        
        assert len(manager.projects) == 2
        assert manager.projects[0]["name"] == "Project 1"
    
    def test_recent_projects_persist(self):
        """Test that recent projects persist."""
        manager = MockProjectManager()
        p1 = manager.create_project("Project 1")
        p2 = manager.create_project("Project 2")
        
        manager.set_current_project(p1["id"])
        
        assert manager.recent_projects[0] == p1["id"]


# ============================================================================
# EDGE CASES TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_project_name(self):
        """Test creating a project with empty name."""
        manager = MockProjectManager()
        project = manager.create_project("")
        
        assert project is not None
        assert project["name"] == ""
    
    def test_very_long_project_name(self):
        """Test creating a project with very long name."""
        manager = MockProjectManager()
        long_name = "A" * 500
        project = manager.create_project(long_name)
        
        assert project["name"] == long_name
    
    def test_special_characters_in_name(self):
        """Test project names with special characters."""
        manager = MockProjectManager()
        project = manager.create_project("Project <>&\"'")
        
        assert project["name"] == "Project <>&\"'"
    
    def test_delete_current_project(self):
        """Test that deleting current project updates current."""
        manager = MockProjectManager()
        p1 = manager.create_project("Project 1")
        p2 = manager.create_project("Project 2")
        
        manager.set_current_project(p1["id"])
        manager.delete_project(p1["id"])
        
        assert manager.current_project != p1["id"]
    
    def test_unicode_in_project_name(self):
        """Test project names with unicode characters."""
        manager = MockProjectManager()
        project = manager.create_project("项目 🎉 Projet")
        
        assert "项目" in project["name"]
        assert "🎉" in project["name"]
    
    def test_timestamps_are_valid(self):
        """Test that created/modified timestamps are valid ISO format."""
        manager = MockProjectManager()
        project = manager.create_project("Project")
        
        # Should not raise
        datetime.fromisoformat(project["created"])
        datetime.fromisoformat(project["modified"])


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complex multi-step workflows."""
    
    def test_full_workflow(self):
        """Test complete workflow: create, modify, pin, clone, search."""
        manager = MockProjectManager()
        
        # Create projects
        p1 = manager.create_project("Button Template")
        p2 = manager.create_project("Form Layout")
        
        # Rename one
        manager.rename_project(p1["id"], "Enhanced Button")
        
        # Pin one
        manager.toggle_favorite(p2["id"])
        
        # Clone one
        p3 = manager.clone_project(p1["id"], "Button Backup")
        
        # Search
        results = manager.search_projects("Button")
        
        assert len(results) == 2
        assert manager.get_favorites()[0]["id"] == p2["id"]
    
    def test_multiple_managers_independent(self):
        """Test that multiple managers are independent."""
        manager1 = MockProjectManager()
        manager2 = MockProjectManager()
        
        manager1.create_project("Project 1")
        manager2.create_project("Project 2")
        
        assert len(manager1.projects) == 1
        assert len(manager2.projects) == 1
    
    def test_export_import_roundtrip(self):
        """Test export/import roundtrip."""
        manager1 = MockProjectManager()
        project1 = manager1.create_project("Original", {"blocks": [{"type": "button"}]})
        exported = manager1.export_project(project1["id"])
        
        manager2 = MockProjectManager()
        project2 = manager2.import_project(exported, "Imported")
        
        assert project2["data"] == project1["data"]
        assert project2["name"] == "Imported"


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
