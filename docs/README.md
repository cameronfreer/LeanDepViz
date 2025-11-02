# LeanDepViz Interactive Viewer

This is the hosted version of the LeanDepViz interactive viewer.

## Live Demo

**View the tool**: [https://cameronfreer.github.io/LeanDepViz/](https://cameronfreer.github.io/LeanDepViz/)

**Example output**: [Exchangeability Project Dependencies](https://cameronfreer.github.io/LeanDepViz/example-exchangeability.html) - See a real-world example of dependency analysis from a probability theory formalization project

## How to Use

The viewer has **two modes**: Table View and Graph View

### Table View
1. Visit the URL above
2. Click "Choose File" next to "Dependency Graph" and select your `depgraph.json`
3. (Optional) Click "Choose File" next to "Paranoia Report" and select your `paranoia_report.json`
4. Explore your project's dependencies with filters and search

### Graph View
1. Click the "🕸️ Graph View" tab
2. Click "Choose File" next to "DOT File" and select your `graph.dot`
3. Interact with the visual graph (zoom, pan, explore)
4. Switch back to Table View for detailed information on any declaration

## Privacy

- **All processing happens in your browser** - no data is sent to any server
- Your JSON files never leave your computer
- The viewer works offline once loaded

## Generating Your Data Files

In your Lean project:

```bash
# Add LeanDepViz to your lakefile.lean
lake update LeanDepViz
lake build depviz

# Generate dependency graph
lake exe depviz --roots YourProject --json-out depgraph.json

# (Optional) Run verification
python .lake/packages/LeanDepViz/scripts/paranoia_runner.py \
  --depgraph depgraph.json \
  --policy your-policy.yaml \
  --out paranoia_report.json
```

## Embedding Your Results

To create a standalone HTML file with your data embedded (for sharing):

```bash
python .lake/packages/LeanDepViz/scripts/embed_data.py \
  --depgraph depgraph.json \
  --report paranoia_report.json \
  --output my-project-report.html
```

Then you can:
- Open `my-project-report.html` directly in a browser
- Share the file with colleagues
- Host it on GitHub Pages, Vercel, Netlify, etc.

## Source Code

Full documentation and source code: [https://github.com/cameronfreer/LeanDepViz](https://github.com/cameronfreer/LeanDepViz)
