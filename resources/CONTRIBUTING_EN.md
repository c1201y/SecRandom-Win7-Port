# Contributing Guidelines

❤️ Thank you for contributing to SecRandom! You can contribute to the SecRandom project in various ways, including but not limited to reporting bugs, submitting feature requests, and contributing code. Please read the following guidelines before contributing.

**Language** [ [简体中文](../CONTRIBUTING.md) | **✔English** | [繁體中文](./CONTRIBUTING_ZH_TW.md) ]

> The Readme you are currently reading is **translated by AI** and reviewed by our developers. If you find any errors, please report it.

## Reporting Bugs

If you encounter a bug while using SecRandom, you can report it in GitHub Issues.

**Please strictly follow the requirements and examples in the Issues template when filling out the relevant fields**, otherwise developers may find it difficult to diagnose the issue you're experiencing.

## Submitting Feature Requests

If you have ideas for new features for SecRandom, please submit a feature request in GitHub Issues.

## Contributing Code

Before contributing code to SecRandom, please read the following guidelines.

### Technology Stack

Understanding the project's technology stack will help you get started faster:

| Category | Technology/Tool | Purpose |
|----------|----------------|---------|
| Programming Language | Python 3.13.5 | Main development language of the project |
| Package Manager | uv | Dependency management and virtual environment creation |
| UI Framework | PySide6 + PyQt-Fluent-Widgets | Modern desktop application interface development |
| Log Management | loguru | Efficient logging |
| Data Processing | numpy & pandas | Data processing and analysis |
| Text-to-Speech | edge-tts | Text-to-speech functionality |
| Excel Processing | openpyxl | Excel file import/export |
| Security Authentication | pyotp | Two-factor authentication |

### Setting Up the Development Environment

#### 1. Prerequisites

Ensure your system has the following software installed:

- Python 3.13.5
- Git
- uv package manager ([Installation Guide](https://docs.astral.sh/uv/getting-started/))

#### 2. Preparation

1. **Fork the Project**
   - Visit the [SecRandom GitHub Repository](https://github.com/SECTL/SecRandom)
   - Click the "Fork" button in the upper right corner to create your own copy of the repository

2. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/SecRandom.git
   cd SecRandom
   ```

3. **Add Upstream Repository**

   ```bash
   git remote add upstream https://github.com/SECTL/SecRandom.git
   ```

#### 3. Install Dependencies

Use uv to install project dependencies:

```bash
uv sync
```

#### 4. Run the Project

After installing dependencies, you can run the project directly:

```bash
uv run main.py
```

#### 5. C# IPC Development

You need .NET 9.0 to generate Python stubs for .NET assemblies (for IDE hints). If you choose to forgo IDE hints, installing .NET 9.0 is unnecessary.
The assemblies are located in the `data/dlls` directory. Below is the stub generation method:

```bash
powershell ./scripts/generate-stubs.ps1
```

If you are using a Linux distribution, please first install [PowerShell 7](https://github.com/PowerShell/PowerShell), and replace `powershell` with `pwsh` in the command above.

### Contribution Guidelines

**Features you contribute to SecRandom must follow these guidelines:**

- **Stable**: Your contributed features should work as stably as possible.
- **Versatile**: Your contributed features should be for most users.
- **Add switches for radical features**: If your contributed feature is relatively radical, please add a feature switch and disable it by default.
- **Functional**: Before submitting a patch, please test locally to ensure your implemented feature works correctly.
- Try not to submit patches that only contain text fixes.

### Patch Quality

As the project scales, some users have submitted low-quality patches. These patches either fail to implement the expected functionality completely or can't even compile, wasting developers' time and energy on code review and issue troubleshooting. We accept patches with flaws, **but we hope your patches meet at least the following requirements before submission:**

- The implemented functionality works; please test the patch on your local machine at least once before submission to ensure it works correctly.
- We do not recommend fully using generative AI to implement features you want to contribute without human intervention.

If you continue to submit low-quality patches, we may restrict you from continuing to submit patches to this project/organization.

### Branches and Development Cycle

The SecRandom code repository currently has the following branches:

- `master`: Main development branch of SecRandom.

When starting the next version of SecRandom, the current main branch will be forked to the corresponding maintenance branch. During the development of the next version of SecRandom, features of the current stable version will also be maintained in parallel on the maintenance branch.

Since code interfaces may differ between different development branches, **you need to choose different base branches based on the type of contribution you're making.**

**The following types of contributions are recommended to be based on the current maintenance branch:**

- Fixing bugs in stable versions
- Minor optimizations to features in stable versions

**The following types of contributions are recommended to be based on `master`:**

- Adding new features
- Refactoring code
- Other contributions that make significant changes to SecRandom
- Modifying documentation such as README

### Commits

When committing to this code repository, please try to follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

### Merging Changes

Before merging, please test your contributed code to ensure it works stably.

You can submit a [Pull Request](https://github.com/SECTL/SecRandom/pulls) to this project to merge your changes. When submitting a Pull Request, please briefly describe the changes you made and preferably include demo screenshots/videos of the features you implemented.

### Actions Build Workflow

The SecRandom project uses GitHub Actions for automated building and publishing, with the configuration file located at `.github/workflows/build-unified.yml`.

#### Triggering Builds

You can trigger builds in the following ways:

1. **Commit Message Trigger**:
   - Include the keyword `开始打包` (Start Packaging) in the commit message
   - Example: `git commit -m "Add new feature 开始打包"`

---

Thank you for your support and contributions to the SecRandom project! Let's build a better fair random selection system together! 🚀
