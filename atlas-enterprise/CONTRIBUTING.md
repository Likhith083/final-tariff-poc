# Contributing to ATLAS Enterprise

Thank you for your interest in contributing to ATLAS Enterprise! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

### Types of Contributions

We welcome contributions in the following areas:

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new functionality
- **📚 Documentation**: Improve guides, README, and API docs
- **🧪 Testing**: Add tests or improve test coverage
- **🔧 Code Improvements**: Optimize performance, refactor code
- **🌍 Localization**: Add support for additional languages
- **🎨 UI/UX**: Improve the user interface and experience

### Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/atlas-enterprise.git
   cd atlas-enterprise
   ```

2. **Set up development environment**
   ```bash
   # Backend
   cd backend
   pip install -r simple_requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Development Guidelines

### Code Style

#### Python (Backend)
- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Keep functions focused and under 50 lines when possible
- Use descriptive variable and function names

```python
def calculate_tariff(hts_code: str, product_value: float) -> Dict[str, Any]:
    """Calculate comprehensive tariff costs.
    
    Args:
        hts_code: The HTS code for the product
        product_value: The value of the product in USD
        
    Returns:
        Dictionary containing tariff calculation results
    """
    # Implementation here
```

#### TypeScript/JavaScript (Frontend)
- Use **ESLint** and **Prettier** for code formatting
- Follow **React best practices**
- Use **TypeScript** for type safety
- Implement proper error handling

```typescript
interface TariffCalculation {
  htsCode: string;
  productValue: number;
  dutyRate: number;
  totalCost: number;
}

const calculateTariff = async (data: TariffCalculation): Promise<Result> => {
  try {
    // Implementation here
  } catch (error) {
    console.error('Tariff calculation failed:', error);
    throw error;
  }
};
```

### Testing

#### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

#### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Documentation

- Update **README.md** for new features
- Add **API documentation** for new endpoints
- Include **code comments** for complex logic
- Update **CHANGELOG.md** for significant changes

## 🚀 Pull Request Process

### Before Submitting

1. **Test your changes**
   ```bash
   # Backend tests
   cd backend && python -m pytest
   
   # Frontend tests
   cd frontend && npm test
   
   # Integration tests
   docker-compose up -d
   # Run your manual tests
   ```

2. **Check code quality**
   ```bash
   # Python linting
   flake8 backend/
   
   # TypeScript linting
   cd frontend && npm run lint
   ```

3. **Update documentation**
   - Update README if needed
   - Add API documentation
   - Update changelog

### Submitting a PR

1. **Create a descriptive title**
   ```
   feat: Add advanced tariff calculation with Section 301 support
   ```

2. **Write a detailed description**
   ```markdown
   ## Description
   Added advanced tariff calculation that includes Section 301 tariffs for Chinese imports.
   
   ## Changes
   - Added Section 301 tariff detection logic
   - Updated tariff calculation endpoint
   - Added tests for new functionality
   
   ## Testing
   - [x] Unit tests pass
   - [x] Integration tests pass
   - [x] Manual testing completed
   ```

3. **Use conventional commit messages**
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `style:` for formatting changes
   - `refactor:` for code refactoring
   - `test:` for adding tests
   - `chore:` for maintenance tasks

## 🐛 Bug Reports

### Before Reporting

1. **Check existing issues** - Search for similar problems
2. **Reproduce the issue** - Ensure it's consistently reproducible
3. **Check logs** - Look at backend/frontend logs for errors

### Bug Report Template

```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 11]
- Browser: [e.g., Chrome 120]
- ATLAS Version: [e.g., 2.0.0]
- Ollama Version: [e.g., 0.1.0]

## Additional Context
Screenshots, logs, or other relevant information
```

## ✨ Feature Requests

### Feature Request Template

```markdown
## Feature Description
Brief description of the requested feature

## Use Case
How would this feature be used?

## Proposed Implementation
Any ideas on how to implement this?

## Alternatives Considered
Other approaches you've considered

## Additional Context
Any other relevant information
```

## 🏗️ Architecture Guidelines

### Backend Architecture

- **FastAPI** for API endpoints
- **Pydantic** for data validation
- **Async/await** for database operations
- **Proper error handling** with HTTP status codes
- **Logging** for debugging and monitoring

### Frontend Architecture

- **React** with functional components
- **TanStack Query** for data fetching
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Component composition** over inheritance

### Database Design

- **PostgreSQL** for relational data
- **Redis** for caching and sessions
- **Proper indexing** for performance
- **Migration scripts** for schema changes

## 🔧 Development Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Ollama** (for AI features)
- **Git**

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/atlas-enterprise.git
cd atlas-enterprise

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r simple_requirements.txt

# Frontend setup
cd frontend
npm install

# Start development servers
# Terminal 1: Backend
cd backend && python main_unified.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Ollama
ollama serve
```

### Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up -d --build
```

## 📊 Performance Guidelines

### Backend Performance

- **Database queries**: Use proper indexing
- **Caching**: Implement Redis caching for frequently accessed data
- **Async operations**: Use async/await for I/O operations
- **Connection pooling**: For database connections

### Frontend Performance

- **Code splitting**: Use React.lazy for route-based splitting
- **Memoization**: Use React.memo and useMemo appropriately
- **Bundle optimization**: Minimize bundle size
- **Image optimization**: Compress and optimize images

## 🔒 Security Guidelines

### Backend Security

- **Input validation**: Validate all user inputs
- **Authentication**: Implement proper JWT authentication
- **Authorization**: Use role-based access control
- **SQL injection**: Use parameterized queries
- **CORS**: Configure CORS properly

### Frontend Security

- **XSS prevention**: Sanitize user inputs
- **CSRF protection**: Implement CSRF tokens
- **Secure storage**: Use secure storage for sensitive data
- **HTTPS**: Always use HTTPS in production

## 🧪 Testing Guidelines

### Test Types

- **Unit tests**: Test individual functions/components
- **Integration tests**: Test API endpoints
- **E2E tests**: Test complete user workflows
- **Performance tests**: Test under load

### Test Coverage

- **Backend**: Aim for 80%+ coverage
- **Frontend**: Aim for 70%+ coverage
- **Critical paths**: 100% coverage for critical functionality

## 📝 Documentation Standards

### Code Documentation

- **Docstrings**: Use Google-style docstrings for Python
- **JSDoc**: Use JSDoc for JavaScript/TypeScript
- **Inline comments**: Explain complex logic
- **README**: Keep README up to date

### API Documentation

- **OpenAPI/Swagger**: Document all API endpoints
- **Examples**: Provide request/response examples
- **Error codes**: Document all possible error responses

## 🤝 Community Guidelines

### Code of Conduct

- **Be respectful**: Treat others with respect
- **Be inclusive**: Welcome contributors from all backgrounds
- **Be constructive**: Provide constructive feedback
- **Be patient**: Understand that contributors have different skill levels

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and ideas
- **Pull Requests**: For code contributions
- **Discord/Slack**: For real-time communication (if available)

## 🎉 Recognition

Contributors will be recognized in:

- **README.md**: List of contributors
- **Release notes**: Credit for significant contributions
- **GitHub profile**: Contributor badges and statistics

---

Thank you for contributing to ATLAS Enterprise! 🚀 