# rpm-autopay-service

Collectus hackathon backend — **Tamara-like shop + installments + Smart Autocharge**.

## Flow

1. Browse products → checkout with **Pay in 3/4**
2. First installment paid immediately; remaining created as upcoming
3. Customer pays a due/overdue installment
4. RPM event `repayment.succeeded` → **AI decision** → Autopay may settle other overdue

## Quick start

```bash
cd rpm-autopay-service
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Docs: http://127.0.0.1:8000/docs

## Key APIs

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/products` | Catalog |
| GET | `/api/customers` | Demo personas |
| POST | `/api/checkout` | Buy with installments (first payment now) |
| GET | `/api/customers/{id}/orders` | Purchases + installment schedule |
| GET | `/api/customers/{id}/installments` | Flat installment list |
| POST | `/api/installments/{id}/pay` | Pay installment → RPM → AI → Autopay |
| POST | `/api/admin/reset` | Reset seed data |

## AI

Decisions come from [smart-charge-decision-service](https://github.com/krutik0204/collectus-smart-charge-decision-service)
(trained model + expected-value policy), deployed at
`https://collectus-smart-charge-decision-service.onrender.com`.

| Env | Value |
| --- | --- |
| `USE_MOCK_AI` | `false` — call the AI service (`true` = built-in scorecard) |
| `AI_DECISION_URL` | `https://collectus-smart-charge-decision-service.onrender.com/v1/decide` (local: `http://127.0.0.1:8001/v1/decide`) |

If the AI service is unreachable (e.g. Render free-tier cold start), the backend falls back to the
built-in scorecard and labels the decision `mock-fallback`. Warm both services before a demo.

## Demo personas

| Customer | Scenario | Smart Autocharge after paying one overdue installment |
| --- | --- | --- |
| Aisha Al-Harbi | Healthy card, just repaid | **charge** full overdue |
| Omar Nasser | Weak card, 4 recent fails | **skip** — ask to update card |
| Layla Hassan | Mid profile | **partial** 50% |
| Fahad Al-Qahtani | 5 failed attempts this week | **skip** by hard gate (decline budget) — model not called |
| Noura Al-Otaibi | PS5, 3 overdue | **partial** 75% of a large balance |
| Khalid Al-Shehri | ~2 months overdue | **partial** 50% — long-overdue penalty |
| Reem Al-Dosari | Card recovering from fails | **partial** 25% — smallest step |
| Yusuf Al-Ghamdi | Overdue on two orders (pay a **Nike** installment) | **charge** remaining overdue across both orders |
| Sara Al-Mutairi | Only one overdue | no autocharge — upcoming is never charged |
