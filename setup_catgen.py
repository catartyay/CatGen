"""
Setup script to create all necessary __init__.py files for CatGen
Run this in your CatGen directory
"""

import os
from pathlib import Path

# Define directory structure
directories = [
    'core',
    'data',
    'ui',
    'ui/dialogs',
    'rendering',
    'resources',
    'utils'
]

# Create directories and __init__.py files
for directory in directories:
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    init_file = dir_path / '__init__.py'
    if not init_file.exists():
        init_file.touch()
        print(f"Created: {init_file}")
    else:
        print(f"Exists: {init_file}")

print("\n✓ Directory structure created!")
print("\nNext steps:")
print("1. Make sure you have the following files copied to their locations:")
print("   - main.py")
print("   - core/cat.py")
print("   - core/genetics_engine.py")
print("   - core/phenotype_calculator.py")
print("   - core/breeding.py")
print("   - data/registry.py")
print("   - ui/main_window.py")
print("   - ui/registry_tab.py")
print("   - ui/breeding_tab.py")
print("   - ui/generation_tab.py")
print("   - ui/admin_tab.py")
print("   - ui/dialogs/cat_details_dialog.py")
print("   - ui/dialogs/cat_editor_dialog.py")
print("   - ui/dialogs/pedigree_dialog.py")
print("   - rendering/cat_renderer.py")
print("   - resources/genes.json")
print("   - resources/gene_interactions.json")
print("\n2. Run: python main.py")