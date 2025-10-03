"""
Genetic diversity analysis for cat populations
"""

from typing import Dict, List, Tuple, Optional
from collections import Counter
import logging

logger = logging.getLogger('catgen.analytics')


class DiversityAnalyzer:
    """
    Analyze genetic diversity in the cat population
    Provides metrics for breeding decisions and population health
    """
    
    def __init__(self, registry, genetics_engine):
        self.registry = registry
        self.genetics = genetics_engine
    
    def calculate_allele_frequencies(self, gene_name: Optional[str] = None) -> Dict:
        """
        Calculate allele frequencies across the population
        
        Args:
            gene_name: Specific gene to analyze, or None for all genes
            
        Returns:
            Dictionary mapping gene names to allele frequency distributions
        """
        if gene_name:
            genes_to_analyze = [gene_name]
        else:
            genes_to_analyze = self.genetics.get_all_gene_names()
        
        frequencies = {}
        
        for gene in genes_to_analyze:
            gene_info = self.genetics.get_gene_info(gene)
            if not gene_info:
                continue
            
            allele_counts = Counter()
            total_alleles = 0
            
            for cat in self.registry.get_all_cats():
                if gene in cat.genes:
                    for allele in cat.genes[gene]:
                        allele_counts[allele] += 1
                        total_alleles += 1
            
            if total_alleles > 0:
                frequencies[gene] = {
                    'counts': dict(allele_counts),
                    'frequencies': {
                        allele: count / total_alleles
                        for allele, count in allele_counts.items()
                    },
                    'total_alleles': total_alleles,
                    'unique_alleles': len(allele_counts)
                }
        
        return frequencies
    
    def calculate_heterozygosity(self) -> Dict[str, Dict]:
        """
        Calculate observed and expected heterozygosity for each locus
        
        Returns:
            Dictionary with observed (Ho) and expected (He) heterozygosity
        """
        results = {}
        
        for gene_name in self.genetics.get_all_gene_names():
            gene_info = self.genetics.get_gene_info(gene_name)
            
            # Skip X-linked genes for males
            if gene_info.get('x_linked'):
                continue
            
            het_count = 0
            hom_count = 0
            
            # Get allele frequencies
            freq_data = self.calculate_allele_frequencies(gene_name)
            if gene_name not in freq_data:
                continue
            
            allele_freqs = freq_data[gene_name]['frequencies']
            
            # Calculate observed heterozygosity
            for cat in self.registry.get_all_cats():
                if gene_name in cat.genes and len(cat.genes[gene_name]) == 2:
                    if cat.genes[gene_name][0] != cat.genes[gene_name][1]:
                        het_count += 1
                    else:
                        hom_count += 1
            
            total = het_count + hom_count
            if total == 0:
                continue
            
            observed_het = het_count / total
            
            # Calculate expected heterozygosity (1 - sum of squared frequencies)
            expected_het = 1 - sum(freq ** 2 for freq in allele_freqs.values())
            
            results[gene_name] = {
                'observed': observed_het,
                'expected': expected_het,
                'heterozygotes': het_count,
                'homozygotes': hom_count,
                'f_statistic': (expected_het - observed_het) / expected_het if expected_het > 0 else 0
            }
        
        return results
    
    def effective_population_size(self) -> Dict:
        """
        Calculate effective population size (Ne)
        
        Returns:
            Dictionary with Ne and related metrics
        """
        males = len(self.registry.get_males())
        females = len(self.registry.get_females())
        total = males + females
        
        # Effective population size formula: Ne = (4 * Nm * Nf) / (Nm + Nf)
        if males > 0 and females > 0:
            ne = (4 * males * females) / (males + females)
        else:
            ne = 0
        
        # Calculate breeding population (cats with offspring)
        breeding_males = sum(
            1 for cat in self.registry.get_males()
            if len(self.registry.get_offspring(cat.id)) > 0
        )
        breeding_females = sum(
            1 for cat in self.registry.get_females()
            if len(self.registry.get_offspring(cat.id)) > 0
        )
        
        if breeding_males > 0 and breeding_females > 0:
            breeding_ne = (4 * breeding_males * breeding_females) / (breeding_males + breeding_females)
        else:
            breeding_ne = 0
        
        return {
            'total_population': total,
            'males': males,
            'females': females,
            'effective_size': ne,
            'breeding_males': breeding_males,
            'breeding_females': breeding_females,
            'breeding_effective_size': breeding_ne,
            'sex_ratio': males / females if females > 0 else 0
        }
    
    def identify_rare_alleles(self, threshold: float = 0.05) -> Dict[str, List]:
        """
        Identify rare alleles in the population
        
        Args:
            threshold: Frequency below which allele is considered rare
            
        Returns:
            Dictionary mapping genes to lists of rare alleles
        """
        frequencies = self.calculate_allele_frequencies()
        rare_alleles = {}
        
        for gene_name, freq_data in frequencies.items():
            rare = []
            for allele, freq in freq_data['frequencies'].items():
                if freq < threshold:
                    rare.append({
                        'allele': allele,
                        'frequency': freq,
                        'count': freq_data['counts'][allele],
                        'carriers': self._get_allele_carriers(gene_name, allele)
                    })
            
            if rare:
                rare_alleles[gene_name] = sorted(rare, key=lambda x: x['frequency'])
        
        return rare_alleles
    
    def calculate_founder_contribution(self) -> Dict:
        """
        Calculate genetic contribution of founder cats to the population
        
        Returns:
            Dictionary mapping founder IDs to their genetic contribution
        """
        founders = [
            cat for cat in self.registry.get_all_cats()
            if not cat.sire_id and not cat.dam_id
        ]
        
        contributions = {}
        current_generation = self.registry.get_all_cats()
        
        for founder in founders:
            # Count how many cats have this founder in their ancestry
            contribution = self._calculate_ancestor_contribution(founder.id, current_generation)
            contributions[founder.id] = {
                'name': founder.name or f"Cat #{founder.id}",
                'descendants': contribution['descendants'],
                'total_cats': len(current_generation),
                'percentage': (contribution['descendants'] / len(current_generation) * 100) if current_generation else 0
            }
        
        return contributions
    
    def diversity_report(self) -> Dict:
        """
        Generate comprehensive diversity report
        
        Returns:
            Complete diversity analysis
        """
        report = {
            'population_size': self.effective_population_size(),
            'heterozygosity': self.calculate_heterozygosity(),
            'allele_frequencies': self.calculate_allele_frequencies(),
            'rare_alleles': self.identify_rare_alleles(0.05),
            'founder_contributions': self.calculate_founder_contribution()
        }
        
        # Calculate summary metrics
        het_values = [h['observed'] for h in report['heterozygosity'].values()]
        report['summary'] = {
            'mean_heterozygosity': sum(het_values) / len(het_values) if het_values else 0,
            'total_rare_alleles': sum(len(v) for v in report['rare_alleles'].values()),
            'genes_analyzed': len(report['allele_frequencies']),
            'diversity_status': self._assess_diversity_status(report)
        }
        
        return report
    
    def _get_allele_carriers(self, gene_name: str, allele: str) -> List[int]:
        """Get list of cat IDs carrying a specific allele"""
        carriers = []
        for cat in self.registry.get_all_cats():
            if gene_name in cat.genes and allele in cat.genes[gene_name]:
                carriers.append(cat.id)
        return carriers
    
    def _calculate_ancestor_contribution(self, ancestor_id: int, 
                                        population: List) -> Dict:
        """Calculate how many cats have this ancestor"""
        descendants = 0
        
        for cat in population:
            if self._has_ancestor(cat.id, ancestor_id):
                descendants += 1
        
        return {'descendants': descendants}
    
    def _has_ancestor(self, cat_id: int, ancestor_id: int, 
                     depth: int = 0, max_depth: int = 20) -> bool:
        """Check if a cat has a specific ancestor"""
        if depth > max_depth:
            return False
        
        if cat_id == ancestor_id:
            return True
        
        cat = self.registry.get_cat(cat_id)
        if not cat:
            return False
        
        # Check sire line
        if cat.sire_id:
            if cat.sire_id == ancestor_id:
                return True
            if self._has_ancestor(cat.sire_id, ancestor_id, depth + 1, max_depth):
                return True
        
        # Check dam line
        if cat.dam_id:
            if cat.dam_id == ancestor_id:
                return True
            if self._has_ancestor(cat.dam_id, ancestor_id, depth + 1, max_depth):
                return True
        
        return False
    
    def _assess_diversity_status(self, report: Dict) -> str:
        """Assess overall genetic diversity status"""
        mean_het = report['summary']['mean_heterozygosity']
        ne = report['population_size']['effective_size']
        rare_count = report['summary']['total_rare_alleles']
        
        # Simple assessment logic
        if mean_het > 0.5 and ne > 50:
            return "Excellent - High genetic diversity"
        elif mean_het > 0.35 and ne > 30:
            return "Good - Moderate genetic diversity"
        elif mean_het > 0.2 and ne > 15:
            return "Fair - Consider increasing diversity"
        else:
            return "Poor - Low genetic diversity, intervention recommended"


