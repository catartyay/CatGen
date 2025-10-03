"""
Cat service layer - centralized business logic for cat management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from core.cat import Cat
from core.events import EventBus, EventType

logger = logging.getLogger('catgen.services.cat')


class CatService:
    """
    Centralized service for cat management with caching and validation
    This layer sits between UI and data/core logic
    """
    
    def __init__(self, registry, genetics_engine, phenotype_calculator, event_bus: EventBus):
        self.registry = registry
        self.genetics = genetics_engine
        self.phenotype_calc = phenotype_calculator
        self.events = event_bus
        
        # Caches
        self._phenotype_cache: Dict[int, str] = {}
        self._eye_color_cache: Dict[int, str] = {}
        self._validation_cache: Dict[int, List] = {}
        
        # Subscribe to events for cache invalidation
        self.events.subscribe(EventType.CAT_UPDATED, self._on_cat_updated)
        self.events.subscribe(EventType.CAT_DELETED, self._on_cat_deleted)
        self.events.subscribe(EventType.GENE_MODIFIED, self._on_genes_changed)
        
    def create_cat(self, name: str = "", sex: str = "random", 
                   genes: Optional[Dict] = None, **kwargs) -> Cat:
        """
        Create a new cat with validation
        
        Args:
            name: Cat's name
            sex: 'male', 'female', or 'random'
            genes: Genetic makeup
            **kwargs: Additional cat attributes
            
        Returns:
            Created Cat object
            
        Raises:
            ValueError: If validation fails
        """
        # Create cat
        cat = Cat(name=name, sex=sex, genes=genes, **kwargs)
        
        # Validate before adding
        errors = self._validate_cat(cat)
        if any(e['severity'] == 'error' for e in errors):
            error_msgs = [e['message'] for e in errors if e['severity'] == 'error']
            raise ValueError(f"Cat validation failed: {'; '.join(error_msgs)}")
        
        # Add to registry
        cat_id = self.registry.add_cat(cat)
        
        # Emit event
        self.events.emit(EventType.CAT_ADDED, cat, source='CatService')
        
        logger.info(f"Created cat #{cat_id}: {name or 'Unnamed'}")
        return cat
    
    def update_cat(self, cat_id: int, **updates) -> Cat:
        """
        Update cat attributes
        
        Args:
            cat_id: ID of cat to update
            **updates: Attributes to update
            
        Returns:
            Updated Cat object
        """
        cat = self.registry.get_cat(cat_id)
        if not cat:
            raise ValueError(f"Cat #{cat_id} not found")
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(cat, key):
                setattr(cat, key, value)
        
        # Invalidate caches
        cat.invalidate_cache()
        self._invalidate_cat_cache(cat_id)
        
        # Emit event
        self.events.emit(EventType.CAT_UPDATED, cat, source='CatService')
        
        logger.info(f"Updated cat #{cat_id}")
        return cat
    
    def delete_cat(self, cat_id: int) -> bool:
        """Delete a cat from the registry"""
        if cat_id not in self.registry:
            raise ValueError(f"Cat #{cat_id} not found")
        
        # Check if cat has offspring
        offspring = self.registry.get_offspring(cat_id)
        if offspring:
            logger.warning(f"Deleting cat #{cat_id} which has {len(offspring)} offspring")
        
        # Remove from registry
        success = self.registry.remove_cat(cat_id)
        
        if success:
            # Invalidate caches
            self._invalidate_cat_cache(cat_id)
            
            # Emit event
            self.events.emit(EventType.CAT_DELETED, cat_id, source='CatService')
            
            logger.info(f"Deleted cat #{cat_id}")
        
        return success
    
    def get_phenotype(self, cat_id: int, use_cache: bool = True) -> str:
        """
        Get cat's phenotype with caching
        
        Args:
            cat_id: Cat ID
            use_cache: Whether to use cached value
            
        Returns:
            Phenotype description string
        """
        if use_cache and cat_id in self._phenotype_cache:
            return self._phenotype_cache[cat_id]
        
        cat = self.registry.get_cat(cat_id)
        if not cat:
            raise ValueError(f"Cat #{cat_id} not found")
        
        phenotype = self.phenotype_calc.calculate_phenotype(cat)
        self._phenotype_cache[cat_id] = phenotype
        
        return phenotype
    
    def get_eye_color(self, cat_id: int, use_cache: bool = True) -> str:
        """Get cat's eye color with caching"""
        if use_cache and cat_id in self._eye_color_cache:
            return self._eye_color_cache[cat_id]
        
        cat = self.registry.get_cat(cat_id)
        if not cat:
            raise ValueError(f"Cat #{cat_id} not found")
        
        eye_color = self.phenotype_calc.calculate_eye_color(cat)
        self._eye_color_cache[cat_id] = eye_color
        
        return eye_color
    
    def search_cats(self, query: str = "", filters: Optional[Dict] = None) -> List[Cat]:
        """
        Search cats with filters
        
        Args:
            query: Text search query
            filters: Dict with filter criteria (sex, has_parents, etc.)
            
        Returns:
            List of matching cats
        """
        results = self.registry.get_all_cats()
        
        # Apply text search
        if query:
            query = query.lower()
            results = [
                cat for cat in results
                if query in str(cat.id).lower() 
                or query in cat.name.lower()
                or query in self.get_phenotype(cat.id).lower()
            ]
        
        # Apply filters
        if filters:
            if 'sex' in filters and filters['sex'] != 'all':
                results = [cat for cat in results if cat.sex == filters['sex']]
            
            if filters.get('has_parents'):
                results = [cat for cat in results if cat.sire_id or cat.dam_id]
            
            if filters.get('has_offspring'):
                results = [
                    cat for cat in results 
                    if len(self.registry.get_offspring(cat.id)) > 0
                ]
            
            if 'fur_length' in filters and filters['fur_length'] != 'all':
                fur_type = filters['fur_length']
                results = [
                    cat for cat in results
                    if fur_type in self.get_phenotype(cat.id)
                ]
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        cats = self.registry.get_all_cats()
        
        stats = {
            'total': len(cats),
            'males': sum(1 for cat in cats if cat.sex == 'male'),
            'females': sum(1 for cat in cats if cat.sex == 'female'),
            'with_parents': sum(1 for cat in cats if cat.sire_id or cat.dam_id),
            'founders': sum(1 for cat in cats if not cat.sire_id and not cat.dam_id),
            'longhair': sum(1 for cat in cats if 'Longhair' in self.get_phenotype(cat.id)),
            'shorthair': sum(1 for cat in cats if 'Shorthair' in self.get_phenotype(cat.id)),
        }
        
        # Generation distribution
        generations = {}
        for cat in cats:
            gen = self._calculate_generation(cat.id)
            generations[gen] = generations.get(gen, 0) + 1
        
        stats['generations'] = generations
        
        return stats
    
    def _validate_cat(self, cat: Cat) -> List[Dict]:
        """
        Validate a cat's data
        
        Returns:
            List of validation errors/warnings
        """
        errors = []
        
        # Validate sex
        if cat.sex not in ['male', 'female']:
            errors.append({
                'field': 'sex',
                'message': f"Invalid sex: {cat.sex}",
                'severity': 'error'
            })
        
        # Validate genes
        for gene_name, alleles in cat.genes.items():
            gene_info = self.genetics.get_gene_info(gene_name)
            
            if not gene_info:
                errors.append({
                    'field': gene_name,
                    'message': f"Unknown gene: {gene_name}",
                    'severity': 'error'
                })
                continue
            
            # Check allele count
            expected_count = 1 if (gene_info.get('x_linked') and cat.sex == 'male') else 2
            if len(alleles) != expected_count:
                errors.append({
                    'field': gene_name,
                    'message': f"Expected {expected_count} allele(s), got {len(alleles)}",
                    'severity': 'error'
                })
            
            # Check allele validity
            valid_alleles = gene_info['alleles']
            for allele in alleles:
                if allele not in valid_alleles:
                    errors.append({
                        'field': gene_name,
                        'message': f"Invalid allele '{allele}' for gene {gene_name}",
                        'severity': 'error'
                    })
        
        # Validate parents exist
        if cat.sire_id and cat.sire_id not in self.registry:
            errors.append({
                'field': 'sire_id',
                'message': f"Sire #{cat.sire_id} not found in registry",
                'severity': 'warning'
            })
        
        if cat.dam_id and cat.dam_id not in self.registry:
            errors.append({
                'field': 'dam_id',
                'message': f"Dam #{cat.dam_id} not found in registry",
                'severity': 'warning'
            })
        
        # Validate parent sexes
        if cat.sire_id and cat.sire_id in self.registry:
            sire = self.registry.get_cat(cat.sire_id)
            if sire.sex != 'male':
                errors.append({
                    'field': 'sire_id',
                    'message': f"Sire #{cat.sire_id} is not male",
                    'severity': 'error'
                })
        
        if cat.dam_id and cat.dam_id in self.registry:
            dam = self.registry.get_cat(cat.dam_id)
            if dam.sex != 'female':
                errors.append({
                    'field': 'dam_id',
                    'message': f"Dam #{cat.dam_id} is not female",
                    'severity': 'error'
                })
        
        return errors
    
    def _calculate_generation(self, cat_id: int, depth: int = 0) -> int:
        """Calculate generation number (0 = founder)"""
        cat = self.registry.get_cat(cat_id)
        if not cat or (not cat.sire_id and not cat.dam_id):
            return 0
        
        if depth > 50:  # Prevent infinite recursion
            return 0
        
        sire_gen = self._calculate_generation(cat.sire_id, depth + 1) if cat.sire_id else 0
        dam_gen = self._calculate_generation(cat.dam_id, depth + 1) if cat.dam_id else 0
        
        return max(sire_gen, dam_gen) + 1
    
    def _invalidate_cat_cache(self, cat_id: int):
        """Invalidate all caches for a cat"""
        self._phenotype_cache.pop(cat_id, None)
        self._eye_color_cache.pop(cat_id, None)
        self._validation_cache.pop(cat_id, None)
    
    def _on_cat_updated(self, event):
        """Event handler for cat updates"""
        cat = event.data
        if cat and hasattr(cat, 'id'):
            self._invalidate_cat_cache(cat.id)
    
    def _on_cat_deleted(self, event):
        """Event handler for cat deletion"""
        cat_id = event.data
        if cat_id:
            self._invalidate_cat_cache(cat_id)
    
    def _on_genes_changed(self, event):
        """Event handler for gene modifications - invalidate all caches"""
        logger.info("Gene definitions changed, clearing all phenotype caches")
        self._phenotype_cache.clear()
        self._eye_color_cache.clear()
        self._validation_cache.clear()