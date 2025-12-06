# Terraform CI/CD Setup Guide

## Overview
This repository now has a complete CI/CD pipeline set up for Terraform using GitHub Actions and pre-commit hooks.

## What's Included

### 1. GitHub Actions Workflow (`.github/workflows/terraform.yml`)

The workflow runs on:
- **Push events** to `main`, `master`, or `dev` branches (when terraform files change)
- **Pull requests** to `main` or `master` (when terraform files change)
- **Manual triggers** (workflow_dispatch)

#### Jobs:

**terraform-validate**
- Runs `terraform fmt -check` to verify code formatting
- Runs `terraform init` without backend
- Runs `terraform validate` on each Terraform directory
- Runs in a matrix across all 9 Terraform project directories

**terraform-lint**
- Uses TFLint to check for best practices and potential issues
- Runs recursively on all terraform/ directory files

**terraform-security**
- Uses Trivy to scan for security vulnerabilities in Terraform configurations
- Uploads results to GitHub Security tab (SARIF format)

**terraform-plan**
- Runs on pull requests only
- Executes `terraform plan` (requires AWS credentials)
- Comments on PR with plan results
- Can automatically apply on merge (optional)

### 2. Pre-commit Hooks (`.pre-commit-config.yaml`)

Runs locally before commits to catch issues early:
- Terraform format checking (`terraform fmt`)
- Terraform validation
- TFLint linting
- Terraform docs generation
- Generic hooks (trailing whitespace, file size checks, etc.)
- ShellCheck for shell scripts

**Installation:**
```bash
pip install pre-commit
pre-commit install
```

### 3. Enhanced .gitignore

Comprehensive Terraform exclusions:
- `*.tfstate` files (never commit state)
- `.terraform/` directories
- Lock files
- `.tfvars` files (except `.example`)
- Crash logs

### 4. terraform.tfvars.example

Template for variables. Copy to `terraform.tfvars` and fill in your values:
```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform/terraform.tfvars with your values
```

## Setup Instructions

### Step 1: GitHub Actions Secrets (for AWS)

If using AWS resources, add these secrets to your GitHub repo:
1. Go to: Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secrets:
   - `AWS_ROLE_TO_ASSUME` (OIDC role ARN, optional)
   - `AWS_ACCESS_KEY_ID` (if using static credentials)
   - `AWS_SECRET_ACCESS_KEY` (if using static credentials)

**Note:** Using OIDC is recommended for better security. See [GitHub OIDC documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect).

### Step 2: Enable Pre-commit Hooks Locally

```powershell
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# (Optional) Run on all files to verify setup
pre-commit run --all-files
```

### Step 3: Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your actual values
```

### Step 4: Push to Trigger Workflow

```bash
git add .
git commit -m "Set up CI/CD pipeline"
git push origin dev
```

## Workflow Behavior

### On Push to main/master/dev
- ✅ Validates all Terraform configurations
- ✅ Runs TFLint checks
- ✅ Runs security scan with Trivy

### On Pull Request
- ✅ All validation steps above
- ✅ Creates Terraform plan
- ✅ Comments on PR with plan details

### Manual Trigger
- Use Actions tab → "Terraform CI/CD" → "Run workflow"

## Next Steps

### Optional Enhancements

1. **Automatic Apply on Merge**
   - Uncomment the `terraform-apply` job in workflow (lines 140-160)
   - Requires AWS credentials in secrets

2. **Enable TF Registry Documentation**
   - Use `terraform-docs` to auto-generate README.md for modules

3. **Cost Estimation**
   - Add Infracost integration to estimate costs before applying

4. **Approval Gates**
   - Add GitHub environments with required approvals before apply

5. **Slack/Discord Notifications**
   - Add notification step to workflow for build failures

## Local Development

### Format Code
```bash
terraform fmt -recursive terraform/
```

### Validate Configuration
```bash
cd terraform/<project>
terraform init -backend=false
terraform validate
```

### Run Linter
```bash
tflint --init
tflint --format compact --recursive terraform/
```

### Run Pre-commit Hooks
```bash
pre-commit run --all-files
```

## Troubleshooting

### Workflow Fails: "terraform init failed"
- Likely missing backend configuration
- The workflow uses `-backend=false` to skip backend during validation
- For plan/apply jobs, you need AWS credentials

### Pre-commit Hooks Fail Locally
```bash
# Install required tools
pip install pre-commit terraform-docs

# For TFLint
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

# Reinstall hooks
pre-commit install --install-hooks
```

### State File Accidentally Committed
```bash
# Remove from git history
git rm --cached terraform/**/*.tfstate
git commit -m "Remove tfstate files"
```

## Resources

- [Terraform Documentation](https://www.terraform.io/docs)
- [GitHub Actions Terraform Setup](https://github.com/hashicorp/setup-terraform)
- [TFLint Documentation](https://github.com/terraform-linters/tflint)
- [Trivy Documentation](https://github.com/aquasecurity/trivy)
- [Pre-commit Framework](https://pre-commit.com/)

---

**Created:** December 6, 2025
**Status:** Ready for use
