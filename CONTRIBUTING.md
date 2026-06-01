"""Contributing Guidelines

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints everywhere
- Max line length: 100 characters
- Format with: `black .`
- Lint with: `flake8`

### TypeScript/JavaScript (Frontend)
- Use Prettier formatting
- Strict TypeScript mode
- ESLint configuration provided
- Max line length: 100 characters

## Commit Messages

Format: `[type]: description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code structure
- `test`: Tests
- `chore`: Dependencies

Example: `feat: add demand forecasting endpoint`

## Pull Requests

1. Create feature branch: `git checkout -b feature/feature-name`
2. Make changes following code style
3. Add tests if applicable
4. Write clear commit messages
5. Push and create PR with description
6. Address review feedback

## Testing

Before submitting:
```bash
# Backend
pytest
black . --check
flake8

# Frontend
npm test
npm run lint
npm run type-check
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation
- Add examples for new features

## Questions?

Open an issue or check existing documentation.
"""
