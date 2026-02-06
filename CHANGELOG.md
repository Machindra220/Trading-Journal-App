# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2026-02-06
### Added
- [cite_start]**Dual-Metric Visuals**: Updated the Statistics Dashboard to show Profit/Loss in both absolute value (₹) and percentage (%).
- [cite_start]**Interactive Equity Curve**: Added automated growth percentage calculations on the Equity Curve relative to the chart's starting point[cite: 13, 14].
- [cite_start]**Enhanced Tooltips**: Implemented custom Chart.js callbacks to display detailed P&L data on hover for Daily, Weekly, and Monthly bar charts[cite: 18, 24, 30].

### Changed
- [cite_start]**Data Alignment**: Refactored chart logic to utilize the `return_pct` field, ensuring consistency between the Trade History records and visual analytics[cite: 49, 50].

## [1.6.0] - 2025-10-28
### Added
- **Stage 2 Delivery Screener**: New tool to screen stocks with delivery spikes ≥ 3x from Stage 2 entries.
- **Persistence Layer**: Created `stage2_delivery_stock` table to store daily screener results with a 30-day retention policy.
- **Screener History**: New page to list and filter saved records from the past 30 days.
- **UI Enhancements**: Added copy-to-clipboard buttons for stock symbols and tooltips for all sidebar navigation links.

### Changed
- **Sorting & Filtering**: Implemented multi-field sorting (Volume, ROC, RS vs Index) and symbol-based filtering in screeners.

## [1.5.0] - 2025-10-18
### Added
- **Market Scanning**: Added Top 20 Performers lists for NSE 200, NSE 500, and BSE 200.
- **Incomplete Trades**: Tracking for trades missing buy or sell entry data.
- **Sector Analysis**: Added screeners for Sectorwise Stage 2 stocks.
- **Navigation**: Implemented a collapsible vertical sidebar navigation menu.

## [1.4.0] - 2025-10-16
### Changed
- **UI Refinement**: Redesigned the navigation bar for better responsiveness and anchored branding.
- **Layout Optimization**: Global transition to a flexbox-based layout with a sticky footer and improved mobile menu toggles.
- **Styling**: Enhanced hover/active states and spacing for pinned resources using Tailwind UI.

## [1.3.0] - 2025-10-04
### Added
- [cite_start]**Performance Charts**: Added visual Profit/Loss bars for daily, weekly, and monthly timeframes[cite: 10, 15, 21, 27].
- **Partial Exit Logic**: Corrected calculations for remaining quantity, realized P&L, and invested amounts after partial exits.
- **Dashboard Indicators**: Added "Remaining Quantity" column and visual indicators for partial exits in the main trade table.

### Fixed
- Navigation menu toggle bugs and consolidated stock status views.

## [1.2.0] - 2025-09-30
### Added
- **Documentation**: Added database schema at `./app/db/schema.sql`.
- **Risk Calculator**: New tool to calculate position sizing based on investment value.
- **Consistency**: Standardized button sizing across all application pages.

## [1.1.0] - 2025-09-30
### Added
- **Trade Actions**: Integrated "View" button in trade history and unified the Apply/Export/Print layout.

### Changed
- **Delete Logic**: The delete route now supports `request.referrer` for better post-action redirection.

### Fixed
- Resolved Internal Server Errors caused by missing ID fields in enriched data dictionaries.

## [1.0.0] - 2025-09-28
### Added
- Initial public release.
- Core P&L tracking dashboard and Trade History.
- Excel/PDF export functionality with filtering.
- Watchlist, Notes, and basic performance statistics.