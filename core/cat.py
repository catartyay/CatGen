import sys
import json
import os
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSize, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import (QIcon, QAction, QFont, QColor, QTextCharFormat, QTextCursor, 
                           QPalette, QLinearGradient, QBrush, QPainter, QPixmap, QPen)

# Modern dark theme stylesheet
DARK_THEME = """
QMainWindow {
    background-color: #1e1e2e;
}
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}
QTreeWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 5px;
    outline: none;
}
QTreeWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px 0px;
}
QTreeWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QTreeWidget::item:hover {
    background-color: #313244;
}
QTextEdit, QPlainTextEdit, QLineEdit {
    background-color: #181825;
    border: 2px solid #313244;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #89b4fa;
    color: #cdd6f4;
}
QTextEdit:focus, QLineEdit:focus {
    border: 2px solid #89b4fa;
}
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    min-width: 80px;
}
QPushButton:hover {
    background-color: #74c7ec;
}
QPushButton:pressed {
    background-color: #89dceb;
}
QPushButton:disabled {
    background-color: #313244;
    color: #6c7086;
}
QPushButton#dangerButton {
    background-color: #f38ba8;
}
QPushButton#dangerButton:hover {
    background-color: #eba0ac;
}
QPushButton#successButton {
    background-color: #a6e3a1;
}
QPushButton#successButton:hover {
    background-color: #b9f0b6;
}
QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 8px;
    background-color: #181825;
    padding: 5px;
}
QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    border: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 20px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QTabBar::tab:hover:!selected {
    background-color: #45475a;
}
QLabel {
    background: transparent;
    color: #cdd6f4;
}
QLabel#headerLabel {
    font-size: 18pt;
    font-weight: bold;
    color: #89b4fa;
}
QLabel#subHeaderLabel {
    font-size: 12pt;
    font-weight: bold;
    color: #74c7ec;
}
QComboBox {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 6px;
    padding: 6px;
    color: #cdd6f4;
}
QComboBox:hover {
    border: 2px solid #89b4fa;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    selection-background-color: #89b4fa;
    color: #cdd6f4;
}
QTableWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    gridline-color: #313244;
}
QTableWidget::item {
    padding: 8px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    padding: 8px;
    border: none;
    font-weight: bold;
}
QScrollBar:vertical {
    background-color: #181825;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 6px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}
QScrollBar:horizontal {
    background-color: #181825;
    height: 12px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 6px;
    min-width: 20px;
}
QMenuBar {
    background-color: #313244;
    color: #cdd6f4;
    border-bottom: 2px solid #45475a;
}
QMenuBar::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QMenu {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 5px;
}
QMenu::item {
    padding: 8px 25px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QToolBar {
    background-color: #313244;
    border-bottom: 2px solid #45475a;
    spacing: 5px;
    padding: 5px;
}
QStatusBar {
    background-color: #313244;
    color: #cdd6f4;
    border-top: 2px solid #45475a;
}
QGroupBox {
    border: 2px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    font-weight: bold;
    color: #89b4fa;
    padding-top: 15px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QListWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 5px;
}
QListWidget::item {
    padding: 10px;
    border-radius: 4px;
    margin: 2px 0px;
}
QListWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QListWidget::item:hover {
    background-color: #313244;
}
QCheckBox {
    spacing: 8px;
    color: #cdd6f4;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #45475a;
    border-radius: 4px;
    background-color: #181825;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QSpinBox {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 6px;
    padding: 6px;
    color: #cdd6f4;
}
QSpinBox:focus {
    border: 2px solid #89b4fa;
}
QProgressBar {
    border: 2px solid #313244;
    border-radius: 6px;
    background-color: #181825;
    text-align: center;
    color: #cdd6f4;
    height: 20px;
}
QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 4px;
}
QSplitter::handle {
    background-color: #313244;
    width: 3px;
}
QSplitter::handle:hover {
    background-color: #89b4fa;
}
"""

class Entity:
    """Enhanced entity with image support, connections, and metadata"""
    def __init__(self, name="", entity_type="", parent=None):
        self.id = str(datetime.now().timestamp())
        self.name = name
        self.entity_type = entity_type
        self.parent = parent
        self.children = []
        self.properties = {}
        self.description = ""
        self.notes = ""
        self.tags = []
        self.relationships = []
        self.timeline_events = []
        self.image_path = ""
        self.color = "#89b4fa"
        self.icon = "📄"
        self.aliases = []
        self.quotes = []
        self.gallery = []
        self.links = []
        self.importance = 3
        self.privacy = "public"
        self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()
        self.word_count = 0
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'entity_type': self.entity_type,
            'description': self.description,
            'notes': self.notes,
            'tags': self.tags,
            'properties': self.properties,
            'relationships': self.relationships,
            'timeline_events': self.timeline_events,
            'image_path': self.image_path,
            'color': self.color,
            'icon': self.icon,
            'aliases': self.aliases,
            'quotes': self.quotes,
            'gallery': self.gallery,
            'links': self.links,
            'importance': self.importance,
            'privacy': self.privacy,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'word_count': self.word_count,
            'children': [child.to_dict() for child in self.children]
        }
    
    @staticmethod
    def from_dict(data, parent=None):
        entity = Entity(data.get('name', ''), data.get('entity_type', ''), parent)
        entity.id = data.get('id', entity.id)
        entity.description = data.get('description', '')
        entity.notes = data.get('notes', '')
        entity.tags = data.get('tags', [])
        entity.properties = data.get('properties', {})
        entity.relationships = data.get('relationships', [])
        entity.timeline_events = data.get('timeline_events', [])
        entity.image_path = data.get('image_path', '')
        entity.color = data.get('color', '#89b4fa')
        entity.icon = data.get('icon', '📄')
        entity.aliases = data.get('aliases', [])
        entity.quotes = data.get('quotes', [])
        entity.gallery = data.get('gallery', [])
        entity.links = data.get('links', [])
        entity.importance = data.get('importance', 3)
        entity.privacy = data.get('privacy', 'public')
        entity.created_date = data.get('created_date', entity.created_date)
        entity.modified_date = data.get('modified_date', entity.modified_date)
        entity.word_count = data.get('word_count', 0)
        
        for child_data in data.get('children', []):
            child = Entity.from_dict(child_data, entity)
            entity.children.append(child)
        
        return entity

