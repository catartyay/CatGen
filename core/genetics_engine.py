"""
Genetics engine for loading gene definitions and calculating dominance
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class GeneticsEngine:
    """Manages gene definitions and genetic calculations"""
    
    def __init__(self, genes_path: str = 'resources/genes.json', 
                 interactions_path: str = 'resources/gene_interactions.json'):
        self.genes_path = Path(genes_path)
        self.interactions_path = Path(interactions_path)
        self.genes: Dict = {}
        self.interactions: Dict = {}
        self.load_data()
    
    def load_data(self):
        """Load gene definitions and interactions from JSON files"""
        try:
            if self.genes_path.exists():
                with open(self.genes_path, 'r') as f:
                    self.genes = json.load(f)
            else:
                print(f"Warning: {self.genes_path} not found. Using empty gene set.")
                
            if self.interactions_path.exists():
                with open(self.interactions_path, 'r') as f:
                    self.interactions = json.load(f)
            else:
                print(f"Warning: {self.interactions_path} not found.")
        except Exception as e:
            print(f"Error loading genetics data: {e}")
    
    def save_genes(self):
        """Save gene definitions to JSON file"""
        self.genes_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.genes_path, 'w') as f:
            json.dump(self.genes, f, indent=2)
    
    def save_interactions(self):
        """Save interaction rules to JSON file"""
        self.interactions_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.interactions_path, 'w') as f:
            json.dump(self.interactions, f, indent=2)
    
    def get_dominant_allele(self, gene_name: str, alleles: List[str]) -> str:
        """Determine which allele is dominant"""
        gene = self.genes.get(gene_name)
        if not gene or len(alleles) == 1:
            return alleles[0] if alleles else None
        
        dom1 = gene['dominance'].get(alleles[0], 0)
        dom2 = gene['dominance'].get(alleles[1], 0)
        return alleles[0] if dom1 >= dom2 else alleles[1]
    
    def get_gene_info(self, gene_name: str) -> Optional[Dict]:
        """Get complete information about a gene"""
        return self.genes.get(gene_name)
    
    def get_allele_description(self, gene_name: str, allele: str) -> str:
        """Get human-readable description of an allele"""
        gene = self.genes.get(gene_name, {})
        return gene.get('descriptions', {}).get(allele, allele)
    
    def is_x_linked(self, gene_name: str) -> bool:
        """Check if a gene is X-linked"""
        gene = self.genes.get(gene_name, {})
        return gene.get('x_linked', False)
    
    def get_all_gene_names(self) -> List[str]:
        """Get list of all gene names"""
        return list(self.genes.keys())
    
    def add_gene(self, gene_id: str, gene_data: Dict):
        """Add a new gene definition"""
        self.genes[gene_id] = gene_data
    
    def remove_gene(self, gene_id: str):
        """Remove a gene definition"""
        if gene_id in self.genes:
            del self.genes[gene_id]
    
    def update_gene(self, gene_id: str, gene_data: Dict):
        """Update an existing gene definition"""
        if gene_id in self.genes:
            self.genes[gene_id] = gene_data