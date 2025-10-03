"""
Visual Pedigree Chart - Interactive graphical pedigree viewer for CatGen
Place this file as: ui/dialogs/visual_pedigree_dialog.py
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QGraphicsView, QGraphicsScene, QGraphicsItem,
                               QGraphicsRectItem, QGraphicsTextItem, QLabel,
                               QComboBox, QFileDialog, QMessageBox, QGraphicsEllipseItem)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QLinearGradient, 
                          QFont, QPainterPath, QPixmap)
from typing import Dict


class CatNode(QGraphicsRectItem):
    """Graphical node representing a cat in the pedigree"""
    
    def __init__(self, cat, phenotype_calc, registry, generation=0, x=0, y=0):
        super().__init__()
        self.cat = cat
        self.phenotype_calc = phenotype_calc
        self.registry = registry
        self.generation = generation
        
        # Node dimensions
        self.node_width = 200
        self.node_height = 80
        
        # Position
        self.setRect(0, 0, self.node_width, self.node_height)
        self.setPos(x, y)
        
        # Make interactive
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        # Create visual elements
        self.setup_appearance()
        self.create_text_items()
        
        # Store for double-click handling
        self.on_double_click = None
    
    def setup_appearance(self):
        """Setup node colors and style based on cat sex"""
        if self.cat.sex == 'male':
            base_color = QColor(100, 149, 237)  # Cornflower blue
            light_color = QColor(135, 206, 250)
        else:
            base_color = QColor(255, 182, 193)  # Light pink
            light_color = QColor(255, 218, 224)
        
        gradient = QLinearGradient(0, 0, self.node_width, self.node_height)
        gradient.setColorAt(0, light_color)
        gradient.setColorAt(1, base_color)
        
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(QColor(60, 60, 60), 2))
    
    def create_text_items(self):
        """Create text elements within the node"""
        # Cat ID and name
        self.id_text = QGraphicsTextItem(self)
        id_str = f"#{self.cat.id}"
        if self.cat.name:
            id_str += f" - {self.cat.name[:15]}"
        self.id_text.setPlainText(id_str)
        self.id_text.setPos(5, 5)
        
        font = QFont("Arial", 10, QFont.Bold)
        self.id_text.setFont(font)
        self.id_text.setDefaultTextColor(QColor(40, 40, 40))
        
        # Phenotype (shortened)
        self.pheno_text = QGraphicsTextItem(self)
        phenotype = self.phenotype_calc.calculate_phenotype(self.cat)
        if len(phenotype) > 25:
            phenotype = phenotype[:22] + "..."
        self.pheno_text.setPlainText(phenotype)
        self.pheno_text.setPos(5, 28)
        
        pheno_font = QFont("Arial", 8)
        self.pheno_text.setFont(pheno_font)
        self.pheno_text.setDefaultTextColor(QColor(60, 60, 60))
        
        # Sex indicator
        self.sex_text = QGraphicsTextItem(self)
        sex_symbol = "♂" if self.cat.sex == 'male' else "♀"
        self.sex_text.setPlainText(sex_symbol)
        self.sex_text.setPos(self.node_width - 25, 5)
        
        sex_font = QFont("Arial", 16, QFont.Bold)
        self.sex_text.setFont(sex_font)
        self.sex_text.setDefaultTextColor(QColor(40, 40, 40))
        
        # Eye color indicator
        self.eye_text = QGraphicsTextItem(self)
        eye_color = self.phenotype_calc.calculate_eye_color(self.cat)
        eye_short = eye_color.split()[0] if eye_color else "Eyes"
        self.eye_text.setPlainText(f"👁 {eye_short}")
        self.eye_text.setPos(5, 50)
        
        eye_font = QFont("Arial", 7)
        self.eye_text.setFont(eye_font)
        self.eye_text.setDefaultTextColor(QColor(80, 80, 80))
    
    def paint(self, painter, option, widget):
        """Custom paint for rounded corners"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 10, 10)
        
        painter.fillPath(path, self.brush())
        painter.setPen(self.pen())
        painter.drawPath(path)
        
        if self.isSelected():
            highlight_pen = QPen(QColor(255, 215, 0), 3)
            painter.setPen(highlight_pen)
            painter.drawPath(path)
    
    def hoverEnterEvent(self, event):
        """Handle mouse hover enter"""
        self.setScale(1.05)
        self.setZValue(100)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle mouse hover leave"""
        self.setScale(1.0)
        self.setZValue(0)
        super().hoverLeaveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click"""
        if self.on_double_click:
            self.on_double_click(self.cat.id)
        super().mouseDoubleClickEvent(event)


