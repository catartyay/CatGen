"""
Dialog for viewing detailed cat information
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                               QPushButton, QLabel, QWidget, QTabWidget,
                               QGridLayout, QGroupBox, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class CatDetailsDialog(QDialog):
    """Display detailed information about a cat"""
    
    def __init__(self, cat, main_window, parent=None):
        super().__init__(parent)
        self.cat = cat
        self.main_window = main_window
        self.setWindowTitle(f"Cat #{cat.id} Details")
        self.setModal(True)
        self.resize(900, 700)
        self.setup_ui()
    
    def setup_ui(self):
        """Create the dialog interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header section
        header = self.create_header()
        layout.addWidget(header)
        
        # Tabbed content
        tabs = QTabWidget()
        
        # Phenotype tab
        phenotype_tab = self.create_phenotype_tab()
        tabs.addTab(phenotype_tab, "Phenotype")
        
        # Genotype tab
        genotype_tab = self.create_genotype_tab()
        tabs.addTab(genotype_tab, "Genotype")
        
        # Pedigree tab
        pedigree_tab = self.create_pedigree_tab()
        tabs.addTab(pedigree_tab, "Pedigree")
        
        layout.addWidget(tabs)
        
        # Close button
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def create_header(self):
        """Create attractive header with cat ID and name"""
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: white;
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout()
        header_widget.setLayout(layout)
        
        # Cat ID
        id_label = QLabel(f"Cat #{self.cat.id}")
        id_font = QFont()
        id_font.setPointSize(24)
        id_font.setBold(True)
        id_label.setFont(id_font)
        layout.addWidget(id_label)
        
        # Cat name (if exists)
        if self.cat.name:
            name_label = QLabel(self.cat.name)
            name_font = QFont()
            name_font.setPointSize(16)
            name_label.setFont(name_font)
            layout.addWidget(name_label)
        
        # Basic info
        info_layout = QHBoxLayout()
        sex_label = QLabel(f"Sex: {self.cat.sex.capitalize()}")
        birth_label = QLabel(f"Born: {self.cat.birth_date}")
        info_layout.addWidget(sex_label)
        info_layout.addWidget(birth_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        return header_widget
    
    def create_phenotype_tab(self):
        """Create phenotype display tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        phenotype_calc = self.main_window.phenotype_calculator
        
        # Appearance section
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QGridLayout()
        appearance_group.setLayout(appearance_layout)
        
        row = 0
        
        # Coat description
        phenotype = phenotype_calc.calculate_phenotype(self.cat)
        appearance_layout.addWidget(QLabel("Coat:"), row, 0, Qt.AlignRight)
        coat_label = QLabel(phenotype)
        coat_label.setWordWrap(True)
        coat_font = QFont()
        coat_font.setPointSize(11)
        coat_font.setBold(True)
        coat_label.setFont(coat_font)
        appearance_layout.addWidget(coat_label, row, 1)
        row += 1
        
        # Eye color
        eye_color = phenotype_calc.calculate_eye_color(self.cat)
        appearance_layout.addWidget(QLabel("Eyes:"), row, 0, Qt.AlignRight)
        eye_label = QLabel(eye_color)
        eye_font = QFont()
        eye_font.setPointSize(11)
        eye_label.setFont(eye_font)
        appearance_layout.addWidget(eye_label, row, 1)
        row += 1
        
        # White markings
        white_pct = phenotype_calc.get_white_percentage(self.cat)
        appearance_layout.addWidget(QLabel("White Markings:"), row, 0, Qt.AlignRight)
        appearance_layout.addWidget(QLabel(f"{white_pct}%"), row, 1)
        row += 1
        
        layout.addWidget(appearance_group)
        
        # Physical traits section
        physical_group = QGroupBox("Physical Traits")
        physical_layout = QGridLayout()
        physical_group.setLayout(physical_layout)
        
        physical_layout.addWidget(QLabel("Build:"), 0, 0, Qt.AlignRight)
        physical_layout.addWidget(QLabel(f"{self.cat.get_build_phenotype()} ({self.cat.build_value}/100)"), 0, 1)
        
        physical_layout.addWidget(QLabel("Size:"), 1, 0, Qt.AlignRight)
        physical_layout.addWidget(QLabel(f"{self.cat.get_size_phenotype()} ({self.cat.size_value}/100)"), 1, 1)
        
        layout.addWidget(physical_group)
        layout.addStretch()
        
        return widget
    
    def create_genotype_tab(self):
        """Create genotype display tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)
        
        genetics = self.main_window.genetics_engine
        
        # Group genes by category (you can customize these)
        categories = {
            "Color Genes": ["base_color", "dilution", "red", "inhibitor", "wide_band"],
            "Pattern Genes": ["agouti", "tabby", "spotted", "ticked", "bengal"],
            "Pointing & Restriction": ["color_restriction", "karpati"],
            "White": ["white"],
            "Physical": ["fur_length"],
            "Eye Color": ["eye_pigment_1", "eye_pigment_2", "eye_pigment_3", "lipochrome"]
        }
        
        for category_name, gene_list in categories.items():
            group = QGroupBox(category_name)
            group_layout = QGridLayout()
            group.setLayout(group_layout)
            
            row = 0
            for gene_name in gene_list:
                if gene_name in self.cat.genes:
                    alleles = self.cat.genes[gene_name]
                    gene_info = genetics.get_gene_info(gene_name)
                    
                    if gene_info:
                        display_name = gene_info['name']
                        
                        # Gene name
                        name_label = QLabel(f"{display_name}:")
                        name_label.setStyleSheet("font-weight: bold;")
                        group_layout.addWidget(name_label, row, 0, Qt.AlignRight)
                        
                        # Alleles
                        if len(alleles) == 1:
                            desc = genetics.get_allele_description(gene_name, alleles[0])
                            allele_text = f"{alleles[0]} ({desc})"
                        else:
                            # Sort by dominance
                            dom = gene_info.get('dominance', {})
                            sorted_alleles = sorted(alleles, 
                                                  key=lambda a: dom.get(a, 0), 
                                                  reverse=True)
                            desc1 = genetics.get_allele_description(gene_name, sorted_alleles[0])
                            desc2 = genetics.get_allele_description(gene_name, sorted_alleles[1])
                            allele_text = f"{sorted_alleles[0]}/{sorted_alleles[1]} ({desc1}/{desc2})"
                        
                        allele_label = QLabel(allele_text)
                        group_layout.addWidget(allele_label, row, 1)
                        
                        row += 1
            
            scroll_layout.addWidget(group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def create_pedigree_tab(self):
        """Create pedigree display tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        registry = self.main_window.registry
        
        # Parents section
        parents_group = QGroupBox("Parents")
        parents_layout = QGridLayout()
        parents_group.setLayout(parents_layout)
        
        row = 0
        if self.cat.sire_id:
            sire = registry.get_cat(self.cat.sire_id)
            parents_layout.addWidget(QLabel("Sire:"), row, 0, Qt.AlignRight)
            if sire:
                sire_text = f"#{sire.id}"
                if sire.name:
                    sire_text += f" - {sire.name}"
                parents_layout.addWidget(QLabel(sire_text), row, 1)
            else:
                parents_layout.addWidget(QLabel(f"#{self.cat.sire_id} (not found)"), row, 1)
            row += 1
        
        if self.cat.dam_id:
            dam = registry.get_cat(self.cat.dam_id)
            parents_layout.addWidget(QLabel("Dam:"), row, 0, Qt.AlignRight)
            if dam:
                dam_text = f"#{dam.id}"
                if dam.name:
                    dam_text += f" - {dam.name}"
                parents_layout.addWidget(QLabel(dam_text), row, 1)
            else:
                parents_layout.addWidget(QLabel(f"#{self.cat.dam_id} (not found)"), row, 1)
            row += 1
        
        if row == 0:
            parents_layout.addWidget(QLabel("No parents recorded"), 0, 0)
        
        layout.addWidget(parents_group)
        
        # Offspring section
        offspring = registry.get_offspring(self.cat.id)
        offspring_group = QGroupBox(f"Offspring ({len(offspring)})")
        offspring_layout = QVBoxLayout()
        offspring_group.setLayout(offspring_layout)
        
        if offspring:
            for child in offspring[:10]:  # Show first 10
                child_text = f"#{child.id}"
                if child.name:
                    child_text += f" - {child.name}"
                child_text += f" ({child.sex.capitalize()})"
                offspring_layout.addWidget(QLabel(child_text))
            
            if len(offspring) > 10:
                offspring_layout.addWidget(QLabel(f"... and {len(offspring) - 10} more"))
        else:
            offspring_layout.addWidget(QLabel("No offspring recorded"))
        
        layout.addWidget(offspring_group)
        layout.addStretch()
        
        return widget