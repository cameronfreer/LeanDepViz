# Changelog

All notable changes to LeanDepViz will be documented in this file.

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
