"""
Tests for command system (undo/redo functionality).
"""

import pytest
from ui.commands import (
    Command, AddComponentCommand, RemoveComponentCommand,
    MoveComponentCommand, ResizeComponentCommand, ModifyPropertyCommand,
    CommandHistory
)
from ui.components import Component, TextFieldComponent, ComponentType


class TestCommand:
    """Test Command base class"""
    
    def test_command_is_abstract(self):
        """Test that Command class is abstract"""
        with pytest.raises(TypeError):
            Command()


class TestAddComponentCommand:
    """Test AddComponentCommand"""
    
    def test_add_component_execute(self):
        """Test adding a component"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        component = TextFieldComponent("TestField")
        
        cmd = AddComponentCommand(component, parent)
        cmd.execute()
        
        assert len(parent.children) == 1
        assert parent.children[0] == component
    
    def test_add_component_undo(self):
        """Test undoing component addition"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        component = TextFieldComponent("TestField")
        
        cmd = AddComponentCommand(component, parent)
        cmd.execute()
        cmd.undo()
        
        assert len(parent.children) == 0
    
    def test_add_component_with_parent(self):
        """Test adding a component with parent"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        child = TextFieldComponent("Child")
        
        # Add child to parent
        child_cmd = AddComponentCommand(child, parent, 0)
        child_cmd.execute()
        
        assert len(parent.children) == 1
        assert parent.children[0] == child
    
    def test_add_component_description(self):
        """Test command description"""
        component = TextFieldComponent("TestField")
        cmd = AddComponentCommand(component, None)
        
        description = cmd.get_description()
        assert "Add" in description


class TestRemoveComponentCommand:
    """Test RemoveComponentCommand"""
    
    def test_remove_component_execute(self):
        """Test removing a component"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        component = TextFieldComponent("TestField")
        parent.children.append(component)
        component.parent = parent
        
        cmd = RemoveComponentCommand(component)
        cmd.execute()
        
        assert len(parent.children) == 0
    
    def test_remove_component_undo(self):
        """Test undoing component removal"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        component = TextFieldComponent("TestField")
        parent.children.append(component)
        component.parent = parent
        
        cmd = RemoveComponentCommand(component)
        cmd.execute()
        cmd.undo()
        
        assert len(parent.children) == 1
        assert parent.children[0] == component
    
    def test_remove_component_with_children(self):
        """Test removing a component with children"""
        from ui.components import ContainerComponent
        root = ContainerComponent()
        parent = ContainerComponent()
        child = TextFieldComponent("Child")
        parent.children.append(child)
        root.children.append(parent)
        parent.parent = root
        
        cmd = RemoveComponentCommand(parent)
        cmd.execute()
        cmd.undo()
        
        # Should restore with children
        assert len(root.children) == 1
        assert len(root.children[0].children) == 1


class TestMoveComponentCommand:
    """Test MoveComponentCommand"""
    
    def test_move_component_execute(self):
        """Test moving a component"""
        component = TextFieldComponent("TestField")
        component.x = 10
        component.y = 20
        
        cmd = MoveComponentCommand(component, 100, 200)
        cmd.execute()
        
        assert component.x == 100
        assert component.y == 200
    
    def test_move_component_undo(self):
        """Test undoing component move"""
        component = TextFieldComponent("TestField")
        component.x = 10
        component.y = 20
        
        cmd = MoveComponentCommand(component, 100, 200)
        cmd.execute()
        cmd.undo()
        
        assert component.x == 10
        assert component.y == 20


class TestResizeComponentCommand:
    """Test ResizeComponentCommand"""
    
    def test_resize_component_execute(self):
        """Test resizing a component"""
        component = TextFieldComponent("TestField")
        component.width = 100
        component.height = 50
        
        cmd = ResizeComponentCommand(component, 200, 100)
        cmd.execute()
        
        assert component.width == 200
        assert component.height == 100
    
    def test_resize_component_undo(self):
        """Test undoing component resize"""
        component = TextFieldComponent("TestField")
        component.width = 100
        component.height = 50
        
        cmd = ResizeComponentCommand(component, 200, 100)
        cmd.execute()
        cmd.undo()
        
        assert component.width == 100
        assert component.height == 50


class TestModifyPropertyCommand:
    """Test ModifyPropertyCommand"""
    
    def test_modify_property_execute(self):
        """Test modifying a component property"""
        component = TextFieldComponent("TestField")
        component.font_size = 12
        
        cmd = ModifyPropertyCommand(component, 'font_size', 16)
        cmd.execute()
        
        assert component.font_size == 16
    
    def test_modify_property_undo(self):
        """Test undoing property modification"""
        component = TextFieldComponent("TestField")
        component.font_size = 12
        
        cmd = ModifyPropertyCommand(component, 'font_size', 16)
        cmd.execute()
        cmd.undo()
        
        assert component.font_size == 12


class TestCommandHistory:
    """Test CommandHistory"""
    
    def test_execute_command(self):
        """Test executing a command"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        component = TextFieldComponent("TestField")
        
        history = CommandHistory()
        cmd = AddComponentCommand(component, parent)
        
        history.execute(cmd)
        
        assert len(parent.children) == 1
        assert history.can_undo()
        assert not history.can_redo()
    
    def test_undo_command(self):
        """Test undoing a command"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        component = TextFieldComponent("TestField")
        
        history = CommandHistory()
        cmd = AddComponentCommand(component, parent)
        
        history.execute(cmd)
        history.undo()
        
        assert len(parent.children) == 0
        assert not history.can_undo()
        assert history.can_redo()
    
    def test_redo_command(self):
        """Test redoing a command"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        component = TextFieldComponent("TestField")
        
        history = CommandHistory()
        cmd = AddComponentCommand(component, parent)
        
        history.execute(cmd)
        history.undo()
        history.redo()
        
        assert len(parent.children) == 1
        assert history.can_undo()
        assert not history.can_redo()
    
    def test_history_size_limit(self):
        """Test command history size limit"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        history = CommandHistory(max_history=3)
        
        # Add 5 commands
        for i in range(5):
            component = TextFieldComponent(f"Field{i}")
            cmd = AddComponentCommand(component, parent)
            history.execute(cmd)
        
        # Should only have 3 in history
        # Undo 3 times should work, 4th should not
        history.undo()  # 1
        history.undo()  # 2
        history.undo()  # 3
        assert not history.can_undo()  # Can't undo more
    
    def test_clear_redo_on_new_command(self):
        """Test that redo stack is cleared when executing new command"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        history = CommandHistory()
        
        # Execute two commands
        cmd1 = AddComponentCommand(TextFieldComponent("Field1"), parent)
        cmd2 = AddComponentCommand(TextFieldComponent("Field2"), parent)
        history.execute(cmd1)
        history.execute(cmd2)
        
        # Undo one
        history.undo()
        assert history.can_redo()
        
        # Execute new command
        cmd3 = AddComponentCommand(TextFieldComponent("Field3"), parent)
        history.execute(cmd3)
        
        # Redo should now be empty
        assert not history.can_redo()
    
    def test_undo_description(self):
        """Test getting undo description"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        history = CommandHistory()
        
        component = TextFieldComponent("TestField")
        cmd = AddComponentCommand(component, parent)
        history.execute(cmd)
        
        description = history.get_undo_description()
        assert description is not None
        assert "Add" in description
    
    def test_redo_description(self):
        """Test getting redo description"""
        from ui.components import ContainerComponent
        parent = ContainerComponent()
        history = CommandHistory()
        
        component = TextFieldComponent("TestField")
        cmd = AddComponentCommand(component, parent)
        history.execute(cmd)
        history.undo()
        
        description = history.get_redo_description()
        assert description is not None
        assert "Add" in description
