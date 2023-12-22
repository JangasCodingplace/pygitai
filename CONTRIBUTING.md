# Contributing

Welcome! Thank you for considering contributing to PyGitAI. Your
feedback and contributions are invaluable to us!

**Table of Contents**

- [Reporting Issues and Bugs](#reporting-issues-and-bugs)
- [Feature Requests and Feedback](#feature-requests-and-feedback)
- [Contributing Code](#contributing-code)
    - [Prerequisites for Contributing Code](#prerequisites-for-contributing-code)
    - [Submitting a Pull Request](#submitting-a-pull-request)
    - [Contributing to the Documentation](#contributing-to-the-documentation)
- [Maintainers](#maintainers)
- [Preferred communication language](#preferred-communication-language)


<a href="#reporting-issues-and-bugs"></a>
## Reporting Issues and Bugs

If you encounter any bugs or issues with PyGitAI, please report them
on the [issue tracker](https://github.com/JangasCodingplace/pygitai/issues).
Please include as much information as possible, including:

- **Title**: A short, descriptive title for the issue.
- **Reproducibility**: Describe the exact steps to reproduce the
    problem in as much detail as possible.
- **Observed Behavior**: Describe the behavior you observed and what
    makes it a problem.
- **Expected Behavior**: Explain which behavior you expected to see
    instead and why.
- **Versions**: Include Python and PyGitAI versions. Also, confirm if
    the issue persists in the latest version of PyGitAI.
- **Additional Context**: Logs, error messages, or screenshots are
    often very helpful.

After you submit an issue, we aim to review and respond as soon as
possible. If you don't receive a response within a few days, feel
free to add a new comment to the thread to bring it to our attention
again.


<a href="#feature-requests-and-feedback"></a>
## Feature Requests and Feedback

If you have a feature request or feedback, feel free to submit them
to the [issue tracker](https://github.com/JangasCodingplace/pygitai/issues).
When submitting your issue, it helps to provide:

- **Title**: Write a simple and descriptive title to identify your
    suggestion.
- **Description**: Provide as many details as possible. Explain your
    context and how you envision the feature working.
- **Usefulness**: Explain why this feature or improvement would be
    beneficial.
- **Scope**: Keep the scope of the feature narrow to make it easier
    to implement. For example, focus on a specific use-case rather
    than a broad feature set.


<a href="#contributing-code"></a>
## Contributing Code

We welcome contributions to PyGitAI! If you'd like to contribute
code, please follow the guidelines below.

<a href="#prerequisites-for-contributing-code"></a>
### Prerequisites for Contributing Code

**For code contributions**: make sure you have the following
installed:

- Python 3.10 or higher
- Poetry
- pre-commit

**For documentation contributions**: No specific prerequisites are
required. But follow installations are recommended for a better
experience:

- Python 3.10 or higher
- Poetry
- mkdocs, mkdocstrings and mkdocs-material

For either type of contribution it's recommended to observe the
pyproject.toml file for the exact versions of the dependencies.


<a href="#submitting-a-pull-request"></a>
### Submitting a Pull Request
If you'd like to submit a pull request (PR), follow these steps:

1. Fork the repository and clone it locally.
2. Install development tools with `poetry install`.
3. Set up the pre-commit hooks with `poetry run pre-commit install`.
4. Create a new branch for your PR. Target the `main` branch of the
    original repository.
5. Follow [PEP 8](https://pep8.org/) for code style and formatting.
6. Follow [NumPy style](https://numpydoc.readthedocs.io/en/latest/format.html)
    for docstrings.
7. Use Black for code formatting. It will be executed automatically
    by the pre-commit hooks.
8. Write tests for your code. Make sure they pass with
    `poetry run pytest`.
9. Update the documentation if necessary.
10. Commit your changes and push your branch to GitHub.

After submitting, your pull request will be reviewed. If you don't
hear back within a few days, feel free to add a comment to the pull
request to draw our attention.


<a href="#contributing-to-the-documentation"></a>
### Contributing to the Documentation

The documentation is written in Markdown and built with mkdocs. The
documentation is located in the `docs` directory. The documentation
is automatically built and deployed to GitHub Pages when a new
release is published.

To observe the documentation locally, run `poetry run mkdocs serve`.
The documentation will be available at http://localhost:8000 in your
browser.


<a href="#maintainers"></a>
## Maintainers
At present, PyGitAI is maintained by

- JangasCofingplace [@JangasCodingplace](https://github.com/JangasCodingplace)


<a href="#preferred-communication-language"></a>
## Preferred communication language

The preferred communication language is English.
