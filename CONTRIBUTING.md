# Contributing to AI Article Summarizer

First off, thank you for considering contributing to this project! Your help is greatly appreciated. This document provides guidelines for contributing to the project.

## How to Contribute

-   **Reporting Bugs**: If you find a bug, please open an issue. Include a clear title, a detailed description of the bug, steps to reproduce it, and the expected behavior.
-   **Suggesting Enhancements**: If you have an idea for an improvement, open an issue with a clear title and a detailed description of your suggestion and why it would be beneficial.
-   **Pull Requests**: If you want to contribute code, please follow these steps:
    1.  Fork the repository.
    2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name` or `bugfix/your-bug-fix`).
    3.  Make your changes and commit them with a clear and descriptive commit message.
    4.  Ensure your code passes all tests by running `python -m pytest tests/`.
    5.  Ensure your code adheres to the project's coding style by running `ruff check .` and `black .`.
    6.  Push your changes to your forked repository.
    7.  Open a pull request to the `develop` branch of the main repository.

## Coding Style

Please adhere to the existing code style. This project uses `ruff` for linting and `black` for code formatting. Ensure your code passes checks from both tools before submitting a pull request.

## Docker

If you are developing with Docker, you can build the image using `docker build -t article-summarizer .` and run tests within the container.

## Questions?

If you have any questions, feel free to open an issue and ask.