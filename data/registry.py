"""
Cat registry management - stores and manages all cats
"""

from typing import Dict, List, Optional
from core.cat import Cat


class CatRegistry:
    """Manages collection of cats in the registry"""
    
    def __init__(self):
        self.cats: Dict[int, Cat] = {}
        self.next_id = 1
        self.current_file: Optional[str] = None
    
    def add_cat(self, cat: Cat) -> int:
        """Add a cat to the registry and assign ID"""
        if cat.id is None:
            cat.id = self.next_id
            self.next_id += 1
        else:
            self.next_id = max(self.next_id, cat.id + 1)
        
        self.cats[cat.id] = cat
        return cat.id
    
    def remove_cat(self, cat_id: int) -> bool:
        """Remove a cat from the registry"""
        if cat_id in self.cats:
            del self.cats[cat_id]
            return True
        return False
    
    def get_cat(self, cat_id: int) -> Optional[Cat]:
        """Get a cat by ID"""
        return self.cats.get(cat_id)
    
    def get_all_cats(self) -> List[Cat]:
        """Get all cats as a list"""
        return list(self.cats.values())
    
    def get_males(self) -> List[Cat]:
        """Get all male cats"""
        return [cat for cat in self.cats.values() if cat.sex == 'male']
    
    def get_females(self) -> List[Cat]:
        """Get all female cats"""
        return [cat for cat in self.cats.values() if cat.sex == 'female']
    
    def get_offspring(self, parent_id: int) -> List[Cat]:
        """Get all offspring of a cat"""
        return [cat for cat in self.cats.values() 
                if cat.sire_id == parent_id or cat.dam_id == parent_id]
    
    def get_parents(self, cat_id: int) -> tuple:
        """Get both parents of a cat (sire, dam)"""
        cat = self.get_cat(cat_id)
        if not cat:
            return None, None
        
        sire = self.get_cat(cat.sire_id) if cat.sire_id else None
        dam = self.get_cat(cat.dam_id) if cat.dam_id else None
        return sire, dam
    
    def clear(self):
        """Clear all cats from registry"""
        self.cats.clear()
        self.next_id = 1
        self.current_file = None
    
    def to_data(self) -> List[Dict]:
        """Convert registry to JSON-serializable format"""
        return [cat.to_dict() for cat in self.cats.values()]
    
    def load_from_data(self, data: List[Dict]):
        """Load registry from JSON data"""
        self.clear()
        
        for cat_data in data:
            cat = Cat.from_dict(cat_data)
            self.cats[cat.id] = cat
            self.next_id = max(self.next_id, cat.id + 1)
    
    def search_cats(self, query: str) -> List[Cat]:
        """Search cats by ID, name, or phenotype"""
        query = query.lower()
        results = []
        
        for cat in self.cats.values():
            searchable = f"{cat.id} {cat.name}".lower()
            if query in searchable:
                results.append(cat)
        
        return results
    
    def __len__(self) -> int:
        return len(self.cats)
    
    def __contains__(self, cat_id: int) -> bool:
        return cat_id in self.cats