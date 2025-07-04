# TariffAI Backend Application
# A modular tariff management platform

__version__ = "1.0.0"
__author__ = "TariffAI Team"
__description__ = "Enterprise-grade tariff management chatbot with AI-powered insights"

# Export all submodules
from . import api, core, services, agents, db

__all__ = ['api', 'core', 'services', 'agents', 'db'] 