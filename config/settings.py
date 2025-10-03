"""
Configuration management for CatGen
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json
import logging

logger = logging.getLogger('catgen.config')


@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: Path = Path("data/catgen.db")
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    auto_vacuum: bool = True
    cache_phenotypes: bool = True
    
    def __post_init__(self):
        if isinstance(self.path, str):
            self.path = Path(self.path)


@dataclass
class CacheConfig:
    """Caching configuration"""
    enabled: bool = True
    max_phenotype_cache: int = 10000
    max_pedigree_cache: int = 1000
    ttl_seconds: int = 3600  # 1 hour
    clear_on_gene_change: bool = True


@dataclass
class BreedingConfig:
    """Breeding configuration"""
    default_litter_size: int = 4
    min_litter_size: int = 1
    max_litter_size: int = 12
    warn_on_inbreeding: bool = True
    inbreeding_threshold_generations: int = 3
    allow_close_inbreeding: bool = False  # Parent-offspring, siblings
    default_rarity_boost: float = 1.0


@dataclass
class ValidationConfig:
    """Validation configuration"""
    strict_mode: bool = True
    warn_missing_genes: bool = True
    allow_unknown_genes: bool = False
    validate_on_save: bool = True
    validate_parents_exist: bool = True


@dataclass
class UIConfig:
    """UI configuration"""
    theme: str = "dark"  # or "light"
    window_width: int = 1400
    window_height: int = 900
    auto_save_enabled: bool = True
    auto_save_interval_seconds: int = 300  # 5 minutes
    show_notifications: bool = True
    remember_last_file: bool = True


@dataclass
class ExportConfig:
    """Export configuration"""
    default_format: str = "json"
    include_phenotypes: bool = True
    include_pedigrees: bool = True
    pretty_print: bool = True
    export_images: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_to_file: bool = True
    log_to_console: bool = True
    log_dir: Path = Path("logs")
    max_log_size_mb: int = 10
    backup_count: int = 5
    
    def __post_init__(self):
        if isinstance(self.log_dir, str):
            self.log_dir = Path(self.log_dir)


@dataclass
class AppConfig:
    """Main application configuration"""
    # Sub-configs
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    breeding: BreedingConfig = field(default_factory=BreedingConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Paths
    data_dir: Path = Path("data")
    resources_dir: Path = Path("resources")
    genes_file: Path = Path("resources/genes.json")
    
    # Application
    app_name: str = "CatGen"
    version: str = "2.0.0"
    
    def __post_init__(self):
        # Convert strings to Paths
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
        if isinstance(self.resources_dir, str):
            self.resources_dir = Path(self.resources_dir)
        if isinstance(self.genes_file, str):
            self.genes_file = Path(self.genes_file)
    
    def save(self, filepath: Path):
        """Save configuration to JSON file"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = self.to_dict()
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Configuration saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: Path) -> 'AppConfig':
        """Load configuration from JSON file"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.warning(f"Config file not found: {filepath}, using defaults")
            return cls()
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        config = cls.from_dict(data)
        logger.info(f"Configuration loaded from {filepath}")
        return config
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'database': {
                'path': str(self.database.path),
                'backup_enabled': self.database.backup_enabled,
                'backup_interval_hours': self.database.backup_interval_hours,
                'auto_vacuum': self.database.auto_vacuum,
                'cache_phenotypes': self.database.cache_phenotypes
            },
            'cache': {
                'enabled': self.cache.enabled,
                'max_phenotype_cache': self.cache.max_phenotype_cache,
                'max_pedigree_cache': self.cache.max_pedigree_cache,
                'ttl_seconds': self.cache.ttl_seconds,
                'clear_on_gene_change': self.cache.clear_on_gene_change
            },
            'breeding': {
                'default_litter_size': self.breeding.default_litter_size,
                'min_litter_size': self.breeding.min_litter_size,
                'max_litter_size': self.breeding.max_litter_size,
                'warn_on_inbreeding': self.breeding.warn_on_inbreeding,
                'inbreeding_threshold_generations': self.breeding.inbreeding_threshold_generations,
                'allow_close_inbreeding': self.breeding.allow_close_inbreeding,
                'default_rarity_boost': self.breeding.default_rarity_boost
            },
            'validation': {
                'strict_mode': self.validation.strict_mode,
                'warn_missing_genes': self.validation.warn_missing_genes,
                'allow_unknown_genes': self.validation.allow_unknown_genes,
                'validate_on_save': self.validation.validate_on_save,
                'validate_parents_exist': self.validation.validate_parents_exist
            },
            'ui': {
                'theme': self.ui.theme,
                'window_width': self.ui.window_width,
                'window_height': self.ui.window_height,
                'auto_save_enabled': self.ui.auto_save_enabled,
                'auto_save_interval_seconds': self.ui.auto_save_interval_seconds,
                'show_notifications': self.ui.show_notifications,
                'remember_last_file': self.ui.remember_last_file
            },
            'export': {
                'default_format': self.export.default_format,
                'include_phenotypes': self.export.include_phenotypes,
                'include_pedigrees': self.export.include_pedigrees,
                'pretty_print': self.export.pretty_print,
                'export_images': self.export.export_images
            },
            'logging': {
                'level': self.logging.level,
                'log_to_file': self.logging.log_to_file,
                'log_to_console': self.logging.log_to_console,
                'log_dir': str(self.logging.log_dir),
                'max_log_size_mb': self.logging.max_log_size_mb,
                'backup_count': self.logging.backup_count
            },
            'data_dir': str(self.data_dir),
            'resources_dir': str(self.resources_dir),
            'genes_file': str(self.genes_file),
            'app_name': self.app_name,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        """Create from dictionary"""
        config = cls()
        
        # Database
        if 'database' in data:
            db = data['database']
            config.database = DatabaseConfig(
                path=Path(db.get('path', 'data/catgen.db')),
                backup_enabled=db.get('backup_enabled', True),
                backup_interval_hours=db.get('backup_interval_hours', 24),
                auto_vacuum=db.get('auto_vacuum', True),
                cache_phenotypes=db.get('cache_phenotypes', True)
            )
        
        # Cache
        if 'cache' in data:
            c = data['cache']
            config.cache = CacheConfig(
                enabled=c.get('enabled', True),
                max_phenotype_cache=c.get('max_phenotype_cache', 10000),
                max_pedigree_cache=c.get('max_pedigree_cache', 1000),
                ttl_seconds=c.get('ttl_seconds', 3600),
                clear_on_gene_change=c.get('clear_on_gene_change', True)
            )
        
        # Breeding
        if 'breeding' in data:
            b = data['breeding']
            config.breeding = BreedingConfig(
                default_litter_size=b.get('default_litter_size', 4),
                min_litter_size=b.get('min_litter_size', 1),
                max_litter_size=b.get('max_litter_size', 12),
                warn_on_inbreeding=b.get('warn_on_inbreeding', True),
                inbreeding_threshold_generations=b.get('inbreeding_threshold_generations', 3),
                allow_close_inbreeding=b.get('allow_close_inbreeding', False),
                default_rarity_boost=b.get('default_rarity_boost', 1.0)
            )
        
        # Validation
        if 'validation' in data:
            v = data['validation']
            config.validation = ValidationConfig(
                strict_mode=v.get('strict_mode', True),
                warn_missing_genes=v.get('warn_missing_genes', True),
                allow_unknown_genes=v.get('allow_unknown_genes', False),
                validate_on_save=v.get('validate_on_save', True),
                validate_parents_exist=v.get('validate_parents_exist', True)
            )
        
        # UI
        if 'ui' in data:
            u = data['ui']
            config.ui = UIConfig(
                theme=u.get('theme', 'dark'),
                window_width=u.get('window_width', 1400),
                window_height=u.get('window_height', 900),
                auto_save_enabled=u.get('auto_save_enabled', True),
                auto_save_interval_seconds=u.get('auto_save_interval_seconds', 300),
                show_notifications=u.get('show_notifications', True),
                remember_last_file=u.get('remember_last_file', True)
            )
        
        # Export
        if 'export' in data:
            e = data['export']
            config.export = ExportConfig(
                default_format=e.get('default_format', 'json'),
                include_phenotypes=e.get('include_phenotypes', True),
                include_pedigrees=e.get('include_pedigrees', True),
                pretty_print=e.get('pretty_print', True),
                export_images=e.get('export_images', False)
            )
        
        # Logging
        if 'logging' in data:
            log = data['logging']
            config.logging = LoggingConfig(
                level=log.get('level', 'INFO'),
                log_to_file=log.get('log_to_file', True),
                log_to_console=log.get('log_to_console', True),
                log_dir=Path(log.get('log_dir', 'logs')),
                max_log_size_mb=log.get('max_log_size_mb', 10),
                backup_count=log.get('backup_count', 5)
            )
        
        # Paths
        config.data_dir = Path(data.get('data_dir', 'data'))
        config.resources_dir = Path(data.get('resources_dir', 'resources'))
        config.genes_file = Path(data.get('genes_file', 'resources/genes.json'))
        
        # App info
        config.app_name = data.get('app_name', 'CatGen')
        config.version = data.get('version', '2.0.0')
        
        return config
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            self.data_dir,
            self.resources_dir,
            self.logging.log_dir,
            self.database.path.parent
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        config_path = Path("config/settings.json")
        if config_path.exists():
            _config = AppConfig.load(config_path)
        else:
            _config = AppConfig()
            # Save default config
            _config.save(config_path)
    return _config


def set_config(config: AppConfig):
    """Set the global configuration instance"""
    global _config
    _config = config


def reset_config():
    """Reset to default configuration"""
    global _config
    _config = AppConfig()