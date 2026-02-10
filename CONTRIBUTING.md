# Contributing to GTT Blotzman Code

Thank you for your interest in contributing to the GTT Blotzman Code! This document provides guidelines for contributing to the project.

---

## 🎯 How to Contribute

### 1. **Bug Reports**
If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- System information (OS, Python version, etc.)

### 2. **Feature Requests**
For new features:
- Describe the feature and its use case
- Explain how it fits with SDGFT theory
- Provide examples if possible

### 3. **Code Contributions**
We welcome pull requests! Please:
- Fork the repository
- Create a feature branch (`git checkout -b feature/amazing-feature`)
- Make your changes
- Add tests for new functionality
- Ensure all tests pass (`python test_suite.py`)
- Commit with clear messages
- Push to your fork
- Open a Pull Request

---

## 📋 Development Guidelines

### Code Style

#### Python
- Follow PEP 8
- Use type hints where appropriate
- Document all functions with docstrings
- Keep functions focused and < 50 lines

```python
def example_function(param: float) -> float:
    """
    Brief description.
    
    Parameters
    ----------
    param : float
        Description of parameter
        
    Returns
    -------
    float
        Description of return value
    """
    return param * 2.0
```

#### C
- Follow K&R style
- Use descriptive variable names
- Comment complex algorithms
- Check for memory leaks

```c
/**
 * @brief Brief description
 * @param param Description
 * @return Description
 */
double example_function(double param) {
    return param * 2.0;
}
```

### Testing

All contributions must include tests:
- Unit tests for new functions
- Integration tests for new modules
- Validation against known results

Run tests before submitting:
```bash
python test_suite.py
make test  # For C code
```

### Documentation

Update documentation for:
- New features
- Changed behavior
- New parameters
- Examples

---

## 🔬 Scientific Contributions

### Theoretical Extensions

If you want to extend the theory:
1. Ensure consistency with GTT World Formula
2. Provide mathematical derivation
3. Make testable predictions
4. Validate against existing data

### Observational Comparisons

For new data comparisons:
1. Use publicly available data
2. Document data sources
3. Include error analysis
4. Compare with ΛCDM baseline

---

## 🐛 Known Issues

See [STATUS.md](STATUS.md) for current known issues:
- C-Hubble function numerical overflow (minor)
- Compiler warnings for unused variables (trivial)

---

## 📝 Commit Message Guidelines

Use clear, descriptive commit messages:

```
Type: Brief description

Detailed explanation if needed.

- Bullet points for multiple changes
- Reference issues with #123
```

Types:
- `Fix:` Bug fixes
- `Feature:` New features
- `Docs:` Documentation
- `Test:` Tests
- `Refactor:` Code refactoring
- `Build:` Build system changes

---

## 🎓 Scientific Review

All scientific contributions will be reviewed for:
1. **Theoretical consistency** with SDGFT
2. **Mathematical correctness**
3. **Numerical accuracy**
4. **Observational validity**

---

## 📧 Contact

- **GitHub Issues**: For bugs and features
- **Discussions**: For questions and ideas
- **Email**: cosmologicmind@github.com

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Acknowledgments

Contributors will be acknowledged in:
- CONTRIBUTORS.md file
- Paper acknowledgments (for significant contributions)
- Release notes

---

Thank you for helping advance the GTT Blotzman Code! 🚀