class InbreedingCalculator:
    """
    Calculate inbreeding coefficients and detect inbred cats
    """
    
    def __init__(self, registry):
        self.registry = registry
        self._coefficient_cache = {}
    
    def calculate_coefficient(self, cat_id: int) -> float:
        """
        Calculate Wright's inbreeding coefficient (F) for a cat
        
        Returns:
            Inbreeding coefficient (0 = no inbreeding, 1 = maximum)
        """
        if cat_id in self._coefficient_cache:
            return self._coefficient_cache[cat_id]
        
        cat = self.registry.get_cat(cat_id)
        if not cat or not cat.sire_id or not cat.dam_id:
            return 0.0
        
        # Find common ancestors
        common_ancestors = self._find_common_ancestors(cat.sire_id, cat.dam_id)
        
        if not common_ancestors:
            self._coefficient_cache[cat_id] = 0.0
            return 0.0
        
        f = 0.0
        
        for ancestor_id in common_ancestors:
            # Find all paths from sire to ancestor
            paths_sire = self._find_all_paths(cat.sire_id, ancestor_id)
            # Find all paths from dam to ancestor
            paths_dam = self._find_all_paths(cat.dam_id, ancestor_id)
            
            for path_s in paths_sire:
                for path_d in paths_dam:
                    # n = total generations in path
                    n = len(path_s) + len(path_d)
                    # F_a = inbreeding coefficient of common ancestor
                    f_a = self.calculate_coefficient(ancestor_id)
                    # Add contribution
                    f += (0.5 ** n) * (1 + f_a)
        
        self._coefficient_cache[cat_id] = f
        return f
    
    def find_inbred_cats(self, threshold: float = 0.0625) -> List[Dict]:
        """
        Find cats with inbreeding coefficient above threshold
        
        Args:
            threshold: F threshold (default 0.0625 = 6.25%, equivalent to first cousins)
            
        Returns:
            List of inbred cats with details
        """
        inbred_cats = []
        
        for cat in self.registry.get_all_cats():
            if cat.sire_id and cat.dam_id:  # Only check cats with known parents
                f = self.calculate_coefficient(cat.id)
                if f > threshold:
                    common = self._find_common_ancestors(cat.sire_id, cat.dam_id)
                    inbred_cats.append({
                        'id': cat.id,
                        'name': cat.name or f"Cat #{cat.id}",
                        'coefficient': f,
                        'percentage': f * 100,
                        'common_ancestors': list(common),
                        'relationship': self._describe_relationship(f)
                    })
        
        return sorted(inbred_cats, key=lambda x: x['coefficient'], reverse=True)
    
    def _find_common_ancestors(self, cat1_id: int, cat2_id: int, 
                              depth: int = 10) -> set:
        """Find all common ancestors between two cats"""
        ancestors1 = self._get_all_ancestors(cat1_id, depth)
        ancestors2 = self._get_all_ancestors(cat2_id, depth)
        return ancestors1 & ancestors2
    
    def _get_all_ancestors(self, cat_id: int, depth: int) -> set:
        """Get all ancestors up to specified depth"""
        if depth <= 0:
            return set()
        
        cat = self.registry.get_cat(cat_id)
        if not cat:
            return set()
        
        ancestors = set()
        
        if cat.sire_id:
            ancestors.add(cat.sire_id)
            ancestors.update(self._get_all_ancestors(cat.sire_id, depth - 1))
        
        if cat.dam_id:
            ancestors.add(cat.dam_id)
            ancestors.update(self._get_all_ancestors(cat.dam_id, depth - 1))
        
        return ancestors
    
    def _find_all_paths(self, start_id: int, target_id: int, 
                       current_path: List = None, depth: int = 0) -> List[List[int]]:
        """Find all paths from start to target in pedigree"""
        if current_path is None:
            current_path = []
        
        if depth > 10:  # Prevent infinite recursion
            return []
        
        if start_id == target_id:
            return [current_path]
        
        cat = self.registry.get_cat(start_id)
        if not cat:
            return []
        
        all_paths = []
        
        # Try sire path
        if cat.sire_id and cat.sire_id not in current_path:
            paths = self._find_all_paths(
                cat.sire_id, target_id, 
                current_path + [start_id], 
                depth + 1
            )
            all_paths.extend(paths)
        
        # Try dam path
        if cat.dam_id and cat.dam_id not in current_path:
            paths = self._find_all_paths(
                cat.dam_id, target_id, 
                current_path + [start_id], 
                depth + 1
            )
            all_paths.extend(paths)
        
        return all_paths
    
    def _describe_relationship(self, f: float) -> str:
        """Describe inbreeding level in human terms"""
        if f >= 0.25:
            return "Parent-offspring or sibling mating"
        elif f >= 0.125:
            return "Half-sibling or grandparent-grandchild mating"
        elif f >= 0.0625:
            return "First cousin mating"
        elif f >= 0.03125:
            return "Second cousin mating"
        else:
            return "Distant relationship"
    
    def clear_cache(self):
        """Clear the coefficient cache"""
        self._coefficient_cache.clear()


