"""
Phenotype calculation logic - determines visible traits from genetics
"""

import random
from typing import Dict, List, Tuple


class PhenotypeCalculator:
    """Calculates phenotype from genotype"""
    
    def __init__(self, genetics_engine):
        self.genetics = genetics_engine
    
    def calculate_phenotype(self, cat) -> str:
        """Calculate complete phenotype description"""
        # Check for dominant white first
        if 'Wd' in cat.genes.get('white', []):
            fur = self.genetics.get_dominant_allele('fur_length', 
                                                    cat.genes.get('fur_length', ['L']))
            fur_desc = 'Longhair' if fur == 'l' else 'Shorthair'
            return f"{fur_desc} White"
        
        # Check for albino
        cr_alleles = cat.genes.get('color_restriction', [])
        if len(cr_alleles) == 2 and cr_alleles[0] == 'c' and cr_alleles[1] == 'c':
            fur = self.genetics.get_dominant_allele('fur_length', 
                                                    cat.genes.get('fur_length', ['L']))
            fur_desc = 'Longhair' if fur == 'l' else 'Shorthair'
            return f"{fur_desc} Albino"
        
        parts = []
        
        # Fur length
        fur = self.genetics.get_dominant_allele('fur_length', 
                                                cat.genes.get('fur_length', ['L']))
        parts.append('Longhair' if fur == 'l' else 'Shorthair')
        
        # Determine red expression
        red_expression = self._get_red_expression(cat)
        
        # Build color and pattern
        color_pattern = self._build_color_pattern(cat, red_expression)
        parts.append(color_pattern)
        
        return ' '.join(parts)
    
    def _get_red_expression(self, cat) -> str:
        """Determine red/orange expression"""
        red_alleles = cat.genes.get('red', ['o'])
        
        if cat.sex == 'male':
            return 'red' if red_alleles[0] == 'O' else 'non-red'
        else:
            if 'O' in red_alleles and 'o' in red_alleles:
                return 'tortie'
            elif red_alleles[0] == 'O' and red_alleles[1] == 'O':
                return 'red'
            else:
                return 'non-red'
    
    def _build_color_pattern(self, cat, red_expression: str) -> str:
        """Build complete color and pattern description"""
        parts = []
        
        # Base eumelanin color
        base = self.genetics.get_dominant_allele('base_color', 
                                                 cat.genes.get('base_color', ['B']))
        base_color_map = {'B': 'Black', 'b': 'Chocolate', 'bl': 'Cinnamon'}
        eumelanin = base_color_map.get(base, 'Black')
        
        # Apply dilution
        dilute = self.genetics.get_dominant_allele('dilution', 
                                                   cat.genes.get('dilution', ['D']))
        if dilute == 'd':
            eumelanin_map = {'Black': 'Blue', 'Chocolate': 'Lilac', 'Cinnamon': 'Fawn'}
            eumelanin = eumelanin_map.get(eumelanin, eumelanin)
            phaeomelanin = 'Cream'
        else:
            phaeomelanin = 'Red'
        
        # Silver/golden modifiers
        has_silver = 'I' in cat.genes.get('inhibitor', [])
        wb_level = self._get_wideband_level(cat)
        has_wideband = (wb_level >= 1) and not has_silver
        
        # Determine solid vs tabby
        agouti_alleles = cat.genes.get('agouti', ['A', 'A'])
        is_solid = (agouti_alleles[0] == 'a' and agouti_alleles[1] == 'a')
        
        # Build pattern
        if red_expression == 'red':
            pattern = self._get_tabby_pattern(cat, is_red=True)
            if has_silver:
                parts.append(f"Silver {phaeomelanin} {pattern} Tabby")
            elif has_wideband:
                parts.append(f"Golden {phaeomelanin} {pattern} Tabby")
            else:
                parts.append(f"{phaeomelanin} {pattern} Tabby")
        
        elif red_expression == 'tortie':
            is_solid_tortie = (agouti_alleles[0] == 'a' and agouti_alleles[1] == 'a')
            
            if is_solid_tortie:
                if has_silver:
                    parts.append(f"{eumelanin} Smoke Tortoiseshell")
                else:
                    parts.append(f"{eumelanin} Tortoiseshell")
            else:
                pattern = self._get_tabby_pattern(cat, is_red=False)
                display_color = self._apply_breed_naming(eumelanin, pattern)
                
                if has_silver:
                    parts.append(f"Silver {display_color} {pattern} Torbie")
                elif has_wideband:
                    parts.append(f"Golden {display_color} {pattern} Torbie")
                else:
                    parts.append(f"{display_color} {pattern} Torbie")
        
        else:  # non-red
            if is_solid:
                if has_silver:
                    parts.append(f"{eumelanin} Smoke")
                else:
                    parts.append(eumelanin)
            else:
                pattern = self._get_tabby_pattern(cat, is_red=False)
                display_color = self._apply_breed_naming(eumelanin, pattern)
                
                if has_silver:
                    parts.append(f"Silver {display_color} {pattern} Tabby")
                elif has_wideband:
                    parts.append(f"Golden {display_color} {pattern} Tabby")
                else:
                    parts.append(f"{display_color} {pattern} Tabby")
        
        # Karpati modifier
        if 'K' in cat.genes.get('karpati', []):
            parts.append('with Karpati')
        
        # Color restriction
        cr_alleles = cat.genes.get('color_restriction', ['C', 'C'])
        if 'cb' in cr_alleles and 'cs' in cr_alleles:
            parts.append('Mink')
        else:
            restriction = self.genetics.get_dominant_allele('color_restriction', cr_alleles)
            if restriction == 'cs':
                if 'Black' in parts[0]:
                    parts[0] = parts[0].replace('Black', 'Seal')
                parts.append('Point')
            elif restriction == 'cb':
                parts.append('Sepia')
        
        # White spotting
        white_desc = self.get_white_description(cat)
        if white_desc and white_desc != "White":
            parts.append(white_desc)
        
        return ' '.join(parts)
    
    def _get_tabby_pattern(self, cat, is_red: bool = False) -> str:
        """Determine tabby pattern"""
        agouti = self.genetics.get_dominant_allele('agouti', 
                                                   cat.genes.get('agouti', ['A']))
        has_bengal = 'Bm' in cat.genes.get('bengal', [])
        
        # Charcoal variants (only for non-red)
        if agouti == 'Apb' and not is_red:
            ticked = self.genetics.get_dominant_allele('ticked', 
                                                      cat.genes.get('ticked', ['ta']))
            if ticked == 'Ta':
                return 'Midnight Charcoal'
            else:
                return 'Twilight Charcoal'
        
        # Ticked overrides all
        ticked = self.genetics.get_dominant_allele('ticked', 
                                                   cat.genes.get('ticked', ['ta']))
        if ticked == 'Ta':
            return 'Ticked'
        
        # Base pattern
        tabby = self.genetics.get_dominant_allele('tabby', 
                                                  cat.genes.get('tabby', ['Mc']))
        spotted = self.genetics.get_dominant_allele('spotted', 
                                                    cat.genes.get('spotted', ['sp']))
        
        if tabby == 'mc':  # Classic base
            if spotted == 'Sp':
                return 'Rosetted' if has_bengal else 'Spotted'
            else:
                return 'Marbled' if has_bengal else 'Classic'
        else:  # Mackerel base
            if spotted == 'Sp':
                return 'Broken Braided' if has_bengal else 'Broken Mackerel'
            else:
                return 'Braided' if has_bengal else 'Mackerel'
    
    def _apply_breed_naming(self, color: str, pattern: str) -> str:
        """Apply breed-specific color naming"""
        if pattern == 'Ticked':
            if color == 'Black':
                return 'Ruddy'
            elif color == 'Cinnamon':
                return 'Sorrel'
        return color
    
    def _get_wideband_level(self, cat) -> int:
        """Calculate wide band expression level"""
        wb_alleles = cat.genes.get('wide_band', ['wb', 'wb'])
        return sum(1 for a in wb_alleles if a == 'Wb')
    
    def get_white_percentage(self, cat) -> int:
        """Calculate white percentage"""
        if cat._white_percentage is not None:
            return cat._white_percentage
        
        white_alleles = cat.genes.get('white', [])
        
        if 'Wd' in white_alleles:
            cat._white_percentage = 100
            return 100
        
        ws_count = sum(1 for a in white_alleles if a == 'Ws')
        
        if ws_count == 0:
            cat._white_percentage = 0
        elif ws_count == 1:
            cat._white_percentage = random.choices(
                range(1, 51),
                weights=[3] * 15 + [2] * 15 + [1] * 20
            )[0]
        else:
            cat._white_percentage = random.choices(
                range(50, 100),
                weights=[1] * 15 + [2] * 15 + [3] * 20
            )[0]
        
        return cat._white_percentage
    
    def get_white_description(self, cat) -> str:
        """Get descriptive white marking level"""
        pct = self.get_white_percentage(cat)
        
        if pct == 0:
            return None
        elif pct == 100:
            return "White"
        elif pct < 35:
            return "with Low White"
        elif pct < 65:
            return "Bicolor"
        else:
            return "with High White"
    
    def calculate_eye_color(self, cat) -> str:
        """Calculate eye color based on genetics"""
        # Dominant white
        if 'Wd' in cat.genes.get('white', []):
            chance = random.random()
            if chance < 0.50:
                return 'Blue'
            elif chance < 0.70:
                return 'Odd-Eyed (One Blue, One Copper)'
            elif chance < 0.85:
                return 'Copper'
            else:
                return 'Green'
        
        # High white
        white_alleles = cat.genes.get('white', [])
        ws_count = sum(1 for a in white_alleles if a == 'Ws')
        if ws_count == 2:
            if random.random() < 0.35:
                return random.choice([
                    'Blue', 
                    'Odd-Eyed (One Blue, One Green)', 
                    'Odd-Eyed (One Blue, One Copper)'
                ])
        
        # Albino
        cr_alleles = cat.genes.get('color_restriction', ['C', 'C'])
        if cr_alleles[0] == 'c' and cr_alleles[1] == 'c':
            chance = random.random()
            if chance < 0.70:
                return 'Pale Blue'
            elif chance < 0.90:
                return 'Lilac-Blue'
            else:
                return 'Pink'
        
        # Colorpoint
        if 'cs' in cr_alleles:
            if 'cb' in cr_alleles:
                return self._calculate_mink_eye_color(cat)
            else:
                return self._calculate_colorpoint_eye_color(cat)
        
        # Sepia
        if cr_alleles[0] == 'cb' and cr_alleles[1] == 'cb':
            return self._calculate_sepia_eye_color(cat)
        
        return self._calculate_polygenic_eye_color(cat)
    
    def _get_eye_pigment_score(self, cat) -> float:
        """Calculate melanin pigment score"""
        score = 0.0
        for gene_name in ['eye_pigment_1', 'eye_pigment_2', 'eye_pigment_3']:
            alleles = cat.genes.get(gene_name, [])
            gene_data = self.genetics.get_gene_info(gene_name)
            if gene_data:
                contrib = gene_data.get('pigment_contribution', {})
                score += sum(contrib.get(a, 0.0) for a in alleles)
        return score
    
    def _get_lipochrome_score(self, cat) -> float:
        """Calculate lipochrome score"""
        alleles = cat.genes.get('lipochrome', ['lp', 'lp'])
        gene_data = self.genetics.get_gene_info('lipochrome')
        if gene_data:
            contrib = gene_data.get('pigment_contribution', {})
            return sum(contrib.get(a, 0.0) for a in alleles)
        return 0.0
    
    def _calculate_colorpoint_eye_color(self, cat) -> str:
        """Colorpoint eye colors"""
        pigment_score = self._get_eye_pigment_score(cat)
        if pigment_score < 1.0:
            return 'Pale Blue'
        elif pigment_score < 2.0:
            return 'Blue'
        elif pigment_score < 3.0:
            return 'Deep Blue'
        else:
            return 'Sapphire Blue'
    
    def _calculate_mink_eye_color(self, cat) -> str:
        """Mink eye colors"""
        pigment_score = self._get_eye_pigment_score(cat)
        if pigment_score < 1.5:
            return 'Pale Aqua'
        elif pigment_score < 2.5:
            return 'Aqua'
        elif pigment_score < 3.5:
            return 'Blue-Green'
        else:
            return 'Deep Aqua'
    
    def _calculate_sepia_eye_color(self, cat) -> str:
        """Sepia eye colors"""
        pigment_score = self._get_eye_pigment_score(cat)
        lipochrome_score = self._get_lipochrome_score(cat)
        
        if lipochrome_score >= 1.5:
            if pigment_score < 2.0:
                return 'Golden'
            elif pigment_score < 3.5:
                return 'Deep Golden'
            else:
                return 'Copper'
        elif pigment_score < 1.5:
            return random.choice(['Greenish-Blue', 'Pale Yellow-Green'])
        elif pigment_score < 2.5:
            return random.choice(['Yellow-Green', 'Golden-Green'])
        elif pigment_score < 3.5:
            return random.choice(['Yellow', 'Golden'])
        else:
            return random.choice(['Orange', 'Deep Orange'])
    
    def _calculate_polygenic_eye_color(self, cat) -> str:
        """Normal cat eye colors"""
        pigment_score = self._get_eye_pigment_score(cat)
        lipochrome_score = self._get_lipochrome_score(cat)
        
        if lipochrome_score >= 1.5:
            if pigment_score < 2.0:
                return 'Gold'
            elif pigment_score < 3.5:
                return 'Copper'
            else:
                return 'Deep Copper'
        
        if pigment_score < 0.8:
            return random.choice(['Blue', 'Blue-Grey', 'Grey-Blue'])
        elif pigment_score < 1.8:
            return random.choice(['Yellow-Green', 'Gooseberry Green', 'Green', 'Pale Green'])
        elif pigment_score < 2.8:
            colors = ['Yellow', 'Lemon Yellow', 'Hazel', 'Green-Hazel', 'Green']
            if random.random() < 0.15:
                return random.choice([
                    'Dichroic (Green with Yellow Ring)',
                    'Dichroic (Hazel with Green Flecks)',
                    'Sectoral Heterochromia (Green and Yellow)'
                ])
            return random.choice(colors)
        elif pigment_score < 3.8:
            return random.choice(['Amber', 'Light Brown', 'Hazel-Brown', 'Brown'])
        else:
            return random.choice(['Dark Brown', 'Deep Brown'])