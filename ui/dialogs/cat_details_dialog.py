"""
Stunning Cat Details Dialog - Premium professional design
Replace: ui/dialogs/cat_details_dialog.py
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                               QPushButton, QLabel, QWidget, QTabWidget,
                               QGridLayout, QGroupBox, QScrollArea, QFrame, QSplitter)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont, QColor


class StatCard(QFrame):
    """Beautiful stat card with icon"""
    
    def __init__(self, title, value, icon, color):
        super().__init__()
        self.setFixedSize(160, 90)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 {self.lighten(color)});
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        self.setLayout(layout)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28pt; background: transparent;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 8pt;
            color: rgba(255,255,255,0.8);
            background: transparent;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 1px;
        """)
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            font-size: 14pt;
            color: white;
            background: transparent;
            font-weight: bold;
        """)
        layout.addWidget(value_label)
        
        layout.addStretch()
    
    def lighten(self, color):
        """Lighten a color"""
        qcolor = QColor(color)
        h, s, l, a = qcolor.getHsl()
        qcolor.setHsl(h, max(0, s - 30), min(255, l + 30), a)
        return qcolor.name()


class GeneItem(QFrame):
    """Beautiful gene display item"""
    
    def __init__(self, name, alleles, description, color="#3742fa"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e1e8ed;
                border-radius: 6px;
                padding: 12px;
            }
            QFrame:hover {
                border: 1px solid #3742fa;
                background: #f8f9ff;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Header with name and alleles
        header = QHBoxLayout()
        
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            font-weight: 700;
            font-size: 11pt;
            color: #2c3e50;
        """)
        header.addWidget(name_label)
        
        header.addStretch()
        
        allele_label = QLabel(alleles)
        allele_label.setStyleSheet(f"""
            font-family: 'Courier New';
            font-weight: bold;
            font-size: 11pt;
            color: {color};
            background: {color}15;
            padding: 4px 10px;
            border-radius: 4px;
        """)
        header.addWidget(allele_label)
        
        layout.addLayout(header)
        
        # Description
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                font-size: 9pt;
                color: #7f8c8d;
                padding-top: 2px;
            """)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)


class CatDetailsDialog(QDialog):
    """Stunning cat profile with premium design"""
    
    def __init__(self, cat, main_window, parent=None):
        super().__init__(parent)
        self.cat = cat
        self.main_window = main_window
        self.setWindowTitle(f"Cat Profile - {cat.name or f'#{cat.id}'}")
        self.setModal(True)
        self.resize(1100, 750)
        
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f7fa, stop:1 #c3cfe2);
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create stunning interface"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Hero section
        hero = self.create_hero()
        layout.addWidget(hero)
        
        # Main content with sidebar
        content = self.create_content()
        layout.addWidget(content, 1)
        
        # Footer
        footer = self.create_footer()
        layout.addWidget(footer)
    
    def create_hero(self):
        """Create hero section"""
        hero = QFrame()
        hero.setFixedHeight(200)
        
        # Dynamic gradient based on sex
        if self.cat.sex == "male":
            gradient = "stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb"
        else:
            gradient = "stop:0 #f093fb, stop:0.5 #f5576c, stop:1 #ff6b6b"
        
        hero.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, {gradient});
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        hero.setLayout(layout)
        
        # Left side - Cat info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        # Cat emoji/icon with animation feel
        icon = QLabel("🐱")
        icon.setStyleSheet("""
            font-size: 52pt;
            background: transparent;
        """)
        info_layout.addWidget(icon)
        
        # Name
        name_text = self.cat.name or f"Cat #{self.cat.id}"
        name_label = QLabel(name_text)
        name_label.setStyleSheet("""
            font-size: 28pt;
            font-weight: 800;
            color: white;
            background: transparent;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        """)
        info_layout.addWidget(name_label)
        
        # ID badge
        id_badge = QLabel(f"ID: #{self.cat.id}")
        id_badge.setStyleSheet("""
            font-size: 10pt;
            color: white;
            background: rgba(0,0,0,0.2);
            padding: 6px 12px;
            border-radius: 15px;
            font-weight: 600;
        """)
        id_badge.setMaximumWidth(100)
        info_layout.addWidget(id_badge)
        
        # Birth & generation
        meta = QLabel(f"📅 {self.cat.birth_date}  •  Gen {self.calculate_generation()}")
        meta.setStyleSheet("""
            font-size: 10pt;
            color: rgba(255,255,255,0.9);
            background: transparent;
            padding-top: 5px;
        """)
        info_layout.addWidget(meta)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Right side - Quick stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        phenotype_calc = self.main_window.phenotype_calculator
        white_pct = phenotype_calc.get_white_percentage(self.cat)
        
        stats_layout.addWidget(StatCard(
            "Sex",
            self.cat.sex.upper(),
            "♂" if self.cat.sex == "male" else "♀",
            "#667eea" if self.cat.sex == "male" else "#f5576c"
        ))
        
        stats_layout.addWidget(StatCard(
            "Build",
            self.cat.get_build_phenotype(),
            "🏋️",
            "#a29bfe"
        ))
        
        stats_layout.addWidget(StatCard(
            "Size",
            self.cat.get_size_phenotype(),
            "📏",
            "#fd79a8"
        ))
        
        stats_layout.addWidget(StatCard(
            "White",
            f"{white_pct}%",
            "⚪",
            "#74b9ff"
        ))
        
        layout.addLayout(stats_layout)
        
        return hero
    
    def create_content(self):
        """Create main content area"""
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        content.setLayout(layout)
        
        # Left sidebar - Phenotype card
        sidebar = self.create_sidebar()
        layout.addWidget(sidebar)
        
        # Main area - Tabs
        tabs = self.create_tabs()
        layout.addWidget(tabs, 1)
        
        return content
    
    def create_sidebar(self):
        """Create sidebar with phenotype"""
        sidebar = QFrame()
        sidebar.setFixedWidth(320)
        sidebar.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e1e8ed;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        sidebar.setLayout(layout)
        
        phenotype_calc = self.main_window.phenotype_calculator
        phenotype = phenotype_calc.calculate_phenotype(self.cat)
        eye_color = phenotype_calc.calculate_eye_color(self.cat)
        
        # Section title
        title = QLabel("APPEARANCE")
        title.setStyleSheet("""
            font-size: 9pt;
            font-weight: 700;
            color: #95a5a6;
            letter-spacing: 2px;
        """)
        layout.addWidget(title)
        
        # Phenotype
        pheno_label = QLabel("Phenotype")
        pheno_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 10pt;")
        layout.addWidget(pheno_label)
        
        pheno_value = QLabel(phenotype)
        pheno_value.setStyleSheet("""
            font-size: 13pt;
            font-weight: 600;
            color: #3742fa;
            padding: 10px;
            background: #f8f9ff;
            border-radius: 6px;
            border-left: 4px solid #3742fa;
        """)
        pheno_value.setWordWrap(True)
        layout.addWidget(pheno_value)
        
        # Eye color
        eye_label = QLabel("Eye Color")
        eye_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 10pt; padding-top: 10px;")
        layout.addWidget(eye_label)
        
        eye_value = QLabel(f"👁 {eye_color}")
        eye_value.setStyleSheet("""
            font-size: 11pt;
            color: #2c3e50;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
        """)
        eye_value.setWordWrap(True)
        layout.addWidget(eye_value)
        
        # Physical traits
        traits_title = QLabel("PHYSICAL TRAITS")
        traits_title.setStyleSheet("""
            font-size: 9pt;
            font-weight: 700;
            color: #95a5a6;
            letter-spacing: 2px;
            padding-top: 15px;
        """)
        layout.addWidget(traits_title)
        
        # Trait meters
        layout.addWidget(self.create_mini_meter("Build", self.cat.build_value, "#9b59b6"))
        layout.addWidget(self.create_mini_meter("Size", self.cat.size_value, "#3498db"))
        
        white_pct = phenotype_calc.get_white_percentage(self.cat)
        layout.addWidget(self.create_mini_meter("White", white_pct, "#95a5a6"))
        
        layout.addStretch()
        
        return sidebar
    
    def create_mini_meter(self, label, value, color):
        """Create compact progress meter"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(layout)
        
        # Label and value
        header = QHBoxLayout()
        name_label = QLabel(label)
        name_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 9pt;")
        header.addWidget(name_label)
        
        value_label = QLabel(f"{value}")
        value_label.setStyleSheet(f"font-weight: 700; color: {color}; font-size: 9pt;")
        header.addWidget(value_label)
        
        layout.addLayout(header)
        
        # Progress bar
        bar_bg = QFrame()
        bar_bg.setFixedHeight(6)
        bar_bg.setStyleSheet("background: #ecf0f1; border-radius: 3px;")
        
        bar_fill = QFrame(bar_bg)
        bar_fill.setFixedHeight(6)
        bar_fill.setFixedWidth(int((value / 100) * 270))
        bar_fill.setStyleSheet(f"background: {color}; border-radius: 3px;")
        
        layout.addWidget(bar_bg)
        
        return container
    
    def create_tabs(self):
        """Create tabbed content"""
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                background: white;
                border-radius: 12px;
                border: 1px solid #e1e8ed;
            }
            QTabBar::tab {
                background: transparent;
                color: #7f8c8d;
                padding: 12px 24px;
                margin-right: 5px;
                border: none;
                font-weight: 600;
                font-size: 10pt;
            }
            QTabBar::tab:selected {
                color: #3742fa;
                border-bottom: 3px solid #3742fa;
            }
            QTabBar::tab:hover:!selected {
                color: #2c3e50;
            }
        """)
        
        tabs.addTab(self.create_genetics_tab(), "🧬 Genetics")
        tabs.addTab(self.create_family_tab(), "👨‍👩‍👧 Family Tree")
        
        return tabs
    
    def create_genetics_tab(self):
        """Create genetics tab"""
        widget = QWidget()
        widget.setStyleSheet("background: white;")
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        widget.setLayout(layout)
        
        # Search box
        search_label = QLabel("💡 All genes organized by category")
        search_label.setStyleSheet("color: #95a5a6; font-style: italic; padding-bottom: 10px;")
        layout.addWidget(search_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(20)
        scroll_content.setLayout(scroll_layout)
        
        genetics = self.main_window.genetics_engine
        
        categories = {
            "🎨 Color Genetics": ["base_color", "dilution", "red", "inhibitor", "wide_band"],
            "🐆 Pattern Genetics": ["agouti", "tabby", "spotted", "ticked", "bengal"],
            "❄️ Color Restriction": ["color_restriction", "karpati"],
            "⚪ White Spotting": ["white"],
            "✨ Coat Type": ["fur_length"],
            "👁 Eye Pigmentation": ["eye_pigment_1", "eye_pigment_2", "eye_pigment_3", "lipochrome"]
        }
        
        for category, genes in categories.items():
            # Category header
            cat_header = QLabel(category)
            cat_header.setStyleSheet("""
                font-size: 12pt;
                font-weight: 700;
                color: #2c3e50;
                padding: 10px 0 5px 0;
            """)
            scroll_layout.addWidget(cat_header)
            
            # Gene grid
            gene_grid = QGridLayout()
            gene_grid.setSpacing(10)
            
            col = 0
            row = 0
            
            for gene_name in genes:
                if gene_name in self.cat.genes:
                    alleles = self.cat.genes[gene_name]
                    gene_info = genetics.get_gene_info(gene_name)
                    
                    if gene_info:
                        # Format data
                        display_name = gene_info['name']
                        
                        if len(alleles) == 1:
                            allele_text = alleles[0]
                            desc = genetics.get_allele_description(gene_name, alleles[0])
                        else:
                            dom = gene_info.get('dominance', {})
                            sorted_alleles = sorted(alleles, key=lambda a: dom.get(a, 0), reverse=True)
                            allele_text = f"{sorted_alleles[0]}/{sorted_alleles[1]}"
                            desc1 = genetics.get_allele_description(gene_name, sorted_alleles[0])
                            desc2 = genetics.get_allele_description(gene_name, sorted_alleles[1])
                            desc = f"{desc1}, {desc2}"
                        
                        # Get category color
                        color = "#3742fa" if "Color" in category else \
                                "#e74c3c" if "Pattern" in category else \
                                "#9b59b6" if "Restriction" in category else \
                                "#95a5a6" if "White" in category else \
                                "#f39c12" if "Coat" in category else "#1abc9c"
                        
                        gene_item = GeneItem(display_name, allele_text, desc, color)
                        gene_grid.addWidget(gene_item, row, col)
                        
                        col += 1
                        if col >= 2:
                            col = 0
                            row += 1
            
            scroll_layout.addLayout(gene_grid)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_family_tab(self):
        """Create family tab"""
        widget = QWidget()
        widget.setStyleSheet("background: white;")
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        widget.setLayout(layout)
        
        registry = self.main_window.registry
        
        # Parents
        parents_box = self.create_family_box("👨‍👩‍👧 Parents", "#27ae60")
        parents_layout = parents_box.layout()
        
        if self.cat.sire_id:
            sire = registry.get_cat(self.cat.sire_id)
            if sire:
                parents_layout.addWidget(self.create_family_member(
                    f"#{sire.id}" + (f" - {sire.name}" if sire.name else ""),
                    "Sire",
                    "♂",
                    "#3498db"
                ))
        
        if self.cat.dam_id:
            dam = registry.get_cat(self.cat.dam_id)
            if dam:
                parents_layout.addWidget(self.create_family_member(
                    f"#{dam.id}" + (f" - {dam.name}" if dam.name else ""),
                    "Dam",
                    "♀",
                    "#e74c3c"
                ))
        
        if not self.cat.sire_id and not self.cat.dam_id:
            no_parents = QLabel("🌟 Founder cat - No parents recorded")
            no_parents.setStyleSheet("color: #95a5a6; font-style: italic; padding: 10px;")
            parents_layout.addWidget(no_parents)
        
        layout.addWidget(parents_box)
        
        # Offspring
        offspring = registry.get_offspring(self.cat.id)
        offspring_box = self.create_family_box(f"👶 Offspring ({len(offspring)})", "#e67e22")
        offspring_layout = offspring_box.layout()
        
        if offspring:
            for child in offspring[:12]:
                sex_icon = "♂" if child.sex == "male" else "♀"
                sex_color = "#3498db" if child.sex == "male" else "#e74c3c"
                offspring_layout.addWidget(self.create_family_member(
                    f"#{child.id}" + (f" - {child.name}" if child.name else ""),
                    child.sex.capitalize(),
                    sex_icon,
                    sex_color
                ))
            
            if len(offspring) > 12:
                more = QLabel(f"... and {len(offspring) - 12} more offspring")
                more.setStyleSheet("color: #95a5a6; font-style: italic; padding: 10px;")
                offspring_layout.addWidget(more)
        else:
            no_offspring = QLabel("No offspring recorded yet")
            no_offspring.setStyleSheet("color: #95a5a6; font-style: italic; padding: 10px;")
            offspring_layout.addWidget(no_offspring)
        
        layout.addWidget(offspring_box)
        
        # Pedigree button
        pedigree_btn = QPushButton("🌳 View Interactive Pedigree Chart")
        pedigree_btn.setMinimumHeight(44)
        pedigree_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-weight: 700;
                font-size: 11pt;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #6a3f8f);
            }
        """)
        pedigree_btn.clicked.connect(self.show_pedigree)
        layout.addWidget(pedigree_btn)
        
        layout.addStretch()
        
        return widget
    
    def create_family_box(self, title, color):
        """Create family section box"""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background: #f8f9fa;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        box.setLayout(layout)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-weight: 700;
            font-size: 12pt;
            color: {color};
        """)
        layout.addWidget(title_label)
        
        return box
    
    def create_family_member(self, name, role, icon, color):
        """Create family member item"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e1e8ed;
                border-radius: 6px;
                padding: 10px;
            }}
            QFrame:hover {{
                border: 1px solid {color};
                background: #f8f9ff;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 18pt; color: {color}; background: transparent;")
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 10pt;")
        info_layout.addWidget(name_label)
        
        role_label = QLabel(role)
        role_label.setStyleSheet("color: #95a5a6; font-size: 8pt;")
        info_layout.addWidget(role_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return widget
    
    def create_footer(self):
        """Create footer"""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background: white;
                border-top: 1px solid #e1e8ed;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 15, 30, 15)
        footer.setLayout(layout)
        
        edit_btn = QPushButton("✏️ Edit Cat")
        edit_btn.setMinimumHeight(40)
        edit_btn.setMinimumWidth(120)
        edit_btn.setStyleSheet("""
            QPushButton {
                background: #3742fa;
                color: white;
                font-weight: 700;
                border-radius: 6px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: #2f3ce4;
            }
        """)
        edit_btn.clicked.connect(self.edit_cat)
        layout.addWidget(edit_btn)
        
        layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.setMinimumWidth(120)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #dfe4ea;
                color: #2f3542;
                font-weight: 700;
                border-radius: 6px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: #ced6e0;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        return footer
    
    def calculate_generation(self):
        """Calculate generation"""
        def get_gen(cat_id, depth=0):
            if depth > 50:
                return 0
            cat = self.main_window.registry.get_cat(cat_id)
            if not cat or (not cat.sire_id and not cat.dam_id):
                return 0
            sire_gen = get_gen(cat.sire_id, depth + 1) if cat.sire_id else 0
            dam_gen = get_gen(cat.dam_id, depth + 1) if cat.dam_id else 0
            return max(sire_gen, dam_gen) + 1
        return get_gen(self.cat.id)
    
    def show_pedigree(self):
        """Show pedigree"""
        from ui.dialogs.pedigree_dialog import PedigreeDialog
        dialog = PedigreeDialog(self.cat, self.main_window, self)
        dialog.exec()
    
    def edit_cat(self):
        """Edit cat"""
        from ui.dialogs.cat_editor_dialog import CatEditorDialog
        dialog = CatEditorDialog(self.cat, self.main_window, self)
        if dialog.exec():
            self.accept()
            new_dialog = CatDetailsDialog(self.cat, self.main_window, self.parent())
            new_dialog.exec()