"""
Main application class - coordinates all CatGen systems
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

# Core imports
from core.genetics_engine import GeneticsEngine
from core.phenotype_calculator import PhenotypeCalculator
from core.breeding import BreedingEngine
from data.registry import CatRegistry

# New system imports
from core.events import EventBus, EventType, get_event_bus
from core.services.cat_service import CatService
from core.services.breeding_service import BreedingService
from core.analytics.diversity_analyzer import DiversityAnalyzer, InbreedingCalculator, PedigreeAnalyzer
from core.validation.validator import CatValidator, BreedingValidator, RegistryValidator
from data.database import DatabaseManager
from config.settings import AppConfig, get_config
from utils.logging_config import setup_logging

logger = logging.getLogger('catgen.application')


class CatGenApplication:
    """
    Main application class that coordinates all CatGen subsystems
    
    This is the central point of integration for all new improvements:
    - Event system for decoupled communication
    - Service layer for business logic
    - Database for persistent storage
    - Analytics for genetic analysis
    - Validation for data integrity
    - Configuration management
    """
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize the application
        
        Args:
            config: Application configuration (uses default if None)
        """
        # Configuration
        self.config = config or get_config()
        
        # Setup logging
        self._setup_logging()
        
        logger.info(f"Initializing {self.config.app_name} v{self.config.version}")
        
        # Create necessary directories
        self.config.create_directories()
        
        # Core systems
        self.event_bus = get_event_bus()
        self.genetics_engine = GeneticsEngine(
            genes_path=str(self.config.genes_file)
        )
        self.phenotype_calculator = PhenotypeCalculator(self.genetics_engine)
        self.breeding_engine = BreedingEngine(self.genetics_engine)
        
        # Data layer
        self.registry = CatRegistry()
        self.database: Optional[DatabaseManager] = None
        
        # Initialize database if configured
        if self.config.database.path:
            try:
                self.database = DatabaseManager(str(self.config.database.path))
                logger.info(f"Database initialized: {self.config.database.path}")
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                self.database = None
        
        # Services
        self.cat_service = CatService(
            self.registry,
            self.genetics_engine,
            self.phenotype_calculator,
            self.event_bus
        )
        
        self.breeding_service = BreedingService(
            self.registry,
            self.genetics_engine,
            self.breeding_engine,
            self.phenotype_calculator,
            self.event_bus
        )
        
        # Analytics
        self.diversity_analyzer = DiversityAnalyzer(
            self.registry,
            self.genetics_engine
        )
        
        self.inbreeding_calculator = InbreedingCalculator(self.registry)
        self.pedigree_analyzer = PedigreeAnalyzer(self.registry)
        
        # Validators
        self.cat_validator = CatValidator(self.genetics_engine, self.registry)
        self.breeding_validator = BreedingValidator(self.registry, self.breeding_engine)
        self.registry_validator = RegistryValidator(self.registry, self.genetics_engine)
        
        # Setup event subscriptions
        self._setup_event_handlers()
        
        # Application state
        self.current_file: Optional[Path] = None
        self.is_modified = False
        self.last_save_time: Optional[datetime] = None
        
        logger.info("Application initialization complete")
    
    def _setup_logging(self):
        """Configure application logging"""
        setup_logging(
            log_level=self.config.logging.level,
            log_to_file=self.config.logging.log_to_file,
            log_to_console=self.config.logging.log_to_console,
            log_dir=self.config.logging.log_dir,
            max_bytes=self.config.logging.max_log_size_mb * 1024 * 1024,
            backup_count=self.config.logging.backup_count
        )
    
    def _setup_event_handlers(self):
        """Setup event handlers for cross-system coordination"""
        # Mark as modified when cats change
        self.event_bus.subscribe(EventType.CAT_ADDED, self._on_data_modified)
        self.event_bus.subscribe(EventType.CAT_UPDATED, self._on_data_modified)
        self.event_bus.subscribe(EventType.CAT_DELETED, self._on_data_modified)
        self.event_bus.subscribe(EventType.LITTER_SAVED, self._on_data_modified)
        
        # Update database when data changes
        if self.database:
            self.event_bus.subscribe(EventType.CAT_ADDED, self._on_cat_added_to_db)
            self.event_bus.subscribe(EventType.CAT_UPDATED, self._on_cat_updated_in_db)
            self.event_bus.subscribe(EventType.CAT_DELETED, self._on_cat_deleted_from_db)
            self.event_bus.subscribe(EventType.LITTER_SAVED, self._on_litter_saved_to_db)
        
        # Clear inbreeding cache when cats change
        self.event_bus.subscribe(EventType.CAT_ADDED, lambda e: self.inbreeding_calculator.clear_cache())
        self.event_bus.subscribe(EventType.CAT_UPDATED, lambda e: self.inbreeding_calculator.clear_cache())
        self.event_bus.subscribe(EventType.CAT_DELETED, lambda e: self.inbreeding_calculator.clear_cache())
    
    def _on_data_modified(self, event):
        """Mark application as modified"""
        self.is_modified = True
        self.event_bus.emit(EventType.REGISTRY_MODIFIED, None, source='Application')
    
    def _on_cat_added_to_db(self, event):
        """Sync new cat to database"""
        if not self.database:
            return
        try:
            cat = event.data
            if cat and cat.id not in self.database.get_all_cats():
                self.database.insert_cat(cat)
        except Exception as e:
            logger.error(f"Failed to add cat to database: {e}")
    
    def _on_cat_updated_in_db(self, event):
        """Sync updated cat to database"""
        if not self.database:
            return
        try:
            cat = event.data
            if cat:
                self.database.update_cat(cat)
        except Exception as e:
            logger.error(f"Failed to update cat in database: {e}")
    
    def _on_cat_deleted_from_db(self, event):
        """Remove cat from database"""
        if not self.database:
            return
        try:
            cat_id = event.data
            if cat_id:
                self.database.delete_cat(cat_id)
        except Exception as e:
            logger.error(f"Failed to delete cat from database: {e}")
    
    def _on_litter_saved_to_db(self, event):
        """Record litter in database"""
        if not self.database:
            return
        try:
            data = event.data
            if data:
                # Extract litter info from pending litter
                litter_id = data.get('litter_id', '')
                cat_ids = data.get('cat_ids', [])
                
                # Parse sire and dam from litter_id
                if 'x' in litter_id:
                    parts = litter_id.split('_')[1].split('x')
                    if len(parts) == 2:
                        sire_id = int(parts[0])
                        dam_id = int(parts[1])
                        self.database.record_litter(sire_id, dam_id, cat_ids)
        except Exception as e:
            logger.error(f"Failed to record litter in database: {e}")
    
    def load_registry(self, filepath: Path) -> bool:
        """
        Load registry from file
        
        Args:
            filepath: Path to registry file
            
        Returns:
            True if successful
        """
        try:
            import json
            filepath = Path(filepath)
            
            logger.info(f"Loading registry from {filepath}")
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Clear current registry
            self.registry.clear()
            
            # Load data
            self.registry.load_from_data(data)
            
            # Validate loaded data
            if self.config.validation.validate_on_save:
                validation_report = self.registry_validator.validate_registry()
                if validation_report.has_errors():
                    logger.warning(f"Loaded registry has validation errors: {validation_report.summary()}")
                else:
                    logger.info("Registry validation passed")
            
            # Sync to database if available
            if self.database:
                self._sync_registry_to_database()
            
            self.current_file = filepath
            self.is_modified = False
            
            # Emit event
            self.event_bus.emit(
                EventType.REGISTRY_LOADED,
                {'filepath': str(filepath), 'cat_count': len(self.registry)},
                source='Application'
            )
            
            logger.info(f"Successfully loaded {len(self.registry)} cats")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load registry: {e}", exc_info=True)
            return False
    
    def save_registry(self, filepath: Optional[Path] = None) -> bool:
        """
        Save registry to file
        
        Args:
            filepath: Path to save to (uses current_file if None)
            
        Returns:
            True if successful
        """
        if filepath is None:
            filepath = self.current_file
        
        if filepath is None:
            logger.error("No file path specified for save")
            return False
        
        try:
            import json
            filepath = Path(filepath)
            
            logger.info(f"Saving registry to {filepath}")
            
            # Validate before saving
            if self.config.validation.validate_on_save:
                validation_report = self.registry_validator.validate_registry()
                if validation_report.has_errors():
                    logger.error(f"Cannot save: validation failed - {validation_report.summary()}")
                    return False
            
            # Prepare data
            data = self.registry.to_data()
            
            # Create backup if file exists
            if filepath.exists() and self.config.database.backup_enabled:
                backup_path = filepath.with_suffix('.bak')
                import shutil
                shutil.copy2(filepath, backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Save to file
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2 if self.config.export.pretty_print else None)
            
            self.current_file = filepath
            self.is_modified = False
            self.last_save_time = datetime.now()
            
            # Emit event
            self.event_bus.emit(
                EventType.REGISTRY_SAVED,
                {'filepath': str(filepath), 'cat_count': len(self.registry)},
                source='Application'
            )
            
            logger.info(f"Successfully saved {len(self.registry)} cats")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save registry: {e}", exc_info=True)
            return False
    
    def _sync_registry_to_database(self):
        """Sync entire registry to database"""
        if not self.database:
            return
        
        logger.info("Syncing registry to database")
        
        # Get existing cat IDs in database
        db_cats = {cat.id for cat in self.database.get_all_cats()}
        
        # Add/update cats
        for cat in self.registry.get_all_cats():
            if cat.id in db_cats:
                self.database.update_cat(cat)
            else:
                # Manually set ID to maintain consistency
                cursor = self.database.conn.execute('''
                    INSERT INTO cats (
                        id, name, sex, genes, birth_date, sire_id, dam_id,
                        build_value, size_value, white_percentage
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cat.id, cat.name, cat.sex, 
                    self.database.conn.execute('SELECT json(?)', (str(cat.genes),)).fetchone()[0],
                    cat.birth_date, cat.sire_id, cat.dam_id,
                    cat.build_value, cat.size_value, cat._white_percentage
                ))
        
        self.database.conn.commit()
        logger.info("Registry synced to database")
    
    def export_report(self, filepath: Path, include_analytics: bool = True) -> bool:
        """
        Export comprehensive report
        
        Args:
            filepath: Path to save report
            include_analytics: Whether to include genetic analysis
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Generating report: {filepath}")
            
            report = {
                'generated': datetime.now().isoformat(),
                'catgen_version': self.config.version,
                'registry': {
                    'total_cats': len(self.registry),
                    'males': len(self.registry.get_males()),
                    'females': len(self.registry.get_females())
                }
            }
            
            if include_analytics:
                logger.info("Calculating analytics...")
                
                # Population metrics
                report['population'] = self.diversity_analyzer.effective_population_size()
                
                # Heterozygosity
                report['heterozygosity'] = self.diversity_analyzer.calculate_heterozygosity()
                
                # Allele frequencies
                report['allele_frequencies'] = self.diversity_analyzer.calculate_allele_frequencies()
                
                # Rare alleles
                report['rare_alleles'] = self.diversity_analyzer.identify_rare_alleles()
                
                # Inbred cats
                inbred_cats = self.inbreeding_calculator.find_inbred_cats(threshold=0.0625)
                report['inbred_cats'] = inbred_cats
                
                # Founder contributions
                report['founder_contributions'] = self.diversity_analyzer.calculate_founder_contribution()
            
            # Save report
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Report saved: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}", exc_info=True)
            return False
    
    def get_statistics(self) -> dict:
        """Get comprehensive statistics"""
        stats = self.cat_service.get_statistics()
        
        # Add analytics
        stats['diversity'] = {
            'effective_size': self.diversity_analyzer.effective_population_size(),
            'mean_heterozygosity': sum(
                h['observed'] for h in 
                self.diversity_analyzer.calculate_heterozygosity().values()
            ) / max(len(self.diversity_analyzer.calculate_heterozygosity()), 1)
        }
        
        # Inbreeding stats
        inbred = self.inbreeding_calculator.find_inbred_cats(0.0625)
        stats['inbreeding'] = {
            'count': len(inbred),
            'percentage': len(inbred) / max(len(self.registry), 1) * 100
        }
        
        return stats
    
    def validate_all(self) -> dict:
        """
        Run comprehensive validation
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Running comprehensive validation")
        
        results = {}
        
        # Registry validation
        registry_report = self.registry_validator.validate_registry()
        results['registry'] = registry_report.to_dict()
        
        # Individual cat validation
        cat_errors = []
        for cat in self.registry.get_all_cats():
            cat_report = self.cat_validator.validate(cat)
            if cat_report.has_errors():
                cat_errors.append({
                    'cat_id': cat.id,
                    'errors': [r.to_dict() for r in cat_report.get_errors()]
                })
        results['cats_with_errors'] = cat_errors
        
        # Summary
        results['summary'] = {
            'total_errors': len(registry_report.get_errors()),
            'total_warnings': len(registry_report.get_warnings()),
            'cats_with_errors': len(cat_errors),
            'is_valid': registry_report.is_valid() and len(cat_errors) == 0
        }
        
        logger.info(f"Validation complete: {results['summary']}")
        
        return results
    
    def backup_database(self) -> bool:
        """Create database backup"""
        if not self.database:
            logger.warning("No database to backup")
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.config.data_dir / f"backups/catgen_{timestamp}.db"
            
            self.database.backup_database(backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)
            return False
    
    def cleanup(self):
        """Cleanup resources before shutdown"""
        logger.info("Cleaning up application resources")
        
        # Close database
        if self.database:
            if self.config.database.auto_vacuum:
                self.database.vacuum()
            self.database.close()
        
        # Clear event bus
        self.event_bus.clear_listeners()
        
        logger.info("Cleanup complete")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


def create_application(config_path: Optional[Path] = None) -> CatGenApplication:
    """
    Factory function to create configured application instance
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Configured CatGenApplication instance
    """
    if config_path and Path(config_path).exists():
        config = AppConfig.load(config_path)
    else:
        config = get_config()
    
    return CatGenApplication(config)