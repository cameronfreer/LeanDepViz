# Vendored JavaScript Libraries

This directory contains third-party JavaScript libraries bundled with LeanDepViz to ensure reliable same-origin loading on GitHub Pages.

## Why Vendored?

**Problem**: Loading libraries from CDNs (jsdelivr, unpkg, etc.) caused issues:
- CORS (Cross-Origin Resource Sharing) restrictions
- Content Security Policy (CSP) blocking
- CDN downtime or blocking
- Network-dependent reliability

**Solution**: Bundle libraries locally and serve from same origin (GitHub Pages)
- ✅ No cross-origin issues
- ✅ No CSP problems
- ✅ Works offline (once loaded)
- ✅ Consistent, reliable loading

## Libraries

### d3.min.js
- **Version**: 7.9.0
- **Size**: 273KB
- **Source**: https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js
- **License**: ISC
- **Purpose**: Data visualization library, required for graph rendering

### graphviz.umd.js
- **Version**: 2.20.0  
- **Size**: 716KB
- **Source**: https://unpkg.com/@hpcc-js/wasm@2.20.0/dist/graphviz.umd.js
- **License**: Apache-2.0
- **Purpose**: GraphViz WASM for graph layout computation

### d3-graphviz.min.js
- **Version**: 5.6.0
- **Size**: 744KB
- **Source**: https://cdn.jsdelivr.net/npm/d3-graphviz@5.6.0/build/d3-graphviz.min.js
- **License**: BSD-3-Clause
- **Purpose**: D3 plugin for rendering GraphViz DOT graphs

## Total Size

~1.7MB total (acceptable for modern web, loaded once and cached)

## Usage

The viewer HTML loads these in order:

```html
<script src="vendor/d3.min.js"></script>
<script src="vendor/graphviz.umd.js"></script>
<script src="vendor/d3-graphviz.min.js"></script>
```

## Updating

To update to newer versions:

```bash
cd viewer/vendor/

# Update D3
curl -sL https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js > d3.min.js

# Update WASM
curl -sL https://unpkg.com/@hpcc-js/wasm@2/dist/graphviz.umd.js > graphviz.umd.js

# Update d3-graphviz
curl -sL https://cdn.jsdelivr.net/npm/d3-graphviz@5/build/d3-graphviz.min.js > d3-graphviz.min.js

# Copy to docs/ for GitHub Pages
cp -r ../vendor ../../docs/

# Test locally
cd ../..
open docs/index.html

# Regenerate embedded examples
python scripts/embed_data.py ...
```

## License Compliance

All vendored libraries are open source:
- **D3**: ISC License (permissive, allows bundling)
- **@hpcc-js/wasm**: Apache-2.0 (permissive, allows bundling)
- **d3-graphviz**: BSD-3-Clause (permissive, allows bundling)

Full license texts available in original repositories:
- https://github.com/d3/d3
- https://github.com/hpcc-systems/hpcc-js-wasm
- https://github.com/magjac/d3-graphviz