class TemplateManager:
    """Enhanced templates with more entity types"""
    ICONS = {
        "Character": "👤",
        "Location": "📍",
        "Organization": "🏛️",
        "Item": "⚔️",
        "Event": "📅",
        "Species": "🧬",
        "Magic System": "✨",
        "Religion": "⛪",
        "Language": "🗣️",
        "Technology": "🔧",
        "Concept": "💡",
        "Faction": "⚔️",
        "Vehicle": "🚗",
        "Creature": "🐉",
        "Artifact": "💎",
        "Timeline": "📜",
        "Custom": "📄"
    }
    
    TEMPLATES = {
        "Character": {
            "properties": {
                "Full Name": "",
                "Age": "",
                "Gender": "",
                "Species/Race": "",
                "Occupation": "",
                "Alignment": "",
                "Height": "",
                "Weight": "",
                "Hair Color": "",
                "Eye Color": "",
                "Birthplace": "",
                "Current Location": "",
                "Status": "Alive",
                "Class/Role": "",
                "Level/Rank": ""
            },
            "sections": ["Appearance", "Personality", "Background", "Abilities", "Equipment", "Relationships", "Goals & Motivations"]
        },
        "Location": {
            "properties": {
                "Type": "",
                "Population": "",
                "Climate": "",
                "Terrain": "",
                "Government": "",
                "Economy": "",
                "Founded": "",
                "Size (sq km)": "",
                "Languages": "",
                "Currency": "",
                "Ruler/Leader": ""
            },
            "sections": ["Geography", "History", "Culture", "Demographics", "Points of Interest", "Resources"]
        },
        "Organization": {
            "properties": {
                "Type": "",
                "Leader": "",
                "Founded": "",
                "Headquarters": "",
                "Size/Members": "",
                "Alignment": "",
                "Symbol": "",
                "Colors": "",
                "Motto": ""
            },
            "sections": ["History", "Structure", "Goals", "Resources", "Allies", "Enemies", "Notable Members"]
        },
        "Item": {
            "properties": {
                "Type": "",
                "Rarity": "Common",
                "Value": "",
                "Weight": "",
                "Material": "",
                "Crafted By": "",
                "Enchanted": "No",
                "Durability": "",
                "Required Level": ""
            },
            "sections": ["Description", "Powers/Effects", "History", "Current Location", "Lore"]
        },
        "Species": {
            "properties": {
                "Lifespan": "",
                "Average Height": "",
                "Average Weight": "",
                "Habitat": "",
                "Diet": "",
                "Intelligence": "",
                "Population": "",
                "Conservation Status": ""
            },
            "sections": ["Physical Characteristics", "Behavior", "Culture", "Abilities", "History", "Relations"]
        },
        "Magic System": {
            "properties": {
                "Source": "",
                "Type": "",
                "Cost": "",
                "Limitations": "",
                "Learning Difficulty": "",
                "Prevalence": ""
            },
            "sections": ["Mechanics", "Schools/Disciplines", "Famous Practitioners", "History", "Cultural Impact"]
        },
        "Event": {
            "properties": {
                "Date/Era": "",
                "Location": "",
                "Duration": "",
                "Type": "",
                "Scale": "",
                "Outcome": ""
            },
            "sections": ["Causes", "Key Figures", "Timeline", "Consequences", "Legacy"]
        },
        "Faction": {
            "properties": {
                "Type": "",
                "Size": "",
                "Territory": "",
                "Leader": "",
                "Founded": "",
                "Military Strength": "",
                "Economic Power": ""
            },
            "sections": ["Ideology", "Structure", "History", "Allies", "Enemies", "Resources"]
        }
    }
    
    @staticmethod
    def get_template(entity_type):
        return TemplateManager.TEMPLATES.get(entity_type, {"properties": {}, "sections": []})
    
    @staticmethod
    def get_icon(entity_type):
        return TemplateManager.ICONS.get(entity_type, "📄")

class RichTextEditor(QTextEdit):
    """Enhanced text editor with formatting toolbar"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(True)
        
    def create_toolbar(self, parent_layout):
        toolbar = QHBoxLayout()
        
        # Bold
        bold_btn = QPushButton("B")
        bold_btn.setMaximumWidth(30)
        bold_btn.setFont(QFont("Arial", 10, QFont.Bold))
        bold_btn.clicked.connect(lambda: self.setFontWeight(QFont.Bold if self.fontWeight() != QFont.Bold else QFont.Normal))
        toolbar.addWidget(bold_btn)
        
        # Italic
        italic_btn = QPushButton("I")
        italic_btn.setMaximumWidth(30)
        italic_btn.setFont(QFont("Arial", 10, QFont.StyleItalic))
        italic_btn.clicked.connect(lambda: self.setFontItalic(not self.fontItalic()))
        toolbar.addWidget(italic_btn)
        
        # Underline
        underline_btn = QPushButton("U")
        underline_btn.setMaximumWidth(30)
        underline_btn.setFont(QFont("Arial", 10))
        underline_btn.clicked.connect(lambda: self.setFontUnderline(not self.fontUnderline()))
        toolbar.addWidget(underline_btn)
        
        toolbar.addSpacing(10)
        
        # Font size
        size_combo = QComboBox()
        size_combo.addItems(["8", "10", "12", "14", "16", "18", "20", "24"])
        size_combo.setCurrentText("10")
        size_combo.currentTextChanged.connect(lambda s: self.setFontPointSize(int(s)))
        size_combo.setMaximumWidth(60)
        toolbar.addWidget(size_combo)
        
        toolbar.addStretch()
        
        parent_layout.addLayout(toolbar)

class EnhancedEntityDialog(QDialog):
    """Beautiful entity creation/editing dialog"""
    def __init__(self, entity_type="Character", entity=None, parent=None):
        super().__init__(parent)
        self.entity = entity
        self.entity_type = entity_type
        self.setWindowTitle(f"{'Edit' if entity else 'Create'} {entity_type}")
        self.setMinimumSize(800, 700)
        self.setup_ui()
        
        if entity:
            self.load_entity_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"{'Edit' if self.entity else 'Create'} {self.entity_type}")
        header.setObjectName("headerLabel")
        layout.addWidget(header)
        
        # Tabs for organized input
        tabs = QTabWidget()
        
        # Basic Info Tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(f"Enter {self.entity_type.lower()} name...")
        form_layout.addRow("Name:", self.name_edit)
        
        self.icon_edit = QLineEdit()
        self.icon_edit.setText(TemplateManager.get_icon(self.entity_type))
        self.icon_edit.setMaximumWidth(60)
        form_layout.addRow("Icon:", self.icon_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(list(TemplateManager.TEMPLATES.keys()) + ["Custom"])
        self.type_combo.setCurrentText(self.entity_type)
        form_layout.addRow("Type:", self.type_combo)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("fantasy, magic, medieval (comma-separated)")
        form_layout.addRow("Tags:", self.tags_edit)
        
        self.aliases_edit = QLineEdit()
        self.aliases_edit.setPlaceholderText("Alternative names (comma-separated)")
        form_layout.addRow("Aliases:", self.aliases_edit)
        
        importance_layout = QHBoxLayout()
        self.importance_spin = QSpinBox()
        self.importance_spin.setMinimum(1)
        self.importance_spin.setMaximum(5)
        self.importance_spin.setValue(3)
        importance_layout.addWidget(self.importance_spin)
        importance_layout.addWidget(QLabel("(1=Minor, 5=Critical)"))
        importance_layout.addStretch()
        form_layout.addRow("Importance:", importance_layout)
        
        basic_layout.addLayout(form_layout)
        
        desc_label = QLabel("Description:")
        desc_label.setObjectName("subHeaderLabel")
        basic_layout.addWidget(desc_label)
        
        self.desc_edit = RichTextEditor()
        self.desc_edit.create_toolbar(basic_layout)
        self.desc_edit.setMinimumHeight(150)
        self.desc_edit.setPlaceholderText("Write a detailed description...")
        basic_layout.addWidget(self.desc_edit)
        
        basic_tab.setLayout(basic_layout)
        tabs.addTab(basic_tab, "📝 Basic Info")
        
        # Properties Tab
        props_tab = QWidget()
        props_layout = QVBoxLayout()
        
        props_label = QLabel("Custom Properties")
        props_label.setObjectName("subHeaderLabel")
        props_layout.addWidget(props_label)
        
        self.properties_table = QTableWidget(0, 2)
        self.properties_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.properties_table.horizontalHeader().setStretchLastSection(True)
        self.properties_table.setMinimumHeight(200)
        props_layout.addWidget(self.properties_table)
        
        # Load template properties
        template = TemplateManager.get_template(self.entity_type)
        for key, value in template.get("properties", {}).items():
            self.add_property_row(key, value)
        
        btn_layout = QHBoxLayout()
        add_prop_btn = QPushButton("➕ Add Property")
        add_prop_btn.clicked.connect(lambda: self.add_property_row())
        btn_layout.addWidget(add_prop_btn)
        
        remove_prop_btn = QPushButton("➖ Remove Selected")
        remove_prop_btn.setObjectName("dangerButton")
        remove_prop_btn.clicked.connect(self.remove_property_row)
        btn_layout.addWidget(remove_prop_btn)
        btn_layout.addStretch()
        props_layout.addLayout(btn_layout)
        
        props_tab.setLayout(props_layout)
        tabs.addTab(props_tab, "⚙️ Properties")
        
        # Relationships Tab
        rel_tab = QWidget()
        rel_layout = QVBoxLayout()
        
        rel_label = QLabel("Relationships")
        rel_label.setObjectName("subHeaderLabel")
        rel_layout.addWidget(rel_label)
        
        self.relationships_table = QTableWidget(0, 3)
        self.relationships_table.setHorizontalHeaderLabels(["Entity", "Type", "Description"])
        self.relationships_table.horizontalHeader().setStretchLastSection(True)
        rel_layout.addWidget(self.relationships_table)
        
        rel_btn_layout = QHBoxLayout()
        add_rel_btn = QPushButton("➕ Add Relationship")
        add_rel_btn.clicked.connect(self.add_relationship_row)
        rel_btn_layout.addWidget(add_rel_btn)
        
        remove_rel_btn = QPushButton("➖ Remove Selected")
        remove_rel_btn.setObjectName("dangerButton")
        remove_rel_btn.clicked.connect(self.remove_relationship_row)
        rel_btn_layout.addWidget(remove_rel_btn)
        rel_btn_layout.addStretch()
        rel_layout.addLayout(rel_btn_layout)
        
        rel_tab.setLayout(rel_layout)
        tabs.addTab(rel_tab, "🔗 Relationships")
        
        # Notes Tab
        notes_tab = QWidget()
        notes_layout = QVBoxLayout()
        
        notes_label = QLabel("Extended Notes")
        notes_label.setObjectName("subHeaderLabel")
        notes_layout.addWidget(notes_label)
        
        self.notes_edit = RichTextEditor()
        self.notes_edit.create_toolbar(notes_layout)
        self.notes_edit.setPlaceholderText("Write detailed notes, backstory, or additional information...")
        notes_layout.addWidget(self.notes_edit)
        
        notes_tab.setLayout(notes_layout)
        tabs.addTab(notes_tab, "📖 Notes")
        
        layout.addWidget(tabs)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("✓ Save")
        buttons.button(QDialogButtonBox.Cancel).setText("✗ Cancel")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def add_property_row(self, key="", value=""):
        row = self.properties_table.rowCount()
        self.properties_table.insertRow(row)
        self.properties_table.setItem(row, 0, QTableWidgetItem(key))
        self.properties_table.setItem(row, 1, QTableWidgetItem(value))
    
    def remove_property_row(self):
        current_row = self.properties_table.currentRow()
        if current_row >= 0:
            self.properties_table.removeRow(current_row)
    
    def add_relationship_row(self):
        row = self.relationships_table.rowCount()
        self.relationships_table.insertRow(row)
        self.relationships_table.setItem(row, 0, QTableWidgetItem())
        self.relationships_table.setItem(row, 1, QTableWidgetItem())
        self.relationships_table.setItem(row, 2, QTableWidgetItem())
    
    def remove_relationship_row(self):
        current_row = self.relationships_table.currentRow()
        if current_row >= 0:
            self.relationships_table.removeRow(current_row)
    
    def load_entity_data(self):
        if not self.entity:
            return
        
        self.name_edit.setText(self.entity.name)
        self.icon_edit.setText(self.entity.icon)
        self.type_combo.setCurrentText(self.entity.entity_type)
        self.tags_edit.setText(", ".join(self.entity.tags))
        self.aliases_edit.setText(", ".join(self.entity.aliases))
        self.importance_spin.setValue(self.entity.importance)
        self.desc_edit.setHtml(self.entity.description)
        self.notes_edit.setHtml(self.entity.notes)
        
        self.properties_table.setRowCount(0)
        for key, value in self.entity.properties.items():
            self.add_property_row(key, str(value))
        
        self.relationships_table.setRowCount(0)
        for rel in self.entity.relationships:
            row = self.relationships_table.rowCount()
            self.relationships_table.insertRow(row)
            self.relationships_table.setItem(row, 0, QTableWidgetItem(rel.get('entity', '')))
            self.relationships_table.setItem(row, 1, QTableWidgetItem(rel.get('type', '')))
            self.relationships_table.setItem(row, 2, QTableWidgetItem(rel.get('description', '')))
    
    def get_entity_data(self):
        properties = {}
        for row in range(self.properties_table.rowCount()):
            key_item = self.properties_table.item(row, 0)
            value_item = self.properties_table.item(row, 1)
            if key_item and value_item and key_item.text():
                properties[key_item.text()] = value_item.text()
        
        relationships = []
        for row in range(self.relationships_table.rowCount()):
            entity_item = self.relationships_table.item(row, 0)
            type_item = self.relationships_table.item(row, 1)
            desc_item = self.relationships_table.item(row, 2)
            
            if entity_item and entity_item.text():
                relationships.append({
                    'entity': entity_item.text(),
                    'type': type_item.text() if type_item else '',
                    'description': desc_item.text() if desc_item else ''
                })
        
        tags = [tag.strip() for tag in self.tags_edit.text().split(',') if tag.strip()]
        aliases = [alias.strip() for alias in self.aliases_edit.text().split(',') if alias.strip()]
        
        return {
            'name': self.name_edit.text(),
            'icon': self.icon_edit.text(),
            'entity_type': self.type_combo.currentText(),
            'description': self.desc_edit.toHtml(),
            'notes': self.notes_edit.toHtml(),
            'tags': tags,
            'aliases': aliases,
            'properties': properties,
            'relationships': relationships,
            'importance': self.importance_spin.value()
        }

class AdvancedSearchDialog(QDialog):
    """Powerful search with filters"""
    def __init__(self, root_entity, parent=None):
        super().__init__(parent)
        self.root_entity = root_entity
        self.results = []
        self.setWindowTitle("🔍 Advanced Search")
        self.setMinimumSize(700, 500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Search header
        header = QLabel("Advanced Entity Search")
        header.setObjectName("headerLabel")
        layout.addWidget(header)
        
        # Search input
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name, description, tags, properties...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.setObjectName("successButton")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Filters
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All"] + list(TemplateManager.TEMPLATES.keys()) + ["Custom"])
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("Importance:"))
        self.importance_filter = QComboBox()
        self.importance_filter.addItems(["All", "1", "2", "3", "4", "5"])
        filter_layout.addWidget(self.importance_filter)
        
        filter_layout.addWidget(QLabel("Has Tags:"))
        self.tag_checkbox = QCheckBox()
        filter_layout.addWidget(self.tag_checkbox)
        
        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Results
        results_label = QLabel("Search Results")
        results_label.setObjectName("subHeaderLabel")
        layout.addWidget(results_label)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.results_list)
        
        self.result_count_label = QLabel("Enter search terms to begin")
        layout.addWidget(self.result_count_label)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def perform_search(self):
        query = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        importance_filter = self.importance_filter.currentText()
        has_tags = self.tag_checkbox.isChecked()
        
        self.results = []
        self.search_recursive(self.root_entity, query, type_filter, importance_filter, has_tags)
        
        self.results_list.clear()
        for entity in self.results:
            item_text = f"{entity.icon} {entity.name} ({entity.entity_type})"
            if entity.tags:
                item_text += f" | Tags: {', '.join(entity.tags[:3])}"
            if entity.importance > 3:
                item_text += f" | ⭐ Priority"
            
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.UserRole, entity)
            self.results_list.addItem(list_item)
        
        self.result_count_label.setText(f"✓ Found {len(self.results)} result(s)")
    
    def search_recursive(self, entity, query, type_filter, importance_filter, has_tags):
        if entity.entity_type != "Root":
            matches = False
            
            if not query:
                matches = True
            elif query in entity.name.lower():
                matches = True
            elif query in entity.description.lower():
                matches = True
            elif any(query in tag.lower() for tag in entity.tags):
                matches = True
            elif any(query in str(v).lower() for v in entity.properties.values()):
                matches = True
            
            if matches:
                if type_filter != "All" and entity.entity_type != type_filter:
                    matches = False
                if importance_filter != "All" and entity.importance != int(importance_filter):
                    matches = False
                if has_tags and not entity.tags:
                    matches = False
                
                if matches:
                    self.results.append(entity)
        
        for child in entity.children:
            self.search_recursive(child, query, type_filter, importance_filter, has_tags)
    
    def get_selected_entity(self):
        current_item = self.results_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None

class StatisticsDialog(QDialog):
    """Comprehensive world statistics"""
    def __init__(self, root_entity, parent=None):
        super().__init__(parent)
        self.root_entity = root_entity
        self.setWindowTitle("📊 World Statistics")
        self.setMinimumSize(600, 500)
        self.setup_ui()
        self.calculate_statistics()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("World Statistics Dashboard")
        header.setObjectName("headerLabel")
        layout.addWidget(header)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def calculate_statistics(self):
        stats = {
            "Total Entities": 0,
            "Characters": 0,
            "Locations": 0,
            "Organizations": 0,
            "Items": 0,
            "Events": 0,
            "Species": 0,
            "Factions": 0,
            "Other": 0
        }
        
        total_words = 0
        total_relationships = 0
        total_tags = set()
        importance_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        self.count_entities(self.root_entity, stats, importance_counts)
        total_words, total_relationships, total_tags = self.calculate_extended_stats(self.root_entity)
        
        stats_html = """
        <style>
            body { font-family: 'Segoe UI'; color: #cdd6f4; }
            h2 { color: #89b4fa; border-bottom: 2px solid #89b4fa; padding-bottom: 10px; }
            h3 { color: #74c7ec; margin-top: 20px; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            td { padding: 8px; border-bottom: 1px solid #313244; }
            .number { color: #a6e3a1; font-weight: bold; font-size: 16px; }
            .label { color: #cdd6f4; }
            .highlight { background-color: #313244; border-radius: 4px; padding: 15px; margin: 10px 0; }
        </style>
        
        <h2>📊 Entity Overview</h2>
        <table>
        """
        
        for key, value in stats.items():
            if key != "Other":
                icon = "📄"
                if key == "Characters": icon = "👤"
                elif key == "Locations": icon = "📍"
                elif key == "Organizations": icon = "🏛️"
                elif key == "Items": icon = "⚔️"
                elif key == "Events": icon = "📅"
                elif key == "Species": icon = "🧬"
                elif key == "Factions": icon = "⚔️"
                
                stats_html += f'<tr><td class="label">{icon} {key}</td><td class="number" align="right">{value}</td></tr>'
        
        stats_html += "</table>"
        
        stats_html += '<div class="highlight">'
        stats_html += f'<h3>✨ Content Statistics</h3>'
        stats_html += f'<p>📝 Total Words Written: <span class="number">{total_words:,}</span></p>'
        stats_html += f'<p>🔗 Total Relationships: <span class="number">{total_relationships}</span></p>'
        stats_html += f'<p>🏷️ Unique Tags: <span class="number">{len(total_tags)}</span></p>'
        stats_html += '</div>'
        
        stats_html += '<h3>⭐ Importance Distribution</h3><table>'
        for importance, count in sorted(importance_counts.items(), reverse=True):
            stars = "⭐" * importance
            stats_html += f'<tr><td class="label">{stars} Level {importance}</td><td class="number" align="right">{count}</td></tr>'
        stats_html += '</table>'
        
        if total_tags:
            stats_html += '<h3>🏷️ Most Used Tags</h3>'
            stats_html += '<p>' + ' • '.join(list(total_tags)[:10]) + '</p>'
        
        self.stats_text.setHtml(stats_html)
    
    def count_entities(self, entity, stats, importance_counts):
        if entity.entity_type != "Root":
            stats["Total Entities"] += 1
            
            if entity.entity_type + "s" in stats:
                stats[entity.entity_type + "s"] += 1
            else:
                stats["Other"] += 1
            
            importance_counts[entity.importance] = importance_counts.get(entity.importance, 0) + 1
        
        for child in entity.children:
            self.count_entities(child, stats, importance_counts)
    
    def calculate_extended_stats(self, entity, total_words=0, total_rels=0, tags=None):
        if tags is None:
            tags = set()
        
        if entity.entity_type != "Root":
            total_words += len(entity.description.split()) + len(entity.notes.split())
            total_rels += len(entity.relationships)
            tags.update(entity.tags)
        
        for child in entity.children:
            total_words, total_rels, tags = self.calculate_extended_stats(child, total_words, total_rels, tags)
        
        return total_words, total_rels, tags

class TimelineWidget(QWidget):
    """Enhanced timeline with visual representation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("📜 Timeline Events")
        header.setObjectName("subHeaderLabel")
        layout.addWidget(header)
        
        toolbar = QHBoxLayout()
        add_event_btn = QPushButton("➕ Add Event")
        add_event_btn.clicked.connect(self.add_event)
        toolbar.addWidget(add_event_btn)
        
        remove_event_btn = QPushButton("➖ Remove Selected")
        remove_event_btn.setObjectName("dangerButton")
        remove_event_btn.clicked.connect(self.remove_event)
        toolbar.addWidget(remove_event_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self.timeline_list = QListWidget()
        layout.addWidget(self.timeline_list)
        
        self.setLayout(layout)
    
    def add_event(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Timeline Event")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Battle of the Five Armies")
        form.addRow("Event Name:", name_edit)
        
        date_edit = QLineEdit()
        date_edit.setPlaceholderText("Year 1523, Third Age")
        form.addRow("Date/Era:", date_edit)
        
        location_edit = QLineEdit()
        location_edit.setPlaceholderText("Location where event occurred")
        form.addRow("Location:", location_edit)
        
        importance_spin = QSpinBox()
        importance_spin.setMinimum(1)
        importance_spin.setMaximum(5)
        importance_spin.setValue(3)
        form.addRow("Importance:", importance_spin)
        
        layout.addLayout(form)
        
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)
        
        desc_edit = QTextEdit()
        desc_edit.setMaximumHeight(150)
        desc_edit.setPlaceholderText("Describe what happened...")
        layout.addWidget(desc_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.Accepted:
            stars = "⭐" * importance_spin.value()
            event_text = f"📅 {date_edit.text()} | {name_edit.text()} {stars}"
            self.timeline_list.addItem(event_text)
            self.events.append({
                'name': name_edit.text(),
                'date': date_edit.text(),
                'location': location_edit.text(),
                'importance': importance_spin.value(),
                'description': desc_edit.toPlainText()
            })
    
    def remove_event(self):
        current_row = self.timeline_list.currentRow()
        if current_row >= 0:
            self.timeline_list.takeItem(current_row)
            self.events.pop(current_row)
    
    def load_events(self, events):
        self.events = events
        self.timeline_list.clear()
        for event in events:
            stars = "⭐" * event.get('importance', 3)
            event_text = f"📅 {event.get('date', '')} | {event.get('name', '')} {stars}"
            self.timeline_list.addItem(event_text)
    
    def get_events(self):
        return self.events

class WorldForge(QMainWindow):
    """Main application - Professional worldbuilding suite"""
    def __init__(self):
        super().__init__()
        self.current_entity = None
        self.world_file = None
        self.root_entity = Entity("World Root", "Root")
        self.modified = False
        
        self.setWindowTitle("WorldForge Pro - Advanced Worldbuilding Suite")
        self.setGeometry(50, 50, 1600, 1000)
        
        self.setup_ui()
        self.create_menu_bar()
        self.create_toolbar()
        self.statusBar().showMessage("🎨 Ready to build your world!")
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(300000)  # 5 minutes
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # LEFT PANEL - Entity Tree
        left_panel = QWidget()
        left_panel.setMinimumWidth(300)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tree header
        tree_header_layout = QHBoxLayout()
        tree_label = QLabel("🌍 World Structure")
        tree_label.setObjectName("headerLabel")
        tree_header_layout.addWidget(tree_label)
        tree_header_layout.addStretch()
        
        expand_btn = QPushButton("📂")
        expand_btn.setMaximumWidth(35)
        expand_btn.setToolTip("Expand All")
        expand_btn.clicked.connect(self.entity_tree.expandAll)
        tree_header_layout.addWidget(expand_btn)
        
        collapse_btn = QPushButton("📁")
        collapse_btn.setMaximumWidth(35)
        collapse_btn.setToolTip("Collapse All")
        collapse_btn.clicked.connect(self.entity_tree.collapseAll)
        tree_header_layout.addWidget(collapse_btn)
        
        left_layout.addLayout(tree_header_layout)
        
        # Search box
        self.quick_search = QLineEdit()
        self.quick_search.setPlaceholderText("🔍 Quick filter...")
        self.quick_search.textChanged.connect(self.filter_tree)
        left_layout.addWidget(self.quick_search)
        
        # Entity tree
        self.entity_tree = QTreeWidget()
        self.entity_tree.setHeaderLabel("Entities")
        self.entity_tree.itemClicked.connect(self.on_entity_selected)
        self.entity_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.entity_tree.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.entity_tree)
        
        # Tree buttons
        tree_buttons = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add")
        add_btn.setObjectName("successButton")
        add_btn.clicked.connect(self.add_entity)
        tree_buttons.addWidget(add_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self.delete_entity)
        tree_buttons.addWidget(delete_btn)
        
        left_layout.addLayout(tree_buttons)
        
        # Entity count
        self.entity_count_label = QLabel("0 entities")
        self.entity_count_label.setStyleSheet("color: #6c7086; font-style: italic;")
        left_layout.addWidget(self.entity_count_label)
        
        left_panel.setLayout(left_layout)
        splitter.addWidget(left_panel)
        
        # RIGHT PANEL - Entity Details
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Entity header
        header_layout = QHBoxLayout()
        
        self.entity_icon_label = QLabel("📄")
        self.entity_icon_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(self.entity_icon_label)
        
        name_layout = QVBoxLayout()
        name_layout.setSpacing(0)
        
        self.entity_name_label = QLabel("Select an entity")
        self.entity_name_label.setObjectName("headerLabel")
        name_layout.addWidget(self.entity_name_label)
        
        self.entity_type_label = QLabel("No entity selected")
        self.entity_type_label.setStyleSheet("color: #6c7086; font-style: italic;")
        name_layout.addWidget(self.entity_type_label)
        
        header_layout.addLayout(name_layout)
        header_layout.addStretch()
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.clicked.connect(self.edit_current_entity)
        header_layout.addWidget(edit_btn)
        
        duplicate_btn = QPushButton("📋 Duplicate")
        duplicate_btn.clicked.connect(self.duplicate_entity)
        header_layout.addWidget(duplicate_btn)
        
        right_layout.addLayout(header_layout)
        
        # Tags and importance
        meta_layout = QHBoxLayout()
        self.entity_tags_label = QLabel("")
        meta_layout.addWidget(self.entity_tags_label)
        meta_layout.addStretch()
        self.entity_importance_label = QLabel("")
        meta_layout.addWidget(self.entity_importance_label)
        right_layout.addLayout(meta_layout)
        
        # Details tabs
        self.details_tabs = QTabWidget()
        
        # OVERVIEW TAB
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        
        desc_label = QLabel("Description")
        desc_label.setObjectName("subHeaderLabel")
        overview_layout.addWidget(desc_label)
        
        self.description_view = QTextEdit()
        self.description_view.setReadOnly(True)
        overview_layout.addWidget(self.description_view)
        
        aliases_label = QLabel("Aliases / Alternative Names")
        aliases_label.setObjectName("subHeaderLabel")
        overview_layout.addWidget(aliases_label)
        
        self.aliases_label = QLabel("None")
        overview_layout.addWidget(self.aliases_label)
        
        overview_tab.setLayout(overview_layout)
        self.details_tabs.addTab(overview_tab, "📝 Overview")
        
        # PROPERTIES TAB
        properties_tab = QWidget()
        props_layout = QVBoxLayout()
        
        props_header = QLabel("Entity Properties")
        props_header.setObjectName("subHeaderLabel")
        props_layout.addWidget(props_header)
        
        self.properties_table = QTableWidget(0, 2)
        self.properties_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.properties_table.horizontalHeader().setStretchLastSection(True)
        self.properties_table.verticalHeader().setVisible(False)
        props_layout.addWidget(self.properties_table)
        
        properties_tab.setLayout(props_layout)
        self.details_tabs.addTab(properties_tab, "⚙️ Properties")
        
        # RELATIONSHIPS TAB
        rel_tab = QWidget()
        rel_layout = QVBoxLayout()
        
        rel_header = QLabel("Connections & Relationships")
        rel_header.setObjectName("subHeaderLabel")
        rel_layout.addWidget(rel_header)
        
        self.relationships_table = QTableWidget(0, 3)
        self.relationships_table.setHorizontalHeaderLabels(["Entity", "Type", "Description"])
        self.relationships_table.horizontalHeader().setStretchLastSection(True)
        self.relationships_table.verticalHeader().setVisible(False)
        rel_layout.addWidget(self.relationships_table)
        
        rel_tab.setLayout(rel_layout)
        self.details_tabs.addTab(rel_tab, "🔗 Relationships")
        
        # TIMELINE TAB
        self.timeline_widget = TimelineWidget()
        self.details_tabs.addTab(self.timeline_widget, "📜 Timeline")
        
        # NOTES TAB
        notes_tab = QWidget()
        notes_layout = QVBoxLayout()
        
        notes_header = QLabel("Extended Notes & Lore")
        notes_header.setObjectName("subHeaderLabel")
        notes_layout.addWidget(notes_header)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Add detailed notes, backstory, or world lore here...")
        self.notes_edit.textChanged.connect(self.save_notes)
        notes_layout.addWidget(self.notes_edit)
        
        self.word_count_label = QLabel("Words: 0")
        self.word_count_label.setStyleSheet("color: #6c7086; font-style: italic;")
        notes_layout.addWidget(self.word_count_label)
        
        notes_tab.setLayout(notes_layout)
        self.details_tabs.addTab(notes_tab, "📖 Notes")
        
        right_layout.addWidget(self.details_tabs)
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)
        
        splitter.setSizes([350, 1250])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Apply dark theme
        self.setStyleSheet(DARK_THEME)
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # FILE MENU
        file_menu = menubar.addMenu("📁 File")
        
        new_action = QAction("🆕 New World", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_world)
        file_menu.addAction(new_action)
        
        open_action = QAction("📂 Open World", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_world)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("💾 Save World", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_world)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("💾 Save World As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_world_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_menu = file_menu.addMenu("📤 Export")
        
        export_json = QAction("Export as JSON", self)
        export_json.triggered.connect(self.export_json)
        export_menu.addAction(export_json)
        
        export_html = QAction("Export as HTML", self)
        export_html.triggered.connect(self.export_html)
        export_menu.addAction(export_html)
        
        export_md = QAction("Export as Markdown", self)
        export_md.triggered.connect(self.export_markdown)
        export_menu.addAction(export_md)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # EDIT MENU
        edit_menu = menubar.addMenu("✏️ Edit")
        
        add_entity_action = QAction("➕ Add Entity", self)
        add_entity_action.setShortcut("Ctrl+E")
        add_entity_action.triggered.connect(self.add_entity)
        edit_menu.addAction(add_entity_action)
        
        delete_entity_action = QAction("🗑️ Delete Entity", self)
        delete_entity_action.setShortcut("Delete")
        delete_entity_action.triggered.connect(self.delete_entity)
        edit_menu.addAction(delete_entity_action)
        
        duplicate_action = QAction("📋 Duplicate Entity", self)
        duplicate_action.setShortcut("Ctrl+D")
        duplicate_action.triggered.connect(self.duplicate_entity)
        edit_menu.addAction(duplicate_action)
        
        edit_menu.addSeparator()
        
        search_action = QAction("🔍 Advanced Search", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self.show_search)
        edit_menu.addAction(search_action)
        
        # VIEW MENU
        view_menu = menubar.addMenu("👁️ View")
        
        expand_all_action = QAction("📂 Expand All", self)
        expand_all_action.triggered.connect(self.entity_tree.expandAll)
        view_menu.addAction(expand_all_action)
        
        collapse_all_action = QAction("📁 Collapse All", self)
        collapse_all_action.triggered.connect(self.entity_tree.collapseAll)
        view_menu.addAction(collapse_all_action)
        
        view_menu.addSeparator()
        
        stats_action = QAction("📊 World Statistics", self)
        stats_action.setShortcut("Ctrl+I")
        stats_action.triggered.connect(self.show_statistics)
        view_menu.addAction(stats_action)
        
        # TOOLS MENU
        tools_menu = menubar.addMenu("🛠️ Tools")
        
        template_action = QAction("📋 Create from Template", self)
        template_action.setShortcut("Ctrl+T")
        template_action.triggered.connect(self.create_from_template)
        tools_menu.addAction(template_action)
        
        batch_action = QAction("⚡ Batch Operations", self)
        batch_action.triggered.connect(self.show_batch_operations)
        tools_menu.addAction(batch_action)
        
        # HELP MENU
        help_menu = menubar.addMenu("❓ Help")
        
        shortcuts_action = QAction("⌨️ Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        about_action = QAction("ℹ️ About WorldForge Pro", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
"""
Cat model class representing a single cat with genetics and phenotype
"""

import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class Cat:
    """Represents a cat with complete genetic information"""
    
    def __init__(
        self,
        cat_id: Optional[int] = None,
        name: str = "",
        sex: str = "random",
        genes: Optional[Dict[str, List[str]]] = None,
        birth_date: Optional[str] = None,
        sire_id: Optional[int] = None,
        dam_id: Optional[int] = None,
        build_value: Optional[int] = None,
        size_value: Optional[int] = None,
        white_percentage: Optional[int] = None
    ):
        self.id = cat_id
        self.name = name
        self.sex = random.choice(['male', 'female']) if sex == 'random' else sex
        self.genes = genes or {}
        self.birth_date = birth_date or datetime.now().strftime('%Y-%m-%d')
        self.sire_id = sire_id
        self.dam_id = dam_id
        
        # Physical attributes (0-100 scale)
        self.build_value = build_value if build_value is not None else self._generate_random_build()
        self.size_value = size_value if size_value is not None else self._generate_random_size()
        
        # Apply sexual dimorphism for males
        if self.sex == 'male' and size_value is None:
            self.size_value = min(100, self.size_value + random.randint(3, 8))
        
        # Cached values
        self._white_percentage = white_percentage
        self._phenotype_cache = None
        self._eye_color_cache = None
    
    def _generate_random_build(self) -> int:
        """Generate random build value weighted toward average (46-55)"""
        return int(random.triangular(0, 100, 50))
    
    def _generate_random_size(self) -> int:
        """Generate random size value weighted toward medium (41-60)"""
        return int(random.triangular(0, 100, 50))
    
    def get_build_phenotype(self) -> str:
        """Map hidden build value (0-100) to phenotype category"""
        if self.build_value <= 15:
            return "Extreme Cobby"
        elif self.build_value <= 30:
            return "Cobby"
        elif self.build_value <= 45:
            return "Semi-Cobby"
        elif self.build_value <= 55:
            return "Average"
        elif self.build_value <= 70:
            return "Semi-Foreign"
        elif self.build_value <= 85:
            return "Foreign"
        else:
            return "Extreme Foreign"
    
    def get_size_phenotype(self) -> str:
        """Map hidden size value (0-100) to phenotype category"""
        if self.size_value <= 20:
            return "Toy"
        elif self.size_value <= 40:
            return "Small"
        elif self.size_value <= 60:
            return "Medium"
        elif self.size_value <= 80:
            return "Large"
        else:
            return "Giant"
    
    def invalidate_cache(self):
        """Invalidate cached phenotype calculations"""
        self._phenotype_cache = None
        self._eye_color_cache = None
        self._white_percentage = None
    
    def to_dict(self) -> Dict:
        """Convert cat to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'sex': self.sex,
            'genes': self.genes,
            'birth_date': self.birth_date,
            'sire_id': self.sire_id,
            'dam_id': self.dam_id,
            'build_value': self.build_value,
            'size_value': self.size_value,
            'white_percentage': self._white_percentage
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Cat':
        """Create cat from dictionary"""
        return cls(
            cat_id=data['id'],
            name=data.get('name', ''),
            sex=data['sex'],
            genes=data['genes'],
            birth_date=data.get('birth_date'),
            sire_id=data.get('sire_id'),
            dam_id=data.get('dam_id'),
            build_value=data.get('build_value'),
            size_value=data.get('size_value'),
            white_percentage=data.get('white_percentage')
        )
    
    def __repr__(self) -> str:
        return f"Cat(id={self.id}, name='{self.name}', sex='{self.sex}')"