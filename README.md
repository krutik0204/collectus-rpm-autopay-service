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

Each customer has a monthly scheme decline budget (Mada allows 3). A failed autocharge uses one;
with none left, neither Smart Autocharge nor cron will attempt.

| Customer | Declines left | Scenario | Smart Autocharge after paying one overdue installment |
| --- | --- | --- | --- |
| Aisha Al-Harbi | 3 | Healthy card, just repaid | **charge** full overdue |
| Omar Nasser | 2 | Weak card, 4 recent fails | **skip** — below the 10% bar, ask to update card |
| Layla Hassan | 2 | Mid profile | **charge** full overdue (~49–61% likely) |
| Fahad Al-Qahtani | 0 | No declines left, 5 fails | **skip** by hard gate — model not called |
| Noura Al-Otaibi | 3 | PS5, 3 overdue | **charge** the remaining SAR 1,049.50 |
| Khalid Al-Shehri | 3 | ~2 months overdue | **charge** — still worth it at the repayment moment |
| Reem Al-Dosari | 1 | Last decline of the month | **skip** — needs 30%, ~20–28% likely, saves the decline |
| Yusuf Al-Ghamdi | 3 | Overdue on two orders (pay a **Nike** installment) | **charge** remaining overdue across both orders |
| Sara Al-Mutairi | 3 | Only one overdue | no autocharge — upcoming is never charged |
