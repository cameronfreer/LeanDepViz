# Updating Your Project to Use LeanDepViz

This guide shows how to update the exchangeability repository (or any Lean project) to use LeanDepViz as a dependency instead of having the code embedded.

## Steps for Exchangeability Repo

### 1. Update lakefile.lean

Replace the local DepViz library with the LeanDepViz dependency.

**Before:**
```lean
lean_lib «DepViz» where
  -- auxiliary tooling for dependency visualization

lean_exe depviz where
  root := `DepViz.Main
  supportInterpreter := true
```

**After:**
```lean
require LeanDepViz from git
  "https://github.com/[username]/LeanDepViz.git" @ "main"
```

(Replace `[username]` with your GitHub username)

### 2. Remove Local Files

Delete the local DepViz directory and related files:

```bash
cd ~/work/exch-repos/exchangeability-windsurf

# Remove local DepViz code (now comes from dependency)
rm -rf DepViz/

# Remove documentation that's now in LeanDepViz repo
rm PARANOIA_INTEGRATION.md
rm INTEGRATION_SUMMARY.md
rm README_PARANOIA.md

# Remove example policies (keep your customized one)
rm depviz-policy-dev.yaml
rm depviz-policy-strict.yaml
# Keep depviz-policy.yaml if you've customized it for your project

# Remove scripts and viewer (will use from dependency)
rm -rf scripts/
rm -rf viewer/
```

### 3. Update Your Policy File

Keep `depviz-policy.yaml` but update it to use Exchangeability-specific module names:

```yaml
zones:
  - name: "Probability Core"
    include:
      - "Exchangeability.Probability.**"
    # ... rest of your configuration
```

### 4. Update Lake Dependencies

```bash
lake update LeanDepViz
lake build depviz
```

### 5. Usage (Nothing Changes!)

The commands remain the same:

```bash
# Generate graph
lake exe depviz --roots Exchangeability --json-out depgraph.json

# Run paranoia checks
python .lake/packages/LeanDepViz/scripts/paranoia_runner.py \
  --depgraph depgraph.json \
  --policy depviz-policy.yaml \
  --out paranoia_report.json \
  --jobs 8

# Copy viewer if needed
cp .lake/packages/LeanDepViz/viewer/paranoia-viewer.html ./
open paranoia-viewer.html
```

### 6. Optional: Create Convenience Scripts

Create `scripts/check-paranoia.sh` in your repo:

```bash
#!/bin/bash
set -e

echo "Generating dependency graph..."
lake exe depviz --roots Exchangeability --json-out depgraph.json

echo "Running paranoia checks..."
python .lake/packages/LeanDepViz/scripts/paranoia_runner.py \
  --depgraph depgraph.json \
  --policy depviz-policy.yaml \
  --out paranoia_report.json \
  --jobs "$(sysctl -n hw.ncpu 2>/dev/null || nproc)"

echo "Done! Open viewer/paranoia-viewer.html to see results."
```

Make it executable:
```bash
chmod +x scripts/check-paranoia.sh
```

### 7. Update .gitignore

Your .gitignore already has the right patterns for generated files, so no changes needed.

### 8. Commit Changes

```bash
git add lakefile.lean depviz-policy.yaml
git commit -m "Refactor: Use LeanDepViz as external dependency

- Removed local DepViz code (now from github.com/[username]/LeanDepViz)
- Kept project-specific policy configuration
- Usage remains the same via lake exe depviz"

git push origin depviz
```

## Benefits

✅ **Reusable**: LeanDepViz can be used by other Lean projects
✅ **Versioned**: Pin to specific commits or use latest
✅ **Maintained separately**: Issues and PRs in LeanDepViz repo
✅ **Cleaner**: exchangeability repo only has project-specific config
✅ **Same workflow**: No changes to how you use the tool

## Updating LeanDepViz Later

To get the latest version:

```bash
lake update LeanDepViz
lake build depviz
```

## Pinning to a Specific Version

To pin to a specific commit:

```lean
require LeanDepViz from git
  "https://github.com/[username]/LeanDepViz.git" @ "abc1234"
```

Replace `abc1234` with the commit SHA or tag.
