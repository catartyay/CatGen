"""
Modern Cat Details Dialog - Beautiful redesigned cat profile viewer
Replace: ui/dialogs/cat_details_dialog.py
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                               QPushButton, QLabel, QWidget, QTabWidget,
                               QGridLayout, QGroupBox, QScrollArea, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor


class InfoCard(QFrame):
    """Reusable card widget for displaying information"""
    
    def __init__(self, title, value, icon="", color="#4CAF50"):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 2px solid {color};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Icon and title
        header_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"font-size: 24pt; color: {color};")
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 10pt; color: #666; font-weight: normal;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {color};")
        value_label.setWordWrap(True)
        layout.addWidget(value_label)


class GeneCard(QFrame):
    """Card for displaying a single gene"""
    
    def __init__(self, gene_name, alleles, description):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #4CAF50;
                padding: 10px;
                margin: 2px;
            }
            QFrame:hover {
                background-color: #e8f5e9;
            }
        """)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Gene name
        name_label = QLabel(gene_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2c3e50;")
        layout.addWidget(name_label)
        
        # Alleles
        allele_label = QLabel(alleles)
        allele_label.setStyleSheet("font-size: 10pt; color: #34495e; font-family: 'Courier New';")
        layout.addWidget(allele_label)
        
        # Description
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("font-size: 9pt; color: #7f8c8d; font-style: italic;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)


class ModernCatDetailsDialog(QDialog):
    """Beautiful modern cat profile viewer"""
    
    def __init__(self, cat, main_window, parent=None):
        super().__init__(parent)
        self.cat = cat
        self.main_window = main_window
        self.setWindowTitle(f"Cat Profile - #{cat.id}")
        self.setModal(True)
        self.resize(1000, 750)
        
        # Set background
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the beautiful modern interface"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Header section with gradient
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content area
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content.setLayout(content_layout)
        
        # Quick stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        phenotype_calc = self.main_window.phenotype_calculator
        phenotype = phenotype_calc.calculate_phenotype(self.cat)
        eye_color = phenotype_calc.calculate_eye_color(self.cat)
        white_pct = phenotype_calc.get_white_percentage(self.cat)
        
        # Create stat cards
        stats_layout.addWidget(InfoCard("Sex", self.cat.sex.capitalize(), 
                                        "♂" if self.cat.sex == "male" else "♀", 
                                        "#3498db" if self.cat.sex == "male" else "#e91e63"))
        stats_layout.addWidget(InfoCard("Build", self.cat.get_build_phenotype(), "🏋️", "#9b59b6"))
        stats_layout.addWidget(InfoCard("Size", self.cat.get_size_phenotype(), "📏", "#f39c12"))
        stats_layout.addWidget(InfoCard("White", f"{white_pct}%", "⚪", "#95a5a6"))
        
        content_layout.addLayout(stats_layout)
        
        # Phenotype showcase
        pheno_card = QFrame()
        pheno_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                padding: 20px;
                margin-top: 15px;
            }
        """)
        pheno_layout = QVBoxLayout()
        pheno_card.setLayout(pheno_layout)
        
        pheno_title = QLabel("PHENOTYPE")
        pheno_title.setStyleSheet("color: white; font-size: 12pt; font-weight: bold;")
        pheno_layout.addWidget(pheno_title)
        
        pheno_text = QLabel(phenotype)
        pheno_text.setStyleSheet("color: white; font-size: 16pt; font-weight: 600;")
        pheno_text.setWordWrap(True)
        pheno_layout.addWidget(pheno_text)
        
        eye_label = QLabel(f"👁 Eyes: {eye_color}")
        eye_label.setStyleSheet("color: #f8f9fa; font-size: 11pt;")
        pheno_layout.addWidget(eye_label)
        
        content_layout.addWidget(pheno_card)
        
        # Tabbed content
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #bdc3c7;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #3498db;
            }
            QTabBar::tab:hover:!selected {
                background-color: #95a5a6;
            }
        """)
        
        # Genotype tab
        genotype_tab = self.create_genotype_tab()
        tabs.addTab(genotype_tab, "🧬 Genetics")
        
        # Pedigree tab
        pedigree_tab = self.create_pedigree_tab()
        tabs.addTab(pedigree_tab, "👨‍👩‍👧‍👦 Family")
        
        # Physical traits tab
        physical_tab = self.create_physical_tab()
        tabs.addTab(physical_tab, "📊 Physical Traits")
        
        content_layout.addWidget(tabs)
        layout.addWidget(content)
        
        # Footer with action buttons
        footer = self.create_footer()
        layout.addWidget(footer)
    
    def create_header(self):
        """Create beautiful header section"""
        header = QFrame()
        header.setMinimumHeight(120)
        
        # Gradient background based on sex
        if self.cat.sex == "male":
            gradient_colors = "stop:0 #667eea, stop:1 #764ba2"
        else:
            gradient_colors = "stop:0 #f093fb, stop:1 #f5576c"
        
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    {gradient_colors});
                border-radius: 0px;
            }}
        """)
        
        layout = QHBoxLayout()
        header.setLayout(layout)
        
        # Cat icon/placeholder
        icon_label = QLabel("🐱")
        icon_label.setStyleSheet("font-size: 48pt;")
        layout.addWidget(icon_label)
        
        # Cat info
        info_layout = QVBoxLayout()
        
        # Cat ID and name
        id_name = f"Cat #{self.cat.id}"
        if self.cat.name:
            id_name += f" • {self.cat.name}"
        
        name_label = QLabel(id_name)
        name_label.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: white;
            background: transparent;
        """)
        info_layout.addWidget(name_label)
        
        # Birth date
        if self.cat.birth_date:
            date_label = QLabel(f"📅 Born: {self.cat.birth_date}")
            date_label.setStyleSheet("font-size: 11pt; color: rgba(255,255,255,0.9); background: transparent;")
            info_layout.addWidget(date_label)
        
        # Generation info
        generation = self.calculate_generation()
        gen_label = QLabel(f"Generation {generation}")
        gen_label.setStyleSheet("font-size: 10pt; color: rgba(255,255,255,0.8); background: transparent;")
        info_layout.addWidget(gen_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return header
    
    def create_genotype_tab(self):
        """Create beautiful genotype display"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Search/filter bar
        search_label = QLabel("💡 Tip: Hover over gene cards to highlight")
        search_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 10px;")
        layout.addWidget(search_label)
        
        # Scrollable gene list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: white;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)
        
        genetics = self.main_window.genetics_engine
        
        # Organize genes by category
        categories = {
            "🎨 Color Genes": ["base_color", "dilution", "red", "inhibitor", "wide_band"],
            "🐆 Pattern Genes": ["agouti", "tabby", "spotted", "ticked", "bengal"],
            "❄️ Pointing & Restriction": ["color_restriction", "karpati"],
            "⚪ White Genes": ["white"],
            "✨ Physical Traits": ["fur_length"],
            "👁 Eye Color Genes": ["eye_pigment_1", "eye_pigment_2", "eye_pigment_3", "lipochrome"]
        }
        
        for category_name, gene_list in categories.items():
            # Category header
            cat_header = QLabel(category_name)
            cat_header.setStyleSheet("""
                font-size: 13pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px 0px 5px 0px;
                margin-top: 10px;
            """)
            scroll_layout.addWidget(cat_header)
            
            # Genes in category
            for gene_name in gene_list:
                if gene_name in self.cat.genes:
                    alleles = self.cat.genes[gene_name]
                    gene_info = genetics.get_gene_info(gene_name)
                    
                    if gene_info:
                        display_name = gene_info['name']
                        
                        # Format alleles
                        if len(alleles) == 1:
                            desc = genetics.get_allele_description(gene_name, alleles[0])
                            allele_text = f"{alleles[0]}"
                            desc_text = desc
                        else:
                            dom = gene_info.get('dominance', {})
                            sorted_alleles = sorted(alleles, 
                                                  key=lambda a: dom.get(a, 0), 
                                                  reverse=True)
                            desc1 = genetics.get_allele_description(gene_name, sorted_alleles[0])
                            desc2 = genetics.get_allele_description(gene_name, sorted_alleles[1])
                            allele_text = f"{sorted_alleles[0]}/{sorted_alleles[1]}"
                            desc_text = f"{desc1} / {desc2}"
                        
                        # Create gene card
                        gene_card = GeneCard(display_name, allele_text, desc_text)
                        scroll_layout.addWidget(gene_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_pedigree_tab(self):
        """Create family tree tab"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        widget.setLayout(layout)
        
        registry = self.main_window.registry
        
        # Parents section
        parents_frame = QFrame()
        parents_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e9;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        parents_layout = QVBoxLayout()
        parents_frame.setLayout(parents_layout)
        
        parents_title = QLabel("👨‍👩‍👧 Parents")
        parents_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2e7d32;")
        parents_layout.addWidget(parents_title)
        
        # Sire
        if self.cat.sire_id:
            sire = registry.get_cat(self.cat.sire_id)
            if sire:
                sire_text = f"♂ Sire: #{sire.id}"
                if sire.name:
                    sire_text += f" - {sire.name}"
                sire_label = QLabel(sire_text)
                sire_label.setStyleSheet("font-size: 12pt; color: #1976d2; padding: 5px;")
                parents_layout.addWidget(sire_label)
        
        # Dam
        if self.cat.dam_id:
            dam = registry.get_cat(self.cat.dam_id)
            if dam:
                dam_text = f"♀ Dam: #{dam.id}"
                if dam.name:
                    dam_text += f" - {dam.name}"
                dam_label = QLabel(dam_text)
                dam_label.setStyleSheet("font-size: 12pt; color: #c2185b; padding: 5px;")
                parents_layout.addWidget(dam_label)
        
        if not self.cat.sire_id and not self.cat.dam_id:
            no_parents = QLabel("No parents recorded (Founder)")
            no_parents.setStyleSheet("color: #7f8c8d; font-style: italic;")
            parents_layout.addWidget(no_parents)
        
        layout.addWidget(parents_frame)
        
        # Offspring section
        offspring = registry.get_offspring(self.cat.id)
        offspring_frame = QFrame()
        offspring_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3e0;
                border-radius: 12px;
                padding: 15px;
                margin-top: 15px;
            }
        """)
        offspring_layout = QVBoxLayout()
        offspring_frame.setLayout(offspring_layout)
        
        offspring_title = QLabel(f"👶 Offspring ({len(offspring)})")
        offspring_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #e65100;")
        offspring_layout.addWidget(offspring_title)
        
        if offspring:
            for child in offspring[:8]:
                child_text = f"#{child.id}"
                if child.name:
                    child_text += f" - {child.name}"
                child_text += f" ({child.sex})"
                
                child_label = QLabel(child_text)
                child_label.setStyleSheet("font-size: 11pt; color: #424242; padding: 3px;")
                offspring_layout.addWidget(child_label)
            
            if len(offspring) > 8:
                more_label = QLabel(f"... and {len(offspring) - 8} more")
                more_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
                offspring_layout.addWidget(more_label)
        else:
            no_offspring = QLabel("No offspring recorded")
            no_offspring.setStyleSheet("color: #7f8c8d; font-style: italic;")
            offspring_layout.addWidget(no_offspring)
        
        layout.addWidget(offspring_frame)
        
        # View pedigree button
        pedigree_btn = QPushButton("🌳 View Full Pedigree Chart")
        pedigree_btn.setMinimumHeight(45)
        pedigree_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 8px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        pedigree_btn.clicked.connect(self.show_pedigree)
        layout.addWidget(pedigree_btn)
        
        layout.addStretch()
        
        return widget
    
    def create_physical_tab(self):
        """Create physical traits visualization"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        widget.setLayout(layout)
        
        # Build meter
        build_frame = self.create_trait_meter(
            "Build Type",
            self.cat.build_value,
            self.cat.get_build_phenotype(),
            "#9b59b6"
        )
        layout.addWidget(build_frame)
        
        # Size meter
        size_frame = self.create_trait_meter(
            "Size Category",
            self.cat.size_value,
            self.cat.get_size_phenotype(),
            "#f39c12"
        )
        layout.addWidget(size_frame)
        
        # White percentage meter
        phenotype_calc = self.main_window.phenotype_calculator
        white_pct = phenotype_calc.get_white_percentage(self.cat)
        white_frame = self.create_trait_meter(
            "White Markings",
            white_pct,
            f"{white_pct}%",
            "#95a5a6"
        )
        layout.addWidget(white_frame)
        
        layout.addStretch()
        
        return widget
    
    def create_trait_meter(self, title, value, description, color):
        """Create a visual meter for a trait"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-radius: 12px;
                border-left: 5px solid {color};
                padding: 15px;
                margin-bottom: 15px;
            }}
        """)
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {color};")
        layout.addWidget(title_label)
        
        # Progress bar
        progress_bg = QFrame()
        progress_bg.setFixedHeight(30)
        progress_bg.setStyleSheet(f"""
            QFrame {{
                background-color: #ecf0f1;
                border-radius: 15px;
            }}
        """)
        
        progress_fill = QFrame(progress_bg)
        fill_width = int((value / 100) * progress_bg.width())
        progress_fill.setGeometry(0, 0, fill_width, 30)
        progress_fill.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 {self.lighten_color(color)});
                border-radius: 15px;
            }}
        """)
        
        layout.addWidget(progress_bg)
        
        # Value and description
        value_layout = QHBoxLayout()
        value_label = QLabel(f"{value}/100")
        value_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: #2c3e50;")
        value_layout.addWidget(value_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 11pt; color: #7f8c8d;")
        value_layout.addWidget(desc_label)
        value_layout.addStretch()
        
        layout.addLayout(value_layout)
        
        return frame
    
    def lighten_color(self, hex_color):
        """Lighten a hex color"""
        # Simple lightening by mixing with white
        return hex_color + "80"  # Add alpha for lighter appearance
    
    def create_footer(self):
        """Create footer with action buttons"""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #bdc3c7;
                padding: 15px;
            }
        """)
        layout = QHBoxLayout()
        footer.setLayout(layout)
        
        # Edit button
        edit_btn = QPushButton("✏️ Edit Cat")
        edit_btn.setMinimumHeight(40)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 0px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        edit_btn.clicked.connect(self.edit_cat)
        layout.addWidget(edit_btn)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.setMinimumWidth(100)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        return footer
    
    def calculate_generation(self):
        """Calculate generation number"""
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
        """Show pedigree dialog"""
        from ui.dialogs.pedigree_dialog import PedigreeDialog
        dialog = PedigreeDialog(self.cat, self.main_window, self)
        dialog.exec()
    
    def edit_cat(self):
        """Open cat editor"""
        from ui.dialogs.cat_editor_dialog import CatEditorDialog
        dialog = CatEditorDialog(self.cat, self.main_window, self)
        if dialog.exec():
            self.accept()
            # Reopen with updated data
            new_dialog = ModernCatDetailsDialog(self.cat, self.main_window, self.parent())
            new_dialog.exec()