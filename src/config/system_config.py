"""
⚙️ System Configuration Management
Addresses critical system need: standardized environment configuration
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    database_url: str = "sqlite:///dsatrain_phase4.db"
    skill_tree_database_url: str = "sqlite:///dsatrain_skilltree.db"
    connection_pool_size: int = 5
    connection_timeout: int = 30
    backup_enabled: bool = True
    backup_interval_hours: int = 24

@dataclass
class ServerConfig:
    """Server configuration settings"""
    host: str = "127.0.0.1"
    port: int = 8001
    debug: bool = False
    reload: bool = False
    workers: int = 1
    log_level: str = "info"
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = [
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001"
            ]

@dataclass
class SkillTreeConfig:
    """Skill tree specific configuration"""
    default_similarity_threshold: float = 0.3
    max_similar_problems: int = 10
    clustering_enabled: bool = True
    confidence_tracking_enabled: bool = True
    analytics_enabled: bool = True
    cache_similarity_results: bool = True
    cache_timeout_seconds: int = 3600

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 100
    cors_allow_credentials: bool = True

@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "logs/dsatrain.log"
    max_log_size_mb: int = 10
    backup_count: int = 5
    console_logging: bool = True

class SystemConfig:
    """Central system configuration management"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/system_config.json"
        self.config_dir = Path(self.config_file).parent
        
        # Default configurations
        self.database = DatabaseConfig()
        self.server = ServerConfig()
        self.skill_tree = SkillTreeConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()
        
        # Load from file or environment
        self.load_configuration()
    
    def load_configuration(self):
        """Load configuration from file and environment variables"""
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load from config file if it exists
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                self._apply_config_data(config_data)
                logger.info(f"✅ Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config file: {e}")
        
        # Override with environment variables
        self._load_from_environment()
        
        # Validate configuration
        self._validate_configuration()
    
    def _apply_config_data(self, config_data: Dict[str, Any]):
        """Apply configuration data to config objects"""
        
        for section_name, section_data in config_data.items():
            if hasattr(self, section_name):
                section_obj = getattr(self, section_name)
                for key, value in section_data.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        
        # Database configuration
        if os.getenv("DATABASE_URL"):
            self.database.database_url = os.getenv("DATABASE_URL")
        
        if os.getenv("SKILL_TREE_DATABASE_URL"):
            self.database.skill_tree_database_url = os.getenv("SKILL_TREE_DATABASE_URL")
        
        # Server configuration
        if os.getenv("HOST"):
            self.server.host = os.getenv("HOST")
        
        if os.getenv("PORT"):
            self.server.port = int(os.getenv("PORT"))
        
        if os.getenv("DEBUG"):
            self.server.debug = os.getenv("DEBUG").lower() == "true"
        
        if os.getenv("LOG_LEVEL"):
            self.server.log_level = os.getenv("LOG_LEVEL").lower()
        
        # Security configuration
        if os.getenv("JWT_SECRET_KEY"):
            self.security.jwt_secret_key = os.getenv("JWT_SECRET_KEY")
        
        # Logging configuration
        if os.getenv("LOG_LEVEL"):
            self.logging.log_level = os.getenv("LOG_LEVEL")
        
        if os.getenv("LOG_FILE"):
            self.logging.log_file = os.getenv("LOG_FILE")
    
    def _validate_configuration(self):
        """Validate configuration settings"""
        
        # Validate database URLs
        if not self.database.database_url:
            raise ValueError("Database URL cannot be empty")
        
        # Validate server settings
        if self.server.port < 1 or self.server.port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        
        # Validate security settings
        if len(self.security.jwt_secret_key) < 16:
            logger.warning("⚠️ JWT secret key should be at least 16 characters")
        
        # Create log directory
        log_path = Path(self.logging.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_configuration(self):
        """Save current configuration to file"""
        
        config_data = {
            "database": {
                "database_url": self.database.database_url,
                "skill_tree_database_url": self.database.skill_tree_database_url,
                "connection_pool_size": self.database.connection_pool_size,
                "connection_timeout": self.database.connection_timeout,
                "backup_enabled": self.database.backup_enabled,
                "backup_interval_hours": self.database.backup_interval_hours
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "debug": self.server.debug,
                "reload": self.server.reload,
                "workers": self.server.workers,
                "log_level": self.server.log_level,
                "cors_origins": self.server.cors_origins
            },
            "skill_tree": {
                "default_similarity_threshold": self.skill_tree.default_similarity_threshold,
                "max_similar_problems": self.skill_tree.max_similar_problems,
                "clustering_enabled": self.skill_tree.clustering_enabled,
                "confidence_tracking_enabled": self.skill_tree.confidence_tracking_enabled,
                "analytics_enabled": self.skill_tree.analytics_enabled,
                "cache_similarity_results": self.skill_tree.cache_similarity_results,
                "cache_timeout_seconds": self.skill_tree.cache_timeout_seconds
            },
            "security": {
                "jwt_algorithm": self.security.jwt_algorithm,
                "jwt_expiration_hours": self.security.jwt_expiration_hours,
                "rate_limit_enabled": self.security.rate_limit_enabled,
                "max_requests_per_minute": self.security.max_requests_per_minute,
                "cors_allow_credentials": self.security.cors_allow_credentials
            },
            "logging": {
                "log_level": self.logging.log_level,
                "log_format": self.logging.log_format,
                "log_file": self.logging.log_file,
                "max_log_size_mb": self.logging.max_log_size_mb,
                "backup_count": self.logging.backup_count,
                "console_logging": self.logging.console_logging
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
    
    def get_database_url(self, use_main_db: bool = True) -> str:
        """Get appropriate database URL"""
        if use_main_db:
            return self.database.database_url
        else:
            return self.database.skill_tree_database_url
    
    def setup_logging(self):
        """Setup logging configuration"""
        
        log_path = Path(self.logging.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        handlers = []
        
        # File handler
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            self.logging.log_file,
            maxBytes=self.logging.max_log_size_mb * 1024 * 1024,
            backupCount=self.logging.backup_count
        )
        file_handler.setFormatter(logging.Formatter(self.logging.log_format))
        handlers.append(file_handler)
        
        # Console handler
        if self.logging.console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(self.logging.log_format))
            handlers.append(console_handler)
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, self.logging.log_level.upper()),
            handlers=handlers,
            format=self.logging.log_format
        )
        
        logger.info("✅ Logging configuration applied")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "database": {
                "main_db": self.database.database_url,
                "skill_tree_db": self.database.skill_tree_database_url,
                "backup_enabled": self.database.backup_enabled
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "debug": self.server.debug,
                "workers": self.server.workers
            },
            "skill_tree": {
                "clustering_enabled": self.skill_tree.clustering_enabled,
                "confidence_tracking": self.skill_tree.confidence_tracking_enabled,
                "analytics_enabled": self.skill_tree.analytics_enabled
            },
            "security": {
                "rate_limiting": self.security.rate_limit_enabled,
                "cors_enabled": bool(self.server.cors_origins)
            },
            "logging": {
                "level": self.logging.log_level,
                "file_logging": bool(self.logging.log_file),
                "console_logging": self.logging.console_logging
            }
        }

# Global configuration instance
_system_config = None

def get_system_config() -> SystemConfig:
    """Get global system configuration instance"""
    global _system_config
    if _system_config is None:
        _system_config = SystemConfig()
    return _system_config

def setup_system_configuration(config_file: Optional[str] = None):
    """Setup system configuration with optional config file"""
    global _system_config
    _system_config = SystemConfig(config_file)
    _system_config.setup_logging()
    return _system_config

if __name__ == "__main__":
    # Configuration setup utility
    print("⚙️ DSA Train System Configuration Setup")
    print("=" * 50)
    
    config = SystemConfig()
    
    print("\n📋 Current Configuration Summary:")
    summary = config.get_summary()
    for section, settings in summary.items():
        print(f"\n{section.upper()}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    print(f"\n💾 Configuration file: {config.config_file}")
    
    # Save configuration
    response = input("\n🤔 Save current configuration to file? (y/N): ").lower().strip()
    if response in ['y', 'yes']:
        config.save_configuration()
        print("✅ Configuration saved successfully!")
    else:
        print("❌ Configuration not saved")
