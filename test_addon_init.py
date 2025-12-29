"""
Quick test to verify the add-on initialization structure
"""

def test_init_structure():
    """Test that __init__.py has correct structure"""
    import sys
    import os
    
    # Read the __init__.py file
    init_file = os.path.join(os.path.dirname(__file__), '__init__.py')
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify it imports init_addon
    assert 'from .template_designer import init_addon' in content, \
        "__init__.py should import init_addon"
    
    # Verify it calls init_addon
    assert 'init_addon()' in content, \
        "__init__.py should call init_addon()"
    
    print("✅ __init__.py structure is correct")


def test_template_designer_structure():
    """Test that template_designer.py has correct structure"""
    import sys
    import os
    
    # Read the template_designer.py file
    td_file = os.path.join(os.path.dirname(__file__), 'template_designer.py')
    with open(td_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verify setup_menu function exists
    assert 'def setup_menu():' in content, \
        "setup_menu function should exist"
    
    # Verify it adds to Tools menu
    assert 'mw.form.menuTools.addAction(action)' in content, \
        "Should add action to Tools menu"
    
    # Verify init_addon exists
    assert 'def init_addon():' in content, \
        "init_addon function should exist"
    
    # Verify init_addon calls setup_menu
    assert 'setup_menu()' in content, \
        "init_addon should call setup_menu"
    
    # Verify no duplicate function definitions
    function_count = content.count('def show_template_designer_for_note_type(')
    assert function_count == 1, \
        f"show_template_designer_for_note_type should be defined once, found {function_count}"
    
    # Verify no standalone init_addon() call at module level
    lines = content.split('\n')
    standalone_calls = [line for line in lines 
                       if line.strip() == 'init_addon()' 
                       and not line.strip().startswith('#')]
    assert len(standalone_calls) == 0, \
        "init_addon() should not be called at module level in template_designer.py"
    
    print("✅ template_designer.py structure is correct")


if __name__ == '__main__':
    test_init_structure()
    test_template_designer_structure()
    print("\n✅ All checks passed! The menu should now appear under Tools.")
