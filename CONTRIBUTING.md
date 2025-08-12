# Contributing to Risk Field Model Python

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Branch Strategy

```
main                    # Stable releases (v0.1.0, v0.2.0, ...)
├── develop             # Development main branch, integration testing
├── feature/highd       # highD dataset integration branch  
├── feature/round       # rounD dataset integration branch
├── feature/llm-api     # LLM API integration branch
├── feature/cuda        # CUDA parallel computing branch
├── hotfix/v0.1.x       # v0.1 version hotfix branch
└── docs/update         # Documentation update branch
```

## Pull Request Process

1. Fork the repo and create your branch from `develop`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/your-username/risk-field-model-python/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/your-username/risk-field-model-python/issues/new).

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Use a Consistent Coding Style

* Use PEP 8 for Python code
* Use Google-style docstrings for function documentation
* Include unit tests for new functionality
* Use conventional commits for commit messages

Example commit message:
```
feat: add highD dataset integration

- Implement HighDDataLoader class
- Add data preprocessing pipeline
- Include unit tests for data loading
- Update documentation

Closes #123
```

## Code Review Process

The core team looks at Pull Requests on a regular basis. After feedback has been given we expect responses within two weeks. After two weeks we may close the pull request if it isn't showing any activity.

## Community and Behavioral Expectations

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

Ready to contribute? Here's how to set up the project for local development:

1. Fork the repo on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/risk-field-model-python.git
   cd risk-field-model-python
   ```
3. Create a branch for local development:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
5. Make your changes locally.
6. Run tests:
   ```bash
   python -m pytest tests/
   python macbook_optimized.py  # Functional test
   ```
7. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```
8. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
9. Submit a pull request through GitHub.

## Development Priorities

### Current Focus (v0.1.x)
- Bug fixes and stability improvements
- Documentation enhancements
- Performance optimizations
- Code quality improvements

### Next Version (v0.2.0)
- highD dataset integration
- rounD dataset integration  
- Data preprocessing pipeline
- Batch scenario testing

### Future Versions
- AI/LLM integration (v0.3.0)
- CUDA acceleration (v0.4.0)
- Production deployment (v1.0.0)

## Questions?

Don't hesitate to reach out! You can:
- Open an issue with the `question` label
- Start a discussion in GitHub Discussions
- Contact the maintainers directly

Thank you for contributing! 🎉