class PedigreeConnection(QGraphicsItem):
    """Connection line between parent and child nodes"""
    
    def __init__(self, parent_node, child_node, is_sire=True):
        super().__init__()
        self.parent_node = parent_node
        self.child_node = child_node
        self.is_sire = is_sire
        self.setZValue(-1)
    
    def boundingRect(self):
        """Define bounding rectangle"""
        parent_pos = self.parent_node.scenePos()
        child_pos = self.child_node.scenePos()
        
        parent_point = parent_pos + QPointF(0, self.parent_node.node_height / 2)
        child_point = child_pos + QPointF(self.child_node.node_width, 
                                          self.child_node.node_height / 2)
        
        return QRectF(child_point, parent_point).normalized().adjusted(-5, -5, 5, 5)
    
    def paint(self, painter, option, widget):
        """Draw connection line"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        parent_pos = self.parent_node.scenePos()
        child_pos = self.child_node.scenePos()
        
        parent_point = parent_pos + QPointF(0, self.parent_node.node_height / 2)
        child_point = child_pos + QPointF(self.child_node.node_width, 
                                          self.child_node.node_height / 2)
        
        path = QPainterPath()
        path.moveTo(child_point)
        
        ctrl_x = (parent_point.x() + child_point.x()) / 2
        path.quadTo(QPointF(ctrl_x, child_point.y()), parent_point)
        
        color = QColor(100, 149, 237) if self.is_sire else QColor(255, 182, 193)
        pen = QPen(color, 2)
        painter.setPen(pen)
        painter.drawPath(path)


class VisualPedigreeDialog(QDialog):
    """Interactive visual pedigree chart dialog"""
    
    def __init__(self, cat, main_window, parent=None):
        super().__init__(parent)
        self.cat = cat
        self.main_window = main_window
        self.registry = main_window.registry
        self.phenotype_calc = main_window.phenotype_calculator
        
        self.cat_nodes: Dict[int, CatNode] = {}
        self.selected_cat_id = cat.id
        
        self.setWindowTitle(f"Visual Pedigree - Cat #{cat.id}")
        self.setModal(True)
        self.resize(1400, 800)
        
        self.setup_ui()
        self.build_pedigree()
    
    def setup_ui(self):
        """Create dialog interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_text = f"Visual Pedigree for Cat #{self.cat.id}"
        if self.cat.name:
            title_text += f" - {self.cat.name}"
        
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2c3e50; padding: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Generations:"))
        self.gen_combo = QComboBox()
        self.gen_combo.addItems(["3", "4", "5", "6"])
        self.gen_combo.setCurrentText("4")
        self.gen_combo.currentTextChanged.connect(self.rebuild_pedigree)
        header_layout.addWidget(self.gen_combo)
        
        layout.addLayout(header_layout)
        
        # Graphics view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setStyleSheet("background-color: #ecf0f1; border: 1px solid #bdc3c7;")
        layout.addWidget(self.view)
        
        # Info bar
        info_layout = QHBoxLayout()
        self.info_label = QLabel("Double-click a cat to view details • Drag to pan • Scroll to zoom")
        self.info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        
        legend = QLabel("♂ Male   ♀ Female")
        legend.setStyleSheet("padding: 5px; font-weight: bold;")
        info_layout.addWidget(legend)
        
        layout.addLayout(info_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        details_btn = QPushButton("📋 View Selected Cat Details")
        details_btn.clicked.connect(self.view_selected_details)
        button_layout.addWidget(details_btn)
        
        center_btn = QPushButton("🎯 Center View")
        center_btn.clicked.connect(self.center_view)
        button_layout.addWidget(center_btn)
        
        export_btn = QPushButton("💾 Export as Image")
        export_btn.clicked.connect(self.export_image)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def build_pedigree(self):
        """Build the pedigree tree"""
        self.scene.clear()
        self.cat_nodes.clear()
        
        generations = int(self.gen_combo.currentText())
        
        vertical_spacing = 120
        horizontal_spacing = 250
        
        subject_node = self.create_cat_node(
            self.cat, 
            generation=0,
            x=50,
            y=400
        )
        
        self.build_ancestors(
            subject_node,
            generation=1,
            max_gen=generations,
            base_x=50 + horizontal_spacing,
            vertical_spacing=vertical_spacing
        )
        
        self.center_view()
    
    def create_cat_node(self, cat, generation, x, y):
        """Create a cat node and add to scene"""
        node = CatNode(cat, self.phenotype_calc, self.registry, generation, x, y)
        node.on_double_click = self.on_node_double_clicked
        self.scene.addItem(node)
        self.cat_nodes[cat.id] = node
        return node
    
    def build_ancestors(self, child_node, generation, max_gen, base_x, vertical_spacing):
        """Recursively build ancestor tree"""
        if generation > max_gen:
            return
        
        cat = child_node.cat
        current_spacing = vertical_spacing / (2 ** (generation - 1))
        child_y = child_node.scenePos().y()
        
        sire_y = child_y - current_spacing
        dam_y = child_y + current_spacing
        
        if cat.sire_id and cat.sire_id in self.registry:
            sire = self.registry.get_cat(cat.sire_id)
            sire_node = self.create_cat_node(sire, generation, base_x, sire_y)
            
            connection = PedigreeConnection(sire_node, child_node, is_sire=True)
            self.scene.addItem(connection)
            
            self.build_ancestors(sire_node, generation + 1, max_gen, base_x + 250, vertical_spacing)
        
        if cat.dam_id and cat.dam_id in self.registry:
            dam = self.registry.get_cat(cat.dam_id)
            dam_node = self.create_cat_node(dam, generation, base_x, dam_y)
            
            connection = PedigreeConnection(dam_node, child_node, is_sire=False)
            self.scene.addItem(connection)
            
            self.build_ancestors(dam_node, generation + 1, max_gen, base_x + 250, vertical_spacing)
    
    def rebuild_pedigree(self):
        """Rebuild pedigree when generation count changes"""
        self.build_pedigree()
    
    def center_view(self):
        """Center and fit the view"""
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.scale(0.9, 0.9)
    
    def on_node_double_clicked(self, cat_id):
        """Handle node double click"""
        self.selected_cat_id = cat_id
        self.view_selected_details()
    
    def view_selected_details(self):
        """View details of selected cat"""
        if self.selected_cat_id:
            cat = self.registry.get_cat(self.selected_cat_id)
            if cat:
                from ui.dialogs.cat_details_dialog import CatDetailsDialog
                dialog = CatDetailsDialog(cat, self.main_window, self)
                dialog.exec()
    
    def export_image(self):
        """Export pedigree as image"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Pedigree",
            f"pedigree_cat_{self.cat.id}.png",
            "PNG Image (*.png);;JPEG Image (*.jpg)"
        )
        
        if filename:
            rect = self.scene.sceneRect()
            pixmap = QPixmap(int(rect.width()), int(rect.height()))
            pixmap.fill(Qt.white)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            self.scene.render(painter)
            painter.end()
            
            if pixmap.save(filename):
                QMessageBox.information(self, "Export Successful", f"Pedigree exported to:\n{filename}")
            else:
                QMessageBox.warning(self, "Export Failed", "Failed to export pedigree image")
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.view.scale(factor, factor)