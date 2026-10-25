# Schema audit: where answers can silently depend on an unstated choice (`specbridge.report.impact audit`)

| database | join fan-out > 1.1 | join drops > 5% unmatched | measure column > 5% NULL | ranking column tied at the top | flag/status with a minority >= 2% | total |
|---|---|---|---|---|---|---|
| baseball_1 | 46 | 30 | 0 | 98 | 54 | 228 |
| sakila_1 | 10 | 0 | 0 | 2 | 5 | 17 |
| customers_and_invoices | 13 | 12 | 1 | 0 | 10 | 36 |
| chinook_1 | 12 | 6 | 1 | 0 | 14 | 33 |
| financial | 8 | 5 | 1 | 2 | 12 | 28 |
| student_club | 6 | 8 | 0 | 1 | 13 | 28 |
| thrombosis_prediction | 1 | 2 | 31 | 1 | 8 | 43 |
| formula_1 | 19 | 8 | 0 | 3 | 0 | 30 |
| archeology | 0 | 0 | 0 | 15 | 55 | 70 |
| insider | 0 | 1 | 0 | 13 | 48 | 62 |
| crypto | 0 | 0 | 0 | 10 | 12 | 22 |
| alien | 0 | 0 | 0 | 9 | 50 | 59 |
| Brazilian_E_Commerce | 2 | 0 | 0 | 6 | 2 | 10 |
| IPL | 4 | 1 | 0 | 2 | 8 | 15 |
| bank_sales_trading | 3 | 0 | 2 | 5 | 28 | 38 |

Examples:
- sakila_1: city.country_id -> country: 5.5 rows per country row (max 60); film.length: 10 rows share the maximum; customer.active: 0 is 3%
- Brazilian_E_Commerce: olist_order_items.order_id -> olist_orders: 1.1 rows per olist_orders row (max 21); olist_products.product_length_cm: 149 rows share the maximum; olist_order_reviews.review_score: 2 is 3%
