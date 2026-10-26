# Budget Tracker Mobile

An Expo React Native companion app with its own local SQLite database. It provides the same core budget flow as the desktop app:

- Separate bank and cash balances, with cash withdrawals recorded as transfers.
- Savings accounts with contribution transactions that identify bank or cash as their source, subtract contributions from that balance, count contributions against the Savings allocation, and show an aggregate saved balance on the dashboard.
- Source-specific spending and per-category monthly remaining amounts.
- Average monthly cash-added allocation across savings, guilt-free, investment, emergency fund, and needs/bills.
- Account and transaction create, edit, and delete.
- Account and transaction create/edit forms open in modal sheets from floating add buttons and row edit actions.
- Editable allocation percentages using sliders or numeric inputs, with category and tab icons.
- Dashboard budget-versus-spending charts by category.

## Run

From this directory:

```bash
npm install
npx expo start
```

Open the project using Expo Go or a development build. Android and iOS use Expo SQLite; this project currently targets native mobile, not web.

## Design

- `src/data/database.ts` owns schema creation and migrations.
- `src/data/budgetRepository.ts` owns parameterized SQLite queries and write operations.
- `src/domain/` contains types, validation, and shared budget constants and formatting.
- `src/screens/` contains screen-level state and presentation.
- `src/ui/` contains shared visual components and design tokens.
- `src/app/` contains Expo Router routes and the shared navigation layout.

Database operations and budget calculations are kept out of screen components, while shared controls avoid repeated UI logic. The mobile database (`budget-tracker.db`) is separate from the desktop database; this app does not sync data between devices or applications.

Run `npm run lint` and `npm run typecheck` to validate the source.
