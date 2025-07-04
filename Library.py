


import logging
from typing import Optional, Dict, Any, List

class BoostWorkLib(loader.Library):
    '''Lib for modules to speed up work'''
    
    developer = "@/Kowalskiu"
    version = (1, 0, 37)
    logger = logging.getLogger(__name__)

    def __init__(self):
        """Инициализация библиотеки с настройками по умолчанию"""
        super().__init__()
        self._performance_stats: Dict[str, Any] = {}
        self._optimization_enabled: bool = False

    def init(self) -> None:
        """Инициализация конфигурации библиотеки. Создает конфигурационные параметры с значениями по умолчанию."""
        try:
            self.config = loader.LibraryConfig(
                loader.ConfigValue(
                    "enable_performance_boost",
                    "Включить оптимизацию производительности",
                    True,
                    validator=loader.validators.Boolean()
                ),
                loader.ConfigValue(
                    "max_cpu_usage",
                    "Максимальное использование CPU (%)",
                    80,
                    validator=loader.validators.Integer(minimum=10, maximum=100)
                ),
                loader.ConfigValue(
                    "cache_ttl",
                    "Время жизни кеша (сек)",
                    300,
                    validator=loader.validators.Integer(minimum=60)
                ),
                loader.ConfigValue(
                    "monitoring_interval",
                    "Интервал мониторинга (сек)",
                    60,
                    validator=loader.validators.Integer(minimum=10)
                )
            )
            self._optimization_enabled = self.config["enable_performance_boost"]
            self.logger.info("BoostWorkLib initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize BoostWorkLib: {e}")
            raise

    async def enable_optimization(self) -> bool:
        """Включает оптимизацию производительности. Returns: bool: True если оптимизация успешно включена, False в случае ошибки"""
        try:
            self._optimization_enabled = True
            self.config["enable_performance_boost"] = True
            self.logger.info("Performance optimization enabled")
            return True
        except Exception as e:
            self.logger.error(f"Failed to enable optimization: {e}")
            return False

    async def disable_optimization(self) -> bool:
        """Выключает оптимизацию производительности. Returns: bool: True если оптимизация успешно выключена, False в случае ошибки"""
        try:
            self._optimization_enabled = False
            self.config["enable_performance_boost"] = False
            self.logger.info("Performance optimization disabled")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disable optimization: {e}")
            return False

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Возвращает текущую статистику производительности. Returns: Dict[str, Any]: Словарь с метриками производительности"""
        return {
            "optimization_enabled": self._optimization_enabled,
            "config": dict(self.config),
            **self._performance_stats
        }
