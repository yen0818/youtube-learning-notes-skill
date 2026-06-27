# Publishing to GitHub

This folder is already initialized as a Git repository on the `main` branch.

## Option 1: Create and push with GitHub CLI

Install and authenticate:

```bash
brew install gh
gh auth login
```

Create the GitHub repository and push:

```bash
gh repo create youtube-learning-notes-skill --public --source . --remote origin --push
```

Use `--private` instead of `--public` if you do not want the repository to be public.

## Option 2: Push to an existing GitHub repository

Create an empty repository on GitHub, then run:

```bash
git remote add origin git@github.com:OWNER/youtube-learning-notes-skill.git
git push -u origin main
```

Replace `OWNER` with your GitHub username or organization.

## Before making it public

Pick a license if you want others to have clear permission to reuse or modify the skill. The current README intentionally leaves the license undecided.
