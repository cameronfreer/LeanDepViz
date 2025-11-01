# Pushing LeanDepViz to GitHub

## Using GitHub CLI (gh)

Run these commands from the LeanDepViz directory:

```bash
# Create a new repository on GitHub
gh repo create LeanDepViz --public --source=. --remote=origin --description="Dependency visualization and verification for Lean 4 projects"

# Push the code
git push -u origin main
```

## Alternative: Manual Setup

If you prefer to create the repo manually:

1. Go to https://github.com/new
2. Create a new repository named `LeanDepViz`
3. Don't initialize with README (we already have one)
4. Then run:

```bash
git remote add origin https://github.com/[your-username]/LeanDepViz.git
git push -u origin main
```

## After Pushing

Update the README.md to replace `[username]` with your actual GitHub username in the installation instructions.

## Next Steps

See `UPDATE_EXCHANGEABILITY.md` for instructions on updating your exchangeability repo to use LeanDepViz as a dependency.
