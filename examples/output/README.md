# Example Output Files

This directory contains example output files generated from the [Exchangeability](https://github.com/cameronfreer/exchangeability) project - a Lean 4 formalization of probability theory, exchangeability, and de Finetti's theorem.

## Files

### Dependency Graph Formats

- **`exchangeability.json`** (143KB)
  - Machine-readable JSON format
  - Contains full metadata: declarations, modules, kinds, axioms, etc.
  - Used for verification and analysis
  - Can be loaded into the interactive viewer

- **`exchangeability.dot`** (125KB)
  - GraphViz DOT format
  - Can be rendered with `dot -Tsvg exchangeability.dot -o output.svg`
  - Or viewed in tools like VS Code with GraphViz extension

- **`exchangeability.svg`** (543KB)
  - Scalable Vector Graphics format
  - Open in any browser or SVG viewer
  - Zoomable without quality loss
  - Good for embedding in documentation

- **`exchangeability.png`** (6.7MB)
  - Raster image format
  - High resolution rendering of the full graph
  - Use for presentations or printing

### Interactive Viewer

- **`exchangeability-embedded.html`** (162KB)
  - Standalone HTML file with data embedded
  - No external dependencies required
  - Open directly in any browser
  - Fully interactive: filtering, search, details on click
  - [View Live Example](https://cameronfreer.github.io/LeanDepViz/example-exchangeability.html)

## About the Exchangeability Project

The example data comes from a formalization of:
- Probability measure theory
- Exchangeable sequences
- De Finetti's theorem (representation via L² convergence)
- Tail σ-algebras and ergodic theory

**Statistics**:
- ~800 declarations (theorems and definitions)
- Modules: Probability, DeFinetti, Ergodic, Tail, Util
- Dependencies: Mathlib probability theory, measure theory

**GitHub**: https://github.com/cameronfreer/exchangeability

## Generating Your Own

To generate similar output for your Lean project:

```bash
# Add LeanDepViz to your lakefile.lean
lake update LeanDepViz
lake build depviz

# Generate all formats
lake exe depviz --roots YourProject \
  --json-out yourproject.json \
  --dot-out yourproject.dot \
  --svg-out yourproject.svg \
  --png-out yourproject.png

# Create embedded HTML
python .lake/packages/LeanDepViz/scripts/embed_data.py \
  --depgraph yourproject.json \
  --output yourproject-embedded.html
```

## Viewing the Interactive HTML

**Option 1**: Open locally
```bash
open exchangeability-embedded.html
```

**Option 2**: View the hosted version
Visit: https://cameronfreer.github.io/LeanDepViz/example-exchangeability.html

**Features**:
- Browse all 800+ declarations
- Filter by module, kind, status
- Search by name
- See axiom usage
- Click any declaration for details

## File Sizes

| Format | Size | Use Case |
|--------|------|----------|
| JSON | 143KB | Analysis, verification, viewer input |
| DOT | 125KB | Source format, tools, custom rendering |
| SVG | 543KB | Web embedding, scalable viewing |
| PNG | 6.7MB | High-res images, presentations |
| HTML | 162KB | Self-contained interactive viewer |

## Notes

- The PNG file is large due to high resolution (suitable for ~800 nodes)
- SVG is recommended for web use (smaller, scalable)
- Interactive HTML is the most user-friendly for exploration
- JSON is required for verification workflows with LeanParanoia
