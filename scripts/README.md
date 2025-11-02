# LeanDepViz Scripts

Automation scripts for LeanDepViz project.

## generate_paranoia_examples.py / .sh

Automatically generates LeanParanoia example demos.

### What It Does

1. **Creates temporary Lean project** with all example files from `examples/leanparanoia-tests/`
2. **Builds the project** with Lean v4.24.0-rc1
3. **Generates dependency graph** (JSON + DOT formats)
4. **Creates verification report** (mock data showing pass/fail status)
5. **Generates embedded HTML** demo with all data embedded
6. **Copies outputs** to `docs/` and `examples/leanparanoia-tests/`

### Usage

**Python version** (recommended):
```bash
python scripts/generate_paranoia_examples.py
```

**Bash version**:
```bash
./scripts/generate_paranoia_examples.sh
```

### Adding New Examples

To add new example files to the demo:

1. **Add your `.lean` file** to `examples/leanparanoia-tests/`
   - Example: `NewExploit.lean`

2. **Update the configuration**:
   
   **In Python script** (`generate_paranoia_examples.py`):
   ```python
   EXAMPLE_FILES = [
       "Basic.lean",
       "SorryDirect.lean",
       "UnsafeDefinition.lean",
       "PartialNonTerminating.lean",
       "ValidSimple.lean",
       "NewExploit.lean",  # Add here
   ]
   ```
   
   **In Bash script** (`generate_paranoia_examples.sh`):
   ```bash
   cp "$EXAMPLES_DIR"/{Basic,SorryDirect,UnsafeDefinition,PartialNonTerminating,ValidSimple,NewExploit}.lean Examples/
   ```

3. **Add verification results** (in Python script):
   ```python
   VERIFICATION_RESULTS = [
       # ... existing results ...
       {"decl": "your_new_decl", "zone": "Examples", "ok": False,
        "kind": "thm", "module": "Examples.NewExploit", "exit": 1,
        "error": "Description of what's wrong"},
   ]
   ```

4. **Run the script**:
   ```bash
   python scripts/generate_paranoia_examples.py
   ```

5. **Commit the results**:
   ```bash
   git add docs/leanparanoia-examples-all.html examples/leanparanoia-tests/leanparanoia-examples-all.html
   git commit -m "Regenerate examples with NewExploit"
   git push
   ```

### Output

The script generates:
- `docs/leanparanoia-examples-all.html` (for GitHub Pages)
- `examples/leanparanoia-tests/leanparanoia-examples-all.html` (backup copy)

The HTML file will be available at:
https://cameronfreer.github.io/LeanDepViz/leanparanoia-examples-all.html

### Requirements

- **Lean 4.24.0-rc1** (via elan)
- **Python 3** (for Python version)
- **Bash** (for Bash version)
- **Internet connection** (to clone dependencies)
- **jq** (for Bash version, to parse JSON)

### Troubleshooting

**Build fails**:
- Check that Lean 4.24.0-rc1 is installed: `elan toolchain list`
- Try `lake clean` in your project
- Ensure all example files are syntactically correct

**Script can't find files**:
- Run from repo root: `python scripts/generate_paranoia_examples.py`
- Check that example files exist in `examples/leanparanoia-tests/`

**Output is missing declarations**:
- Verify example file is listed in `EXAMPLE_FILES`
- Check that the file builds successfully
- Ensure verification results are added for new declarations

## embed_data.py

Embeds dependency graph, DOT, and paranoia report into standalone HTML viewer.

### Usage

```bash
python scripts/embed_data.py \
  --viewer viewer/paranoia-viewer.html \
  --depgraph depgraph.json \
  --dot graph.dot \
  [--report paranoia-report.json] \
  --output standalone.html
```

### Parameters

- `--viewer`: Path to paranoia-viewer.html template
- `--depgraph`: Dependency graph JSON file (required)
- `--dot`: DOT graph file (optional but recommended)
- `--report`: Paranoia verification report JSON (optional)
- `--output`: Output HTML file path

### Example

```bash
# Generate with all data
python scripts/embed_data.py \
  --viewer viewer/paranoia-viewer.html \
  --depgraph examples/output/exchangeability.json \
  --dot examples/output/exchangeability.dot \
  --output docs/example-exchangeability.html

# Generate without paranoia report (metadata only)
python scripts/embed_data.py \
  --viewer viewer/paranoia-viewer.html \
  --depgraph myproject.json \
  --dot myproject.dot \
  --output myproject-demo.html
```

## paranoia_runner.py

Runs LeanParanoia verification on declarations based on policy zones.

### Usage

```bash
python scripts/paranoia_runner.py \
  --depgraph depgraph.json \
  --policy policy.yaml \
  [--summary-only] \
  --out paranoia_report.json
```

See `scripts/paranoia_runner.py --help` for details.

**Note**: Requires LeanParanoia to be installed and compatible with your Lean version.
