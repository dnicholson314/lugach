# LUGACH

![PyPI](https://img.shields.io/pypi/v/lugach)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lugach)](https://pypi.org/project/lugach/)

LU GA Canvas Helps (LUGACH) is a cross-platform Python CLI tool designed to
automate and streamline daily administrative tasks for Graduate Assistants (GAs)
at Liberty University. LUGACH integrates with Canvas, Top Hat, and Lighthouse,
providing a unified interface for managing student data, assignments, attendance,
and more.

**PyPI:** [https://pypi.org/project/lugach/](https://pypi.org/project/lugach/)

## Features

- Synchronize and cross-reference data between Canvas, Top Hat, and Lighthouse
- Confirm student enrollment and retrieve student emails
- Modify due dates and time limits on quizzes and assignments
- Take and update attendance records
- Identify absent students and quiz concerns
- Post final grades and search for students by name
- Securely manage authentication credentials for all platforms
- Routine update and feedback mechanisms for error reporting

## Requirements

- Python 3.12.0 or later
- [pipx](https://pypa.github.io/pipx/) (recommended for users)
- [uv](https://github.com/astral-sh/uv) (recommended for developers)
- Git (recommended for contributors)

## Installation

### For Users

Install and run LUGACH globally using
[pipx](https://pypa.github.io/pipx/):

```bash
pipx install lugach
```

After installation, run the CLI from anywhere:

```bash
lugach --help
```

### For Developers/Contributors

Clone the repository and install in editable mode with
[uv](https://github.com/astral-sh/uv):

```bash
git clone https://github.com/dnicholson314/LU-GA-Canvas-Helps.git
cd LU-GA-Canvas-Helps
uv pip install -e .
```

## Usage

Run this command for the interactive CLI:

```bash
lugach app -i
```

For information about the commands that retrieve Canvas data about courses or
students, use

```bash
lugach cv --help
```

For information about the commands that retrieve Top Hat data about courses or
students, use

```bash
lugach th --help
```

**First-time setup:**

When you first run LUGACH in interactive mode, you will see a menu like this:

```txt
    Welcome to LUGACH! Please choose one of the following options
    (or 'q' to quit):
        (1) Setup **this option here**
        (2) Identify Absent Students
        (3) Identify Quiz Concerns
        (4) Modify Due Dates
        (5) Modify Time Limits
        (6) Post Final Grades
        (7) Search Student By Name
        (8) Update Attendance Verification
        (9) Modify Attendance
```

Select **Setup** to add your authentication details for Canvas, Top Hat, and
Lighthouse. These credentials are required for the other features to
function and are stored securely using the system keyring.

> Note that WSL lacks a built-in keyring, so credentials are instead stored in
> a dotfile in the user's home directory. This is inherently insecure, so
> proceed with caution.

## Contributing

Contributions are welcome! If you have suggestions or bug reports, feel free to
open an issue or submit a pull request.
