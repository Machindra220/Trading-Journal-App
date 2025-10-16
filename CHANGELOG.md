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

## [v1.3.0] - 2025-10-04
### Added
- Register and Login Page modified with alternate options
- Users table id query updated in schema
- Modified navigation bar collapsible for mobile for screens less than 768px
- Added Stats charts for Profit/Loss by Date, week and Monthly bars
- Corrected Remaining quantity after partial exits, Realized PnL after Partial Exit, corrected invested amount for remaining quantity. 
- On Dashboard Page added remaining quantity column in the table, added visual indicator for partial exits

## [v1.3.0] - 2025-10-04
### Added
- Menu view modified, Toggle menu bug fix
- Pinned Tools Made Compact
- Dashboard page status merged to stock name
