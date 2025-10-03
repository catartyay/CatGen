"""
Breeding service layer - manages breeding operations and genetic predictions
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging
from core.cat import Cat
from core.breeding import BreedingEngine
from core.events import EventBus, EventType

logger = logging.getLogger('catgen.services.breeding')


class BreedingService:
    """
    Service layer for breeding operations
    Handles litter generation, genetic predictions, and breeding recommendations
    """
    
    def __init__(self, registry, genetics_engine, breeding_engine: BreedingEngine, 
                 phenotype_calculator, event_bus: EventBus):
        self.registry = registry
        self.genetics = genetics_engine
        self.breeding = breeding_engine
        self.phenotype_calc = phenotype_calculator
        self.events = event_bus
        
        self._pending_litters: Dict[str, List[Cat]] = {}
    
    def generate_litter(self, sire_id: int, dam_id: int, litter_size: int = 4,
                       rarity_boost: float = 1.0, validate: bool = True) -> Tuple[str, List[Cat]]:
        """
        Generate a litter from two parents
        
        Args:
            sire_id: Father's ID
            dam_id: Mother's ID
            litter_size: Number of kittens
            rarity_boost: Multiplier for rare alleles (1.0 = normal)
            validate: Whether to validate parents
            
        Returns:
            Tuple of (litter_id, list of kittens)
            
        Raises:
            ValueError: If validation fails
        """
        # Get parents
        sire = self.registry.get_cat(sire_id)
        dam = self.registry.get_cat(dam_id)
        
        if not sire:
            raise ValueError(f"Sire #{sire_id} not found")
        if not dam:
            raise ValueError(f"Dam #{dam_id} not found")
        
        # Validate if requested
        if validate:
            errors = self._validate_breeding_pair(sire, dam)
            if errors:
                raise ValueError(f"Breeding validation failed: {'; '.join(errors)}")
        
        # Emit breeding started event
        self.events.emit(
            EventType.BREEDING_STARTED,
            {'sire_id': sire_id, 'dam_id': dam_id, 'litter_size': litter_size},
            source='BreedingService'
        )
        
        # Generate litter
        litter = self.breeding.breed_cats(sire, dam, litter_size, rarity_boost)
        
        # Create litter ID
        litter_id = f"litter_{sire_id}x{dam_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._pending_litters[litter_id] = litter
        
        # Emit event
        self.events.emit(
            EventType.LITTER_GENERATED,
            {'litter_id': litter_id, 'kittens': litter},
            source='BreedingService'
        )
        
        logger.info(
            f"Generated litter {litter_id}: {litter_size} kittens from "
            f"#{sire_id} x #{dam_id}"
        )
        
        return litter_id, litter
    
    def save_litter(self, litter_id: str) -> List[int]:
        """
        Save pending litter to registry
        
        Args:
            litter_id: ID of pending litter
            
        Returns:
            List of assigned cat IDs
        """
        if litter_id not in self._pending_litters:
            raise ValueError(f"Litter {litter_id} not found in pending litters")
        
        litter = self._pending_litters[litter_id]
        cat_ids = []
        
        # Add each kitten to registry
        for kitten in litter:
            kitten.birth_date = datetime.now().strftime('%Y-%m-%d')
            cat_id = self.registry.add_cat(kitten)
            cat_ids.append(cat_id)
        
        # Remove from pending
        del self._pending_litters[litter_id]
        
        # Emit event
        self.events.emit(
            EventType.LITTER_SAVED,
            {'litter_id': litter_id, 'cat_ids': cat_ids},
            source='BreedingService'
        )
        
        logger.info(f"Saved litter {litter_id}: {len(cat_ids)} kittens")
        
        return cat_ids
    
    def discard_litter(self, litter_id: str):
        """Discard a pending litter without saving"""
        if litter_id in self._pending_litters:
            del self._pending_litters[litter_id]
            logger.info(f"Discarded litter {litter_id}")
    
    def get_pending_litter(self, litter_id: str) -> Optional[List[Cat]]:
        """Get a pending litter by ID"""
        return self._pending_litters.get(litter_id)
    
    def get_breeding_recommendations(self, target_traits: Optional[Dict] = None,
                                    max_pairs: int = 10) -> List[Dict]:
        """
        Get recommended breeding pairs based on criteria
        
        Args:
            target_traits: Desired traits (e.g., {'color': 'Black', 'pattern': 'Tabby'})
            max_pairs: Maximum number of recommendations
            
        Returns:
            List of recommended pairs with scores
        """
        males = self.registry.get_males()
        females = self.registry.get_females()
        
        if not males or not females:
            return []
        
        recommendations = []
        
        for sire in males:
            for dam in females:
                # Skip if related
                if self.breeding.check_relatedness(sire.id, dam.id, self.registry.cats):
                    continue
                
                # Calculate score
                score = self._score_breeding_pair(sire, dam, target_traits)
                
                recommendations.append({
                    'sire_id': sire.id,
                    'sire_name': sire.name or f"Cat #{sire.id}",
                    'dam_id': dam.id,
                    'dam_name': dam.name or f"Cat #{dam.id}",
                    'score': score,
                    'expected_traits': self._predict_offspring_traits(sire, dam)
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:max_pairs]
    
    def predict_offspring(self, sire_id: int, dam_id: int, 
                         num_simulations: int = 100) -> Dict:
        """
        Predict offspring characteristics through Monte Carlo simulation
        
        Args:
            sire_id: Father's ID
            dam_id: Mother's ID  
            num_simulations: Number of offspring to simulate
            
        Returns:
            Dictionary with prediction statistics
        """
        sire = self.registry.get_cat(sire_id)
        dam = self.registry.get_cat(dam_id)
        
        if not sire or not dam:
            raise ValueError("Both parents must exist")
        
        # Simulate many offspring
        phenotypes = []
        eye_colors = []
        sexes = []
        
        for _ in range(num_simulations):
            # Generate single offspring
            offspring = self.breeding.breed_cats(sire, dam, 1)[0]
            
            phenotypes.append(self.phenotype_calc.calculate_phenotype(offspring))
            eye_colors.append(self.phenotype_calc.calculate_eye_color(offspring))
            sexes.append(offspring.sex)
        
        # Calculate probabilities
        phenotype_dist = self._calculate_distribution(phenotypes)
        eye_color_dist = self._calculate_distribution(eye_colors)
        sex_dist = self._calculate_distribution(sexes)
        
        return {
            'simulations': num_simulations,
            'phenotype_probabilities': phenotype_dist,
            'eye_color_probabilities': eye_color_dist,
            'sex_ratio': sex_dist,
            'sire_id': sire_id,
            'dam_id': dam_id
        }
    
    def check_inbreeding(self, sire_id: int, dam_id: int, 
                        generations: int = 3) -> Dict:
        """
        Check for inbreeding and calculate coefficient
        
        Args:
            sire_id: Father's ID
            dam_id: Mother's ID
            generations: Generations to check
            
        Returns:
            Dictionary with inbreeding information
        """
        is_related = self.breeding.check_relatedness(
            sire_id, dam_id, self.registry.cats, generations
        )
        
        result = {
            'is_related': is_related,
            'generations_checked': generations,
            'common_ancestors': []
        }
        
        if is_related:
            # Find common ancestors
            sire_ancestors = self._get_ancestors(sire_id, generations)
            dam_ancestors = self._get_ancestors(dam_id, generations)
            common = sire_ancestors & dam_ancestors
            
            result['common_ancestors'] = [
                {
                    'id': cat_id,
                    'name': self.registry.get_cat(cat_id).name
                }
                for cat_id in common
            ]
            
            # Simple inbreeding coefficient estimation
            result['inbreeding_coefficient'] = len(common) / (generations * 2) if common else 0
        
        return result
    
    def _validate_breeding_pair(self, sire: Cat, dam: Cat) -> List[str]:
        """Validate a breeding pair"""
        errors = []
        
        # Check sexes
        if sire.sex != 'male':
            errors.append(f"Sire #{sire.id} is not male")
        if dam.sex != 'female':
            errors.append(f"Dam #{dam.id} is not female")
        
        # Check for same cat
        if sire.id == dam.id:
            errors.append("Cannot breed a cat with itself")
        
        # Warn about inbreeding
        if self.breeding.check_relatedness(sire.id, dam.id, self.registry.cats, 3):
            errors.append("Warning: Cats are related within 3 generations")
        
        return errors
    
    def _score_breeding_pair(self, sire: Cat, dam: Cat, 
                            target_traits: Optional[Dict] = None) -> float:
        """
        Score a breeding pair based on genetic diversity and target traits
        
        Returns score from 0-100
        """
        score = 50.0  # Base score
        
        # Penalize inbreeding
        if self.breeding.check_relatedness(sire.id, dam.id, self.registry.cats, 3):
            score -= 30
        
        # Reward genetic diversity
        diversity_score = self._calculate_genetic_diversity(sire, dam)
        score += diversity_score * 20
        
        # Match target traits if specified
        if target_traits:
            trait_match = self._calculate_trait_match(sire, dam, target_traits)
            score += trait_match * 30
        
        return max(0, min(100, score))
    
    def _calculate_genetic_diversity(self, sire: Cat, dam: Cat) -> float:
        """
        Calculate genetic diversity score (0-1) between two cats
        Higher = more diverse
        """
        differences = 0
        total_alleles = 0
        
        for gene_name in self.genetics.get_all_gene_names():
            sire_alleles = set(sire.genes.get(gene_name, []))
            dam_alleles = set(dam.genes.get(gene_name, []))
            
            # Count unique alleles
            all_alleles = sire_alleles | dam_alleles
            differences += len(all_alleles)
            total_alleles += len(sire_alleles) + len(dam_alleles)
        
        return differences / total_alleles if total_alleles > 0 else 0
    
    def _calculate_trait_match(self, sire: Cat, dam: Cat, 
                              target_traits: Dict) -> float:
        """Calculate how well offspring might match target traits (0-1)"""
        # Simplified - in reality would need probabilistic analysis
        score = 0.0
        trait_count = 0
        
        if 'color' in target_traits:
            # Check if parents could produce target color
            trait_count += 1
            # Simplified logic - would need full genetic analysis
            sire_pheno = self.phenotype_calc.calculate_phenotype(sire)
            dam_pheno = self.phenotype_calc.calculate_phenotype(dam)
            
            if target_traits['color'] in sire_pheno or target_traits['color'] in dam_pheno:
                score += 0.5
        
        return score / trait_count if trait_count > 0 else 0.5
    
    def _predict_offspring_traits(self, sire: Cat, dam: Cat) -> Dict:
        """Predict likely offspring traits"""
        # Generate a few sample offspring
        samples = self.breeding.breed_cats(sire, dam, 5, 1.0)
        
        phenotypes = [self.phenotype_calc.calculate_phenotype(k) for k in samples]
        eye_colors = [self.phenotype_calc.calculate_eye_color(k) for k in samples]
        
        # Get most common
        from collections import Counter
        pheno_common = Counter(phenotypes).most_common(2)
        eye_common = Counter(eye_colors).most_common(2)
        
        return {
            'likely_phenotypes': [p[0] for p in pheno_common],
            'likely_eye_colors': [e[0] for e in eye_common],
            'sex_ratio': '50% male, 50% female'
        }
    
    def _calculate_distribution(self, values: List[str]) -> Dict[str, float]:
        """Calculate probability distribution from list of values"""
        from collections import Counter
        counts = Counter(values)
        total = len(values)
        return {
            value: count / total
            for value, count in counts.items()
        }
    
    def _get_ancestors(self, cat_id: int, generations: int) -> set:
        """Get all ancestors up to N generations"""
        if generations <= 0:
            return set()
        
        ancestors = set()
        cat = self.registry.get_cat(cat_id)
        
        if not cat:
            return ancestors
        
        if cat.sire_id:
            ancestors.add(cat.sire_id)
            ancestors.update(self._get_ancestors(cat.sire_id, generations - 1))
        
        if cat.dam_id:
            ancestors.add(cat.dam_id)
            ancestors.update(self._get_ancestors(cat.dam_id, generations - 1))
        
        return ancestors