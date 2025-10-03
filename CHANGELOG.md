# Changelog

## v1.0 — 28-Sep-2025
- Initial public release
- Trade dashboard with P&L tracking
- Excel export with filters
- Resource pinning and last accessed tracking
- Seperate Completed Trades page
- Secure config via environment variables
- Watchlist page
- Trades history Page
- Notes page 
- Simple statistics for our trading performance tracking

## [v1.1.0] - 2025-09-30
### Added
- View button in `trade_history.html` with consistent styling
- Unified button layout for Apply / Export / Print
- Reuse of dashboard delete route for completed trades

### Changed
- `trade_history()` now includes `trade.id` for action buttons
- Redirect after delete now respects `request.referrer`

### Fixed
- Button size inconsistencies between view and delete
- Internal server error from missing `id` in enriched dictionary

## [v1.2.0] - 2025-09-30
### Added
- DB Schema is placed in ./app/db/schema.sql
- Risk calculator page according our investment value
- Button size inconsistencies updated to all pages
- Modified dashboard page table view columns