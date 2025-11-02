# Changelog

All notable changes to LeanDepViz will be documented in this file.

## [0.2.1] - 2024-11-01

### Fixed
- **Critical: Graph View now works!** Switched from CDN to vendored libraries
- Libraries now loaded from `vendor/` directory (same-origin)
- Eliminates CORS, CSP, and CDN reliability issues
- No more "d3.graphviz is undefined" errors

### Added
- `viewer/vendor/` directory with bundled libraries:
  - d3.min.js (v7.9.0, 273KB)
  - graphviz.umd.js (v2.20.0, 716KB)
  - d3-graphviz.min.js (v5.6.0, 744KB)
- `docs/vendor/` copy for GitHub Pages
- CDN fallback if vendor files fail to load

### Changed
- Script loading: vendor/ → CDN fallback (was: CDN only)
- Console message: "vendored assets" instead of CDN
- Success message: "✅ SUCCESS: All libraries loaded from vendor/"

**Why this matters**: Same-origin loading eliminates:
- ❌ CDN downtime/blocking
- ❌ Cross-origin security issues  
- ❌ Content Security Policy problems
- ❌ Network-dependent loading
- ✅ Reliable, fast, offline-capable!

## [0.2.0] - 2024-11-01

### Added
- **Verification status now shows error details inline** in table view
- Error messages displayed directly under "✗ Fail" badge
- Example: "Uses disallowed axioms: bad_axiom"
- Table header changed to "Verification Status" for clarity

### Changed
- Status column now multi-line: badge + error message
- Error text in red color (0.85em font size) for readability
- Better UX: See why something failed without clicking

**Example Display**:
```
✗ Fail
Uses disallowed axioms: bad_axiom
```

**Why this matters**: Users can immediately see WHY something failed without needing to click for details!

## [0.1.9] - 2024-11-01

### Changed
- All library CDNs switched to jsDelivr for consistency and reliability
- Added crossorigin="anonymous" to all library script tags
- Added explicit final library verification script with diagnostic logging
- Automatic fallback: if d3.graphviz fails to attach, tries unpkg as backup

### Added
- Final verification script that runs after all libraries
- Logs complete library status: d3, d3.select, d3.graphviz, hpccWasm
- Manual reload fallback if d3-graphviz doesn't attach
- More detailed error messages for debugging

**Debugging**: Open console and look for "=== Final library check ===" to see exactly what loaded

## [0.1.8] - 2024-11-01

### Fixed
- **Critical**: d3-graphviz library loading - moved scripts to end of <body>
- Scripts now load AFTER DOM is ready, ensuring proper initialization
- Switched d3-graphviz to unpkg for consistency (all libs from unpkg/jsDelivr)
- Using non-minified d3-graphviz.js for better compatibility

### Changed
- Library scripts moved from <head> to end of <body> tag
- Execution order: DOM loads → user scripts run → library scripts load → d3.graphviz attaches
- This ensures window.d3 is fully initialized before d3-graphviz tries to extend it

**Why this matters**: Graph View should finally work! Previous versions had timing issues where d3-graphviz tried to attach before D3 was ready.

## [0.1.7] - 2024-11-01

### Fixed
- **Mobile layout**: Sidebar now appears below content on narrow screens (< 768px) instead of overlapping
- **Embedded file status**: File inputs now show "✓ Embedded data loaded" instead of "No file chosen" when data is embedded
- Better responsive design with flex-wrap on stats and proper mobile breakpoints

### Changed
- Sidebar switches from side-by-side to stacked layout on mobile
- Maximum sidebar height on mobile: 300px with scroll
- File input status indicators added next to each file input
- Status updates automatically on page load for embedded demos

**Why this matters**: Embedded examples now clearly show what data is preloaded, and mobile users can actually see the content!

## [0.1.6] - 2024-11-01

### Fixed
- **Critical**: Fixed d3-graphviz library loading issues on GitHub Pages
- Switched to pinned, stable CDN versions (jsDelivr + unpkg)
- Updated D3 to v7.9.0, @hpcc-js/wasm to v2.20.0
- Proper script loading order: D3 first, then WASM, then d3-graphviz
- Changed from `load` event to `DOMContentLoaded` for better timing
- Added robust library presence check: `window.d3 && d3.graphviz && typeof d3.graphviz === 'function'`
- Better error messages with diagnostic info

### Changed
- Script tags now use `defer` attribute for proper async loading
- WASM script uses `type="application/javascript"` (UMD mode)
- Improved console logging with detailed library status

**Why this matters**: Graph View now actually works! Previous versions had CDN/timing issues causing "d3.graphviz is not a function" errors.

## [0.1.5] - 2024-11-01

### Changed
- **Rebranded**: "LeanDepViz + LeanParanoia Viewer" → "LeanDepViz"
- Version number now visible in header (v0.1.5)
- Version logged to console on page load
- LeanParanoia positioned as optional feature, not primary

### Fixed
- Updated CDN libraries for better graph view compatibility
- Better error messages when libraries fail to load
- Download button for embedded DOT data when rendering fails

## [0.1.4] - 2024-11-01

### Added
- DOT file embedding support in standalone HTML
- Both Table View and Graph View work without file uploads

### Changed
- Updated embed_data.py to support --dot parameter
- Example output now includes graph view functionality

## [0.1.3] - 2024-11-01

### Added
- Graph View with interactive d3-graphviz rendering
- Tab interface to switch between Table View and Graph View
- Zoom and pan support for large graphs
- DOT file loading

### Changed
- Viewer now has two modes instead of one
- Enhanced UI with tabbed interface

## [0.1.2] - 2024-11-01

### Added
- Summary-only mode for paranoia runner (--summary-only flag)
- Dramatically reduced report sizes (5GB → 64KB)

### Changed
- Error summaries extracted automatically
- Limited stdout/stderr capture to prevent huge files

### Fixed
- LeanParanoia reports now usable for large projects

## [0.1.1] - 2024-11-01

### Added
- Initial paranoia_runner.py script
- Policy-based verification support
- Example policy files (standard, dev, strict)

## [0.1.0] - 2024-11-01

### Added
- Initial release of LeanDepViz
- Dependency graph extraction for Lean 4 projects
- JSON, DOT, SVG, PNG output formats
- Interactive HTML viewer
- Smart filtering by project modules
- Metadata: sorry flags, axioms, unsafe declarations
- GitHub Pages hosting
- Example outputs from Exchangeability project

### Features
- Filter graphs to project modules only
- Multiple output formats
- Interactive viewer with filtering and search
- Edge consistency (auto-filters edges for surviving nodes)
- Metadata extraction without external verification tools
