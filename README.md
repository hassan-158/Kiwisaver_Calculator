How to run in dev:

run api.py from the root with the following:
    uv run uvicorn backend.api:app --reload

cd into frontend from a new bash terminal and run the following:
    npm run dev


Deployment:

API is deployed on https://dashboard.render.com/ to the url https://kiwisaver-calculator.onrender.com/

Web App is deployed on https://vercel.com/ to the url ...

The API automatically rebuilds upon pushing to main, the website does the same.

Test API deployment with:

curl -X POST https://kiwisaver-calculator.onrender.com/calculate \
-H "Content-Type: application/json" \
-d '{
  "current_age": 30,
  "life_cover": 500000,
  "premium": 1800,
  "kiwisaver_balance": 100000,
  "salary": 80000,
  "kiwisaver_rate": 0.03
}'


IMPORTANT need to branch off and do PRs now otherwise the API and website will update in dev.