class PedigreeAnalyzer:
    """
    Analyze pedigree completeness and structure
    """
    
    def __init__(self, registry):
        self.registry = registry
    
    def calculate_pedigree_completeness(self, cat_id: int, 
                                       generations: int = 5) -> Dict:
        """
        Calculate pedigree completeness index
        
        Args:
            cat_id: Cat to analyze
            generations: Number of generations to check
            
        Returns:
            Completeness metrics
        """
        expected_ancestors = sum(2 ** i for i in range(1, generations + 1))
        actual_ancestors = len(self._get_all_ancestors(cat_id, generations))
        
        completeness = actual_ancestors / expected_ancestors if expected_ancestors > 0 else 0
        
        # Calculate generation-wise completeness
        gen_completeness = {}
        for gen in range(1, generations + 1):
            expected = 2 ** gen
            ancestors_at_gen = self._get_ancestors_at_generation(cat_id, gen)
            actual = len(ancestors_at_gen)
            gen_completeness[gen] = {
                'expected': expected,
                'actual': actual,
                'percentage': (actual / expected * 100) if expected > 0 else 0
            }
        
        return {
            'cat_id': cat_id,
            'generations_checked': generations,
            'expected_ancestors': expected_ancestors,
            'known_ancestors': actual_ancestors,
            'completeness_index': completeness,
            'completeness_percentage': completeness * 100,
            'by_generation': gen_completeness
        }
    
    def find_pedigree_loops(self, cat_id: int) -> List[List[int]]:
        """
        Find loops in pedigree (same ancestor appearing multiple times)
        
        Returns:
            List of loops (paths that circle back)
        """
        loops = []
        ancestors = self._get_all_ancestors(cat_id, 10)
        
        for ancestor_id in ancestors:
            # Count how many times this ancestor appears
            paths_to_ancestor = self._count_paths_to_ancestor(cat_id, ancestor_id)
            if paths_to_ancestor > 1:
                loops.append({
                    'ancestor_id': ancestor_id,
                    'ancestor_name': self.registry.get_cat(ancestor_id).name if self.registry.get_cat(ancestor_id) else "Unknown",
                    'occurrences': paths_to_ancestor
                })
        
        return loops
    
    def _get_all_ancestors(self, cat_id: int, depth: int) -> set:
        """Get all ancestors up to depth"""
        if depth <= 0:
            return set()
        
        cat = self.registry.get_cat(cat_id)
        if not cat:
            return set()
        
        ancestors = set()
        if cat.sire_id:
            ancestors.add(cat.sire_id)
            ancestors.update(self._get_all_ancestors(cat.sire_id, depth - 1))
        if cat.dam_id:
            ancestors.add(cat.dam_id)
            ancestors.update(self._get_all_ancestors(cat.dam_id, depth - 1))
        
        return ancestors
    
    def _get_ancestors_at_generation(self, cat_id: int, generation: int) -> set:
        """Get ancestors at specific generation"""
        if generation == 0:
            return {cat_id}
        if generation == 1:
            cat = self.registry.get_cat(cat_id)
            if not cat:
                return set()
            ancestors = set()
            if cat.sire_id:
                ancestors.add(cat.sire_id)
            if cat.dam_id:
                ancestors.add(cat.dam_id)
            return ancestors
        
        cat = self.registry.get_cat(cat_id)
        if not cat:
            return set()
        
        ancestors = set()
        if cat.sire_id:
            ancestors.update(self._get_ancestors_at_generation(cat.sire_id, generation - 1))
        if cat.dam_id:
            ancestors.update(self._get_ancestors_at_generation(cat.dam_id, generation - 1))
        
        return ancestors
    
    def _count_paths_to_ancestor(self, cat_id: int, ancestor_id: int, 
                                 depth: int = 0) -> int:
        """Count number of paths from cat to ancestor"""
        if depth > 10:
            return 0
        
        if cat_id == ancestor_id:
            return 1
        
        cat = self.registry.get_cat(cat_id)
        if not cat:
            return 0
        
        count = 0
        if cat.sire_id:
            count += self._count_paths_to_ancestor(cat.sire_id, ancestor_id, depth + 1)
        if cat.dam_id:
            count += self._count_paths_to_ancestor(cat.dam_id, ancestor_id, depth + 1)
        
        return count