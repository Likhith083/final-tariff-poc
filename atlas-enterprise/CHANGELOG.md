# Changelog

All notable changes to ATLAS Enterprise will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of ATLAS Enterprise
- AI chatbot with local Ollama integration
- HTS database with 12,900+ codes
- Multi-country sourcing analysis
- Real-time tariff calculations
- Knowledge base with ChromaDB vector search
- Docker containerization
- Comprehensive API documentation

### Changed
- Enhanced AI context integration
- Improved Docker-Ollama connection
- Optimized HTS search performance

### Fixed
- Resolved mock data interference with AI responses
- Fixed Docker container networking for Ollama
- Corrected PowerShell startup scripts

## [2.0.0] - 2025-07-06

### Added
- **AI Chatbot**: Local Ollama integration with knowledge base context
- **HTS Database**: Real 2025 tariff data with 12,900+ codes
- **Sourcing Analysis**: Multi-country comparison with risk assessment
- **Tariff Calculator**: Comprehensive duty and fee calculations
- **Vector Search**: ChromaDB integration for knowledge base
- **Docker Support**: Complete containerization with docker-compose
- **API Documentation**: Swagger UI and ReDoc
- **Frontend Dashboard**: React-based unified interface
- **PowerShell Scripts**: Windows-compatible startup scripts

### Technical Features
- FastAPI backend with async support
- React frontend with TypeScript
- TanStack Query for data fetching
- PostgreSQL database with Redis caching
- Celery for background task processing
- Comprehensive logging and error handling

### AI Integration
- Support for multiple Ollama models:
  - llama3.1, llama3.2:3b, qwen3:8b
  - devstral:24b, deepseek-r1:8b
  - gemma3:4b, phi4, moondream
- Knowledge base with trade compliance information
- Contextual AI responses with HTS code references
- Product search integration

### Data & Compliance
- Real HTS tariff database (2025)
- Section 301 tariff calculations
- Multi-country sourcing analysis
- Trade agreement benefits (GSP, USMCA)
- Risk assessment and competitiveness scoring

## [1.0.0] - 2025-07-01

### Added
- Initial project setup
- Basic FastAPI backend structure
- React frontend foundation
- Docker configuration
- Basic documentation

---

## Version History

- **v2.0.0**: Production-ready release with AI integration
- **v1.0.0**: Initial project foundation

## Migration Guide

### From v1.0.0 to v2.0.0

1. **Update Docker images**:
   ```bash
   docker-compose pull
   docker-compose up -d --build
   ```

2. **Install Ollama** (required for AI features):
   ```bash
   # Install Ollama
   # https://ollama.ai/
   
   # Pull recommended models
   ollama pull llama3.1
   ollama pull llama3.2:3b
   ```

3. **Update environment variables**:
   ```env
   OLLAMA_BASE_URL=http://localhost:11434
   DEFAULT_MODEL=llama3.1
   ```

4. **Database migration** (if needed):
   ```bash
   # The system will automatically handle data loading
   # No manual migration required
   ```

## Deprecation Notices

- No deprecations in v2.0.0

## Breaking Changes

- No breaking changes in v2.0.0

---

For detailed information about each release, see the [GitHub releases page](https://github.com/yourusername/atlas-enterprise/releases).

## Upcoming Features

### Version 2.1.0 (Planned)
- [ ] Advanced AI agent workflows
- [ ] Real-time market data integration
- [ ] Enhanced reporting and analytics
- [ ] Mobile application support

### Version 2.2.0 (Planned)
- [ ] Multi-language support
- [ ] Advanced compliance features
- [ ] Integration with external trade systems
- [ ] Machine learning model training

---

## Support

For questions about version compatibility or migration:
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/atlas-enterprise/issues)
- **Documentation**: Check the README and docs folder
- **Community**: Join our discussions on GitHub 