"""
Breeding logic for generating offspring from parent cats
"""

import random
from typing import List
from core.cat import Cat


class BreedingEngine:
    """Handles breeding and offspring generation"""
    
    def __init__(self, genetics_engine):
        self.genetics = genetics_engine
    
    def breed_cats(self, sire: Cat, dam: Cat, litter_size: int, 
                   rarity_boost: float = 1.0) -> List[Cat]:
        """Generate a litter of kittens from two parent cats"""
        litter = []
        
        for _ in range(litter_size):
            sex = random.choice(['male', 'female'])
            genes = self._inherit_genes(sire, dam, sex)
            
            # Apply rarity mutations
            if rarity_boost > 1.0:
                genes = self._apply_rarity_mutations(genes, rarity_boost)
            
            # Calculate build and size with inheritance
            kitten_build = self._calculate_build(sire, dam)
            kitten_size = self._calculate_size(sire, dam, sex)
            
            kitten = Cat(
                sex=sex,
                genes=genes,
                sire_id=sire.id,
                dam_id=dam.id,
                build_value=kitten_build,
                size_value=kitten_size
            )
            
            litter.append(kitten)
        
        return litter
    
    def _inherit_genes(self, sire: Cat, dam: Cat, offspring_sex: str) -> dict:
        """Inherit genes from both parents following Mendelian genetics"""
        genes = {}
        
        for gene_name, gene_data in self.genetics.genes.items():
            # Skip quantitative traits handled separately
            if gene_name in ['build', 'size']:
                continue
            
            is_x_linked = gene_data.get('x_linked', False)
            
            if is_x_linked:
                if offspring_sex == 'male':
                    # Males get X from dam only
                    dam_alleles = dam.genes.get(gene_name, [])
                    genes[gene_name] = [random.choice(dam_alleles)] if dam_alleles else [gene_data['alleles'][0]]
                else:
                    # Females get X from both parents
                    sire_alleles = sire.genes.get(gene_name, [])
                    dam_alleles = dam.genes.get(gene_name, [])
                    a1 = sire_alleles[0] if sire_alleles else gene_data['alleles'][0]
                    a2 = random.choice(dam_alleles) if dam_alleles else gene_data['alleles'][0]
                    genes[gene_name] = [a1, a2]
            else:
                # Autosomal - one allele from each parent
                sire_alleles = sire.genes.get(gene_name, [])
                dam_alleles = dam.genes.get(gene_name, [])
                a1 = random.choice(sire_alleles) if sire_alleles else gene_data['alleles'][0]
                a2 = random.choice(dam_alleles) if dam_alleles else gene_data['alleles'][0]
                genes[gene_name] = [a1, a2]
        
        return genes
    
    def _apply_rarity_mutations(self, genes: dict, rarity_boost: float) -> dict:
        """Apply random mutations to create rarer alleles"""
        mutation_probability = min(0.4, (rarity_boost - 1.0) / 4.0)
        
        for gene_name, allele_pair in genes.items():
            gene_data = self.genetics.genes.get(gene_name, {})
            weights = [gene_data['weights'].get(a, 1) for a in gene_data['alleles']]
            
            # Invert weights to favor rare alleles
            max_w = max(weights) if weights else 1
            inverted = [max_w - w + 1 for w in weights]
            boosted = [w * rarity_boost for w in inverted]
            
            # Apply mutation chance to each allele
            for idx in range(len(allele_pair)):
                if random.random() < mutation_probability:
                    new_allele = random.choices(gene_data['alleles'], weights=boosted)[0]
                    allele_pair[idx] = new_allele
        
        return genes
    
    def _calculate_build(self, sire: Cat, dam: Cat) -> int:
        """Calculate offspring build using polygenic inheritance"""
        # Average of parents with small random variation
        build_avg = (sire.build_value + dam.build_value) / 2
        mutation = random.randint(-5, 5)
        return max(0, min(100, int(build_avg + mutation)))
    
    def _calculate_size(self, sire: Cat, dam: Cat, sex: str) -> int:
        """Calculate offspring size using polygenic inheritance with sexual dimorphism"""
        # Average of parents with small random variation
        size_avg = (sire.size_value + dam.size_value) / 2
        mutation = random.randint(-5, 5)
        kitten_size = max(0, min(100, int(size_avg + mutation)))
        
        # Apply sexual dimorphism - males trend larger
        if sex == 'male':
            kitten_size = min(100, kitten_size + random.randint(3, 8))
        
        return kitten_size
    
    def check_relatedness(self, cat1_id: int, cat2_id: int, 
                         registry: dict, max_generations: int = 3) -> bool:
        """Check if two cats are related within specified generations"""
        def get_ancestors(cat_id: int, depth: int = 0) -> set:
            if depth >= max_generations or cat_id not in registry:
                return set()
            
            cat = registry[cat_id]
            ancestors = {cat_id}
            
            if cat.sire_id:
                ancestors.update(get_ancestors(cat.sire_id, depth + 1))
            if cat.dam_id:
                ancestors.update(get_ancestors(cat.dam_id, depth + 1))
            
            return ancestors
        
        ancestors1 = get_ancestors(cat1_id)
        ancestors2 = get_ancestors(cat2_id)
        
        # Check for shared ancestors (excluding the cats themselves)
        shared = (ancestors1 & ancestors2) - {cat1_id, cat2_id}
        return len(shared) > 0