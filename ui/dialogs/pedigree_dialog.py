"""
Pedigree viewer dialog - displays multi-generation ancestry
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                               QPushButton, QLabel)
from PySide6.QtCore import Qt


class PedigreeDialog(QDialog):
    """Display pedigree chart for a cat"""
    
    def __init__(self, cat, main_window, parent=None):
        super().__init__(parent)
        self.cat = cat
        self.main_window = main_window
        self.setWindowTitle(f"Pedigree - Cat #{cat.id}")
        self.setModal(True)
        self.resize(1200, 800)
        self.setup_ui()
    
    def setup_ui(self):
        """Create dialog interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_text = f"PEDIGREE FOR CAT #{self.cat.id}"
        if self.cat.name:
            title_text += f" - {self.cat.name}"
        
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Pedigree text
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFontFamily("Courier")
        layout.addWidget(self.text_edit)
        
        # Generate pedigree
        pedigree_text = self.build_pedigree()
        self.text_edit.setPlainText(pedigree_text)
        
        # Close button
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def build_pedigree(self):
        """Build pedigree chart"""
        if not self.cat.sire_id and not self.cat.dam_id:
            return "No pedigree information available for this cat."
        
        registry = self.main_window.registry
        phenotype_calc = self.main_window.phenotype_calculator
        
        def get_cat_info(cat_id):
            """Get formatted cat information"""
            if cat_id and cat_id in registry:
                cat = registry.get_cat(cat_id)
                name = cat.name if cat.name else f"Cat #{cat.id}"
                phenotype = phenotype_calc.calculate_phenotype(cat)
                return f"#{cat.id} {name}\n{phenotype}"
            return "Unknown"
        
        def get_ancestors(cat_obj, generation):
            """Recursively get ancestors"""
            if generation == 0 or not cat_obj:
                return None
            
            sire = registry.get_cat(cat_obj.sire_id) if cat_obj.sire_id else None
            dam = registry.get_cat(cat_obj.dam_id) if cat_obj.dam_id else None
            
            return {
                'sire': sire,
                'dam': dam,
                'sire_ancestors': get_ancestors(sire, generation - 1) if sire else None,
                'dam_ancestors': get_ancestors(dam, generation - 1) if dam else None
            }
        
        # Build pedigree structure (4 generations)
        pedigree = get_ancestors(self.cat, 4)
        
        # Create text output
        lines = []
        lines.append(f"Subject: {get_cat_info(self.cat.id)}")
        lines.append("=" * 100)
        lines.append("")
        
        if not pedigree:
            return "\n".join(lines) + "\nNo pedigree information available."
        
        # Generation 1: Parents
        lines.append("PARENTS:")
        lines.append("-" * 100)
        
        if pedigree['sire']:
            lines.append(f"Sire:  {get_cat_info(pedigree['sire'].id)}")
        else:
            lines.append("Sire:  Unknown")
        
        lines.append("")
        
        if pedigree['dam']:
            lines.append(f"Dam:   {get_cat_info(pedigree['dam'].id)}")
        else:
            lines.append("Dam:   Unknown")
        
        lines.append("")
        lines.append("")
        
        # Generation 2: Grandparents
        lines.append("GRANDPARENTS:")
        lines.append("-" * 100)
        
        sire_anc = pedigree.get('sire_ancestors')
        dam_anc = pedigree.get('dam_ancestors')
        
        if sire_anc:
            if sire_anc['sire']:
                lines.append(f"Paternal Grandsire: {get_cat_info(sire_anc['sire'].id)}")
            else:
                lines.append("Paternal Grandsire: Unknown")
            
            lines.append("")
            
            if sire_anc['dam']:
                lines.append(f"Paternal Granddam:  {get_cat_info(sire_anc['dam'].id)}")
            else:
                lines.append("Paternal Granddam:  Unknown")
        else:
            lines.append("Paternal Grandparents: Unknown")
        
        lines.append("")
        
        if dam_anc:
            if dam_anc['sire']:
                lines.append(f"Maternal Grandsire: {get_cat_info(dam_anc['sire'].id)}")
            else:
                lines.append("Maternal Grandsire: Unknown")
            
            lines.append("")
            
            if dam_anc['dam']:
                lines.append(f"Maternal Granddam:  {get_cat_info(dam_anc['dam'].id)}")
            else:
                lines.append("Maternal Granddam:  Unknown")
        else:
            lines.append("Maternal Grandparents: Unknown")
        
        lines.append("")
        lines.append("")
        
        # Generation 3: Great-grandparents (simplified)
        lines.append("GREAT-GRANDPARENTS:")
        lines.append("-" * 100)
        
        gg_count = 0
        
        if sire_anc:
            if sire_anc.get('sire_ancestors'):
                ssa = sire_anc['sire_ancestors']
                if ssa['sire']:
                    lines.append(f"  #{ssa['sire'].id} - Paternal Great-Grandsire (Sire's Sire's Sire)")
                    gg_count += 1
                if ssa['dam']:
                    lines.append(f"  #{ssa['dam'].id} - Paternal Great-Granddam (Sire's Sire's Dam)")
                    gg_count += 1
            
            if sire_anc.get('dam_ancestors'):
                sda = sire_anc['dam_ancestors']
                if sda['sire']:
                    lines.append(f"  #{sda['sire'].id} - Paternal Great-Grandsire (Sire's Dam's Sire)")
                    gg_count += 1
                if sda['dam']:
                    lines.append(f"  #{sda['dam'].id} - Paternal Great-Granddam (Sire's Dam's Dam)")
                    gg_count += 1
        
        if dam_anc:
            if dam_anc.get('sire_ancestors'):
                dsa = dam_anc['sire_ancestors']
                if dsa['sire']:
                    lines.append(f"  #{dsa['sire'].id} - Maternal Great-Grandsire (Dam's Sire's Sire)")
                    gg_count += 1
                if dsa['dam']:
                    lines.append(f"  #{dsa['dam'].id} - Maternal Great-Granddam (Dam's Sire's Dam)")
                    gg_count += 1
            
            if dam_anc.get('dam_ancestors'):
                dda = dam_anc['dam_ancestors']
                if dda['sire']:
                    lines.append(f"  #{dda['sire'].id} - Maternal Great-Grandsire (Dam's Dam's Sire)")
                    gg_count += 1
                if dda['dam']:
                    lines.append(f"  #{dda['dam'].id} - Maternal Great-Granddam (Dam's Dam's Dam)")
                    gg_count += 1
        
        if gg_count == 0:
            lines.append("  No great-grandparent information available")
        
        return "\n".join(lines)