"""
Comprehensive validation framework for CatGen
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger('catgen.validation')


class Severity(Enum):
    """Validation message severity levels"""
    ERROR = "error"      # Must be fixed
    WARNING = "warning"  # Should be reviewed
    INFO = "info"        # Informational only


@dataclass
class ValidationResult:
    """Result of a validation check"""
    field: str
    message: str
    severity: Severity
    code: str
    context: Optional[Dict[str, Any]] = None
    
    def __repr__(self):
        return f"{self.severity.value.upper()}: {self.field} - {self.message}"
    
    def to_dict(self) -> Dict:
        return {
            'field': self.field,
            'message': self.message,
            'severity': self.severity.value,
            'code': self.code,
            'context': self.context
        }


class ValidationReport:
    """Collection of validation results"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def add(self, field: str, message: str, severity: Severity, 
            code: str, context: Optional[Dict] = None):
        """Add a validation result"""
        self.results.append(ValidationResult(field, message, severity, code, context))
    
    def add_error(self, field: str, message: str, code: str, context: Optional[Dict] = None):
        """Add an error"""
        self.add(field, message, Severity.ERROR, code, context)
    
    def add_warning(self, field: str, message: str, code: str, context: Optional[Dict] = None):
        """Add a warning"""
        self.add(field, message, Severity.WARNING, code, context)
    
    def add_info(self, field: str, message: str, code: str, context: Optional[Dict] = None):
        """Add info"""
        self.add(field, message, Severity.INFO, code, context)
    
    def has_errors(self) -> bool:
        """Check if report contains any errors"""
        return any(r.severity == Severity.ERROR for r in self.results)
    
    def has_warnings(self) -> bool:
        """Check if report contains any warnings"""
        return any(r.severity == Severity.WARNING for r in self.results)
    
    def get_errors(self) -> List[ValidationResult]:
        """Get all errors"""
        return [r for r in self.results if r.severity == Severity.ERROR]
    
    def get_warnings(self) -> List[ValidationResult]:
        """Get all warnings"""
        return [r for r in self.results if r.severity == Severity.WARNING]
    
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)"""
        return not self.has_errors()
    
    def summary(self) -> str:
        """Get summary string"""
        errors = len(self.get_errors())
        warnings = len(self.get_warnings())
        return f"Validation: {errors} error(s), {warnings} warning(s)"
    
    def __str__(self):
        lines = [self.summary()]
        for result in self.results:
            lines.append(f"  {result}")
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            'valid': self.is_valid(),
            'error_count': len(self.get_errors()),
            'warning_count': len(self.get_warnings()),
            'results': [r.to_dict() for r in self.results]
        }


class CatValidator:
    """Validate cat data"""
    
    def __init__(self, genetics_engine, registry=None):
        self.genetics = genetics_engine
        self.registry = registry
    
    def validate(self, cat) -> ValidationReport:
        """
        Perform complete validation of a cat
        
        Args:
            cat: Cat object to validate
            
        Returns:
            ValidationReport with all issues found
        """
        report = ValidationReport()
        
        # Basic attribute validation
        self._validate_basic_attributes(cat, report)
        
        # Genetic validation
        self._validate_genetics(cat, report)
        
        # Parent validation
        if self.registry:
            self._validate_parents(cat, report)
        
        # Physical trait validation
        self._validate_physical_traits(cat, report)
        
        logger.debug(f"Validated cat #{cat.id if cat.id else 'new'}: {report.summary()}")
        
        return report
    
    def _validate_basic_attributes(self, cat, report: ValidationReport):
        """Validate basic cat attributes"""
        # Sex validation
        if cat.sex not in ['male', 'female']:
            report.add_error(
                'sex',
                f"Invalid sex: '{cat.sex}'. Must be 'male' or 'female'",
                'INVALID_SEX'
            )
        
        # Name validation
        if cat.name and len(cat.name) > 100:
            report.add_warning(
                'name',
                f"Name is very long ({len(cat.name)} characters)",
                'LONG_NAME'
            )
        
        # Birth date validation
        if cat.birth_date:
            from datetime import datetime
            try:
                datetime.strptime(cat.birth_date, '%Y-%m-%d')
            except ValueError:
                report.add_error(
                    'birth_date',
                    f"Invalid date format: '{cat.birth_date}'. Expected YYYY-MM-DD",
                    'INVALID_DATE'
                )
    
    def _validate_genetics(self, cat, report: ValidationReport):
        """Validate genetic data"""
        if not cat.genes:
            report.add_error(
                'genes',
                "Cat has no genetic data",
                'NO_GENES'
            )
            return
        
        # Validate each gene
        for gene_name, alleles in cat.genes.items():
            gene_info = self.genetics.get_gene_info(gene_name)
            
            # Check if gene exists
            if not gene_info:
                report.add_error(
                    gene_name,
                    f"Unknown gene: '{gene_name}'",
                    'UNKNOWN_GENE',
                    {'gene': gene_name}
                )
                continue
            
            # Check allele count
            is_x_linked = gene_info.get('x_linked', False)
            expected_count = 1 if (is_x_linked and cat.sex == 'male') else 2
            
            if len(alleles) != expected_count:
                report.add_error(
                    gene_name,
                    f"Gene '{gene_name}' should have {expected_count} allele(s) "
                    f"for {cat.sex}, but has {len(alleles)}",
                    'WRONG_ALLELE_COUNT',
                    {'expected': expected_count, 'actual': len(alleles)}
                )
                continue
            
            # Validate each allele
            valid_alleles = gene_info['alleles']
            for i, allele in enumerate(alleles):
                if allele not in valid_alleles:
                    report.add_error(
                        gene_name,
                        f"Invalid allele '{allele}' for gene '{gene_name}'. "
                        f"Valid alleles: {', '.join(valid_alleles)}",
                        'INVALID_ALLELE',
                        {'allele': allele, 'valid': valid_alleles}
                    )
        
        # Check for missing genes
        all_gene_names = set(self.genetics.get_all_gene_names())
        cat_gene_names = set(cat.genes.keys())
        missing_genes = all_gene_names - cat_gene_names
        
        if missing_genes:
            report.add_warning(
                'genes',
                f"Cat is missing {len(missing_genes)} gene(s): {', '.join(list(missing_genes)[:5])}",
                'MISSING_GENES',
                {'missing': list(missing_genes)}
            )
    
    def _validate_parents(self, cat, report: ValidationReport):
        """Validate parent relationships"""
        # Check if parents exist in registry
        if cat.sire_id:
            sire = self.registry.get_cat(cat.sire_id)
            if not sire:
                report.add_error(
                    'sire_id',
                    f"Sire #{cat.sire_id} not found in registry",
                    'PARENT_NOT_FOUND',
                    {'parent_id': cat.sire_id, 'parent_type': 'sire'}
                )
            else:
                # Validate sire is male
                if sire.sex != 'male':
                    report.add_error(
                        'sire_id',
                        f"Sire #{cat.sire_id} is not male (sex: {sire.sex})",
                        'WRONG_PARENT_SEX',
                        {'parent_id': cat.sire_id, 'expected': 'male', 'actual': sire.sex}
                    )
                
                # Check for temporal impossibility
                if cat.birth_date and sire.birth_date:
                    if cat.birth_date <= sire.birth_date:
                        report.add_error(
                            'birth_date',
                            f"Cat birth date ({cat.birth_date}) is before or same as sire's ({sire.birth_date})",
                            'IMPOSSIBLE_BIRTH_DATE'
                        )
        
        if cat.dam_id:
            dam = self.registry.get_cat(cat.dam_id)
            if not dam:
                report.add_error(
                    'dam_id',
                    f"Dam #{cat.dam_id} not found in registry",
                    'PARENT_NOT_FOUND',
                    {'parent_id': cat.dam_id, 'parent_type': 'dam'}
                )
            else:
                # Validate dam is female
                if dam.sex != 'female':
                    report.add_error(
                        'dam_id',
                        f"Dam #{cat.dam_id} is not female (sex: {dam.sex})",
                        'WRONG_PARENT_SEX',
                        {'parent_id': cat.dam_id, 'expected': 'female', 'actual': dam.sex}
                    )
                
                # Check for temporal impossibility
                if cat.birth_date and dam.birth_date:
                    if cat.birth_date <= dam.birth_date:
                        report.add_error(
                            'birth_date',
                            f"Cat birth date ({cat.birth_date}) is before or same as dam's ({dam.birth_date})",
                            'IMPOSSIBLE_BIRTH_DATE'
                        )
        
        # Check for self-referential parents
        if cat.id:
            if cat.sire_id == cat.id:
                report.add_error(
                    'sire_id',
                    "Cat cannot be its own sire",
                    'SELF_PARENT'
                )
            if cat.dam_id == cat.id:
                report.add_error(
                    'dam_id',
                    "Cat cannot be its own dam",
                    'SELF_PARENT'
                )
        
        # Check if parents are the same cat
        if cat.sire_id and cat.dam_id and cat.sire_id == cat.dam_id:
            report.add_error(
                'parents',
                "Sire and dam cannot be the same cat",
                'SAME_PARENTS'
            )
    
    def _validate_physical_traits(self, cat, report: ValidationReport):
        """Validate physical trait values"""
        # Build value
        if not (0 <= cat.build_value <= 100):
            report.add_error(
                'build_value',
                f"Build value must be between 0 and 100, got {cat.build_value}",
                'INVALID_BUILD_VALUE'
            )
        
        # Size value
        if not (0 <= cat.size_value <= 100):
            report.add_error(
                'size_value',
                f"Size value must be between 0 and 100, got {cat.size_value}",
                'INVALID_SIZE_VALUE'
            )
        
        # White percentage
        if cat._white_percentage is not None:
            if not (0 <= cat._white_percentage <= 100):
                report.add_error(
                    'white_percentage',
                    f"White percentage must be between 0 and 100, got {cat._white_percentage}",
                    'INVALID_WHITE_PERCENTAGE'
                )


class BreedingValidator:
    """Validate breeding operations"""
    
    def __init__(self, registry, breeding_engine):
        self.registry = registry
        self.breeding = breeding_engine
    
    def validate_breeding_pair(self, sire_id: int, dam_id: int) -> ValidationReport:
        """
        Validate a potential breeding pair
        
        Args:
            sire_id: Sire's ID
            dam_id: Dam's ID
            
        Returns:
            ValidationReport
        """
        report = ValidationReport()
        
        # Get cats
        sire = self.registry.get_cat(sire_id)
        dam = self.registry.get_cat(dam_id)
        
        if not sire:
            report.add_error(
                'sire_id',
                f"Sire #{sire_id} not found",
                'CAT_NOT_FOUND'
            )
            return report
        
        if not dam:
            report.add_error(
                'dam_id',
                f"Dam #{dam_id} not found",
                'CAT_NOT_FOUND'
            )
            return report
        
        # Validate sexes
        if sire.sex != 'male':
            report.add_error(
                'sire_id',
                f"Sire must be male (currently: {sire.sex})",
                'WRONG_SEX'
            )
        
        if dam.sex != 'female':
            report.add_error(
                'dam_id',
                f"Dam must be female (currently: {dam.sex})",
                'WRONG_SEX'
            )
        
        # Check for same cat
        if sire_id == dam_id:
            report.add_error(
                'breeding',
                "Cannot breed a cat with itself",
                'SAME_CAT'
            )
            return report
        
        # Check for inbreeding
        if self.breeding.check_relatedness(sire_id, dam_id, self.registry.cats, 3):
            report.add_warning(
                'breeding',
                "Cats are related within 3 generations (inbreeding)",
                'INBREEDING_DETECTED',
                {'generations': 3}
            )
        
        # Check for close inbreeding
        if self.breeding.check_relatedness(sire_id, dam_id, self.registry.cats, 1):
            report.add_error(
                'breeding',
                "Cats are parent-offspring or siblings (close inbreeding)",
                'CLOSE_INBREEDING'
            )
        
        return report


class RegistryValidator:
    """Validate entire registry integrity"""
    
    def __init__(self, registry, genetics_engine):
        self.registry = registry
        self.genetics = genetics_engine
        self.cat_validator = CatValidator(genetics_engine, registry)
    
    def validate_registry(self) -> ValidationReport:
        """
        Validate entire registry for consistency
        
        Returns:
            ValidationReport with all issues found
        """
        report = ValidationReport()
        
        # Validate each cat
        for cat in self.registry.get_all_cats():
            cat_report = self.cat_validator.validate(cat)
            for result in cat_report.results:
                # Prepend cat ID to field
                result.field = f"Cat #{cat.id}: {result.field}"
                report.results.append(result)
        
        # Check for orphaned parent references
        self._check_orphaned_references(report)
        
        # Check for circular pedigrees
        self._check_circular_pedigrees(report)
        
        # Check for ID conflicts
        self._check_id_conflicts(report)
        
        return report
    
    def _check_orphaned_references(self, report: ValidationReport):
        """Check for parent IDs that don't exist"""
        all_ids = set(cat.id for cat in self.registry.get_all_cats())
        
        for cat in self.registry.get_all_cats():
            if cat.sire_id and cat.sire_id not in all_ids:
                report.add_warning(
                    f"Cat #{cat.id}",
                    f"References non-existent sire #{cat.sire_id}",
                    'ORPHANED_PARENT_REF'
                )
            
            if cat.dam_id and cat.dam_id not in all_ids:
                report.add_warning(
                    f"Cat #{cat.id}",
                    f"References non-existent dam #{cat.dam_id}",
                    'ORPHANED_PARENT_REF'
                )
    
    def _check_circular_pedigrees(self, report: ValidationReport):
        """Check for impossible circular pedigrees"""
        for cat in self.registry.get_all_cats():
            if self._is_own_ancestor(cat.id, cat.id, depth=0):
                report.add_error(
                    f"Cat #{cat.id}",
                    "Cat is its own ancestor (circular pedigree)",
                    'CIRCULAR_PEDIGREE'
                )
    
    def _is_own_ancestor(self, cat_id: int, ancestor_id: int, depth: int) -> bool:
        """Check if a cat is its own ancestor"""
        if depth > 20:  # Prevent infinite recursion
            return False
        
        cat = self.registry.get_cat(cat_id)
        if not cat:
            return False
        
        if cat.sire_id == ancestor_id or cat.dam_id == ancestor_id:
            if depth > 0:  # Don't count immediate parent check
                return True
        
        if cat.sire_id and self._is_own_ancestor(cat.sire_id, ancestor_id, depth + 1):
            return True
        if cat.dam_id and self._is_own_ancestor(cat.dam_id, ancestor_id, depth + 1):
            return True
        
        return False
    
    def _check_id_conflicts(self, report: ValidationReport):
        """Check for duplicate IDs"""
        id_counts = {}
        for cat in self.registry.get_all_cats():
            if cat.id in id_counts:
                id_counts[cat.id] += 1
            else:
                id_counts[cat.id] = 1
        
        for cat_id, count in id_counts.items():
            if count > 1:
                report.add_error(
                    'registry',
                    f"Duplicate ID: #{cat_id} appears {count} times",
                    'DUPLICATE_ID',
                    {'id': cat_id, 'count': count}
                )