"""
Tests for note type service.

Plan 11: Tests for NoteTypeService and Anki integration.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from anki_template_designer.services.note_type_service import (
    AnkiField,
    CardTemplate,
    NoteType,
    NoteTypeService,
    get_note_type_service,
    init_note_type_service
)


class TestAnkiField:
    """Tests for AnkiField class."""
    
    def test_default_values(self):
        """Test default field values."""
        field = AnkiField(name="Front", ordinal=0)
        assert field.name == "Front"
        assert field.ordinal == 0
        assert field.sticky is False
        assert field.font == "Arial"
        assert field.size == 20
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        field = AnkiField(name="Back", ordinal=1, rtl=True)
        d = field.to_dict()
        assert d["name"] == "Back"
        assert d["ordinal"] == 1
        assert d["rtl"] is True
    
    def test_from_anki_field(self):
        """Test creation from Anki field dict."""
        anki_dict = {
            "name": "Definition",
            "sticky": True,
            "font": "Times",
            "size": 18
        }
        field = AnkiField.from_anki_field(anki_dict, ordinal=2)
        assert field.name == "Definition"
        assert field.ordinal == 2
        assert field.sticky is True
        assert field.font == "Times"


class TestCardTemplate:
    """Tests for CardTemplate class."""
    
    def test_default_values(self):
        """Test default template values."""
        tmpl = CardTemplate(
            name="Card 1",
            ordinal=0,
            front="{{Front}}",
            back="{{FrontSide}}<hr>{{Back}}"
        )
        assert tmpl.name == "Card 1"
        assert tmpl.ordinal == 0
        assert "{{Front}}" in tmpl.front
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        tmpl = CardTemplate(
            name="Reversed",
            ordinal=1,
            front="{{Back}}",
            back="{{Front}}"
        )
        d = tmpl.to_dict()
        assert d["name"] == "Reversed"
        assert d["ordinal"] == 1
        assert d["front"] == "{{Back}}"
    
    def test_from_anki_template(self):
        """Test creation from Anki template dict."""
        anki_dict = {
            "name": "Forward",
            "qfmt": "<div>{{Question}}</div>",
            "afmt": "{{FrontSide}}<hr>{{Answer}}",
            "bfont": "Arial",
            "bsize": 12
        }
        tmpl = CardTemplate.from_anki_template(anki_dict, ordinal=0)
        assert tmpl.name == "Forward"
        assert "{{Question}}" in tmpl.front
        assert "{{Answer}}" in tmpl.back


class TestNoteType:
    """Tests for NoteType class."""
    
    def test_basic_creation(self):
        """Test basic note type creation."""
        nt = NoteType(
            id=12345,
            name="Basic",
            fields=[
                AnkiField(name="Front", ordinal=0),
                AnkiField(name="Back", ordinal=1)
            ],
            templates=[
                CardTemplate(name="Card 1", ordinal=0, front="{{Front}}", back="{{Back}}")
            ]
        )
        assert nt.id == 12345
        assert nt.name == "Basic"
        assert len(nt.fields) == 2
        assert len(nt.templates) == 1
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        nt = NoteType(
            id=123,
            name="Test",
            css=".card { font-size: 20px; }"
        )
        d = nt.to_dict()
        assert d["id"] == 123
        assert d["name"] == "Test"
        assert "font-size" in d["css"]
    
    def test_get_field_names(self):
        """Test getting field names."""
        nt = NoteType(
            id=1,
            name="Test",
            fields=[
                AnkiField(name="Word", ordinal=0),
                AnkiField(name="Definition", ordinal=1),
                AnkiField(name="Example", ordinal=2)
            ]
        )
        names = nt.get_field_names()
        assert names == ["Word", "Definition", "Example"]
    
    def test_get_template_names(self):
        """Test getting template names."""
        nt = NoteType(
            id=1,
            name="Test",
            templates=[
                CardTemplate(name="Forward", ordinal=0, front="", back=""),
                CardTemplate(name="Reverse", ordinal=1, front="", back="")
            ]
        )
        names = nt.get_template_names()
        assert names == ["Forward", "Reverse"]
    
    def test_from_anki_model(self):
        """Test creation from Anki model."""
        model = {
            "id": 999,
            "name": "Vocabulary",
            "flds": [
                {"name": "Term", "sticky": False, "font": "Arial", "size": 20},
                {"name": "Definition", "sticky": True, "font": "Arial", "size": 18}
            ],
            "tmpls": [
                {"name": "Card 1", "qfmt": "{{Term}}", "afmt": "{{Definition}}"}
            ],
            "css": ".card { color: blue; }",
            "sortf": 0
        }
        nt = NoteType.from_anki_model(model)
        assert nt.id == 999
        assert nt.name == "Vocabulary"
        assert len(nt.fields) == 2
        assert nt.fields[0].name == "Term"
        assert nt.fields[1].sticky is True
        assert len(nt.templates) == 1


class TestNoteTypeService:
    """Tests for NoteTypeService class."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = NoteTypeService()
        assert service._mw is None
        assert service._cache == {}
    
    def test_set_main_window(self):
        """Test setting main window."""
        service = NoteTypeService()
        mock_mw = Mock()
        service.set_main_window(mock_mw)
        assert service._mw is mock_mw
    
    def test_get_all_note_types_no_collection(self):
        """Test get_all_note_types with no collection."""
        service = NoteTypeService()
        result = service.get_all_note_types()
        assert result == []
    
    def test_get_all_note_types_with_mock(self):
        """Test get_all_note_types with mocked collection."""
        # Create mock
        mock_mw = Mock()
        mock_col = Mock()
        mock_mw.col = mock_col
        
        mock_col.models.all.return_value = [
            {
                "id": 1,
                "name": "Basic",
                "flds": [{"name": "Front"}, {"name": "Back"}],
                "tmpls": [{"name": "Card 1", "qfmt": "{{Front}}", "afmt": "{{Back}}"}],
                "css": "",
                "sortf": 0
            },
            {
                "id": 2,
                "name": "Cloze",
                "flds": [{"name": "Text"}, {"name": "Extra"}],
                "tmpls": [{"name": "Cloze", "qfmt": "{{cloze:Text}}", "afmt": "{{cloze:Text}}"}],
                "css": "",
                "sortf": 0
            }
        ]
        
        service = NoteTypeService(mock_mw)
        result = service.get_all_note_types()
        
        assert len(result) == 2
        assert result[0].name == "Basic"
        assert result[1].name == "Cloze"
    
    def test_get_note_type_from_cache(self):
        """Test getting note type from cache."""
        service = NoteTypeService()
        
        # Pre-populate cache
        nt = NoteType(id=100, name="Cached")
        service._cache[100] = nt
        
        result = service.get_note_type(100)
        assert result is nt
    
    def test_get_note_type_not_found(self):
        """Test getting non-existent note type."""
        mock_mw = Mock()
        mock_col = Mock()
        mock_mw.col = mock_col
        mock_col.models.get.return_value = None
        
        service = NoteTypeService(mock_mw)
        result = service.get_note_type(999)
        assert result is None
    
    def test_get_fields(self):
        """Test getting fields for a note type."""
        service = NoteTypeService()
        
        nt = NoteType(
            id=1,
            name="Test",
            fields=[
                AnkiField(name="F1", ordinal=0),
                AnkiField(name="F2", ordinal=1)
            ]
        )
        service._cache[1] = nt
        
        fields = service.get_fields(1)
        assert len(fields) == 2
        assert fields[0].name == "F1"
    
    def test_get_templates(self):
        """Test getting templates for a note type."""
        service = NoteTypeService()
        
        nt = NoteType(
            id=1,
            name="Test",
            templates=[
                CardTemplate(name="T1", ordinal=0, front="", back=""),
                CardTemplate(name="T2", ordinal=1, front="", back="")
            ]
        )
        service._cache[1] = nt
        
        templates = service.get_templates(1)
        assert len(templates) == 2
        assert templates[1].name == "T2"
    
    def test_get_css(self):
        """Test getting CSS for a note type."""
        service = NoteTypeService()
        
        nt = NoteType(id=1, name="Test", css=".card { color: red; }")
        service._cache[1] = nt
        
        css = service.get_css(1)
        assert "color: red" in css
    
    def test_get_sample_data(self):
        """Test getting sample data."""
        service = NoteTypeService()
        
        nt = NoteType(
            id=1,
            name="Test",
            fields=[
                AnkiField(name="Question", ordinal=0),
                AnkiField(name="Answer", ordinal=1)
            ]
        )
        service._cache[1] = nt
        
        sample = service.get_sample_data(1)
        assert sample["Question"] == "[Question]"
        assert sample["Answer"] == "[Answer]"
    
    def test_render_preview(self):
        """Test rendering a preview."""
        service = NoteTypeService()
        
        nt = NoteType(
            id=1,
            name="Test",
            fields=[
                AnkiField(name="Front", ordinal=0),
                AnkiField(name="Back", ordinal=1)
            ],
            templates=[
                CardTemplate(
                    name="Card 1",
                    ordinal=0,
                    front="<div>{{Front}}</div>",
                    back="{{FrontSide}}<hr id=answer><div>{{Back}}</div>"
                )
            ],
            css=".card { font-size: 20px; }"
        )
        service._cache[1] = nt
        
        preview = service.render_preview(1, 0, {"Front": "Hello", "Back": "World"})
        
        assert "Hello" in preview["front"]
        assert "World" in preview["back"]
        assert "Hello" in preview["back"]  # FrontSide replacement
        assert "css" in preview
    
    def test_update_template(self):
        """Test updating a template."""
        mock_mw = Mock()
        mock_col = Mock()
        mock_mw.col = mock_col
        
        model = {
            "id": 1,
            "name": "Test",
            "tmpls": [
                {"name": "Card 1", "qfmt": "old front", "afmt": "old back"}
            ]
        }
        mock_col.models.get.return_value = model
        
        service = NoteTypeService(mock_mw)
        result = service.update_template(1, 0, front="new front", back="new back")
        
        assert result is True
        assert model["tmpls"][0]["qfmt"] == "new front"
        assert model["tmpls"][0]["afmt"] == "new back"
        mock_col.models.save.assert_called_once_with(model)
    
    def test_update_css(self):
        """Test updating CSS."""
        mock_mw = Mock()
        mock_col = Mock()
        mock_mw.col = mock_col
        
        model = {"id": 1, "name": "Test", "css": "old css"}
        mock_col.models.get.return_value = model
        
        service = NoteTypeService(mock_mw)
        result = service.update_css(1, "new css")
        
        assert result is True
        assert model["css"] == "new css"
        mock_col.models.save.assert_called_once()


class TestGlobalFunctions:
    """Tests for global service functions."""
    
    def test_init_note_type_service(self):
        """Test initializing global service."""
        mock_mw = Mock()
        service = init_note_type_service(mock_mw)
        
        assert service is not None
        assert service._mw is mock_mw
    
    def test_get_note_type_service(self):
        """Test getting global service."""
        mock_mw = Mock()
        init_note_type_service(mock_mw)
        
        service = get_note_type_service()
        assert service is not None
