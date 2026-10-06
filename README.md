# Campus Customs — HW4

Campus Customs is a Yale-inspired merchandise storefront with a React/Vite frontend and a FastAPI/PydanticAI backend.

## Important data note

The local database, product images, and `.env` file are intentionally excluded from GitHub. Place the provided local data pack at `data/campus_customs.db` and `data/products/` before running the full app. Copy `.env.example` to `.env` and add a local API key; never commit `.env`.

## Run the frontend

From the repository root:

```powershell
npm install
npm.cmd run dev
```

## Run the backend

From the `backend/` folder:

```powershell
py -m pip install -r requirements.txt
py -m uvicorn main:app --reload --port 8000
```

The frontend runs at `http://localhost:5173` and proxies `/api` and `/media` to FastAPI on port 8000.

## Included documentation

- `AI_prompts.md` — prompt and request log
- `output/harness.md` — data, model, tools, safety, and runtime harness
- `output/usability.md` — Problem 9 usability improvements
- `output/design.md` — Problem 10 design improvements
- `output/app_check.html` — Problem 11 screenshot checks
- `output/audit_trail.json` — append-only agent activity audit

## Repository safety

Do not commit `.env`, `data/campus_customs.db`, product images, API keys, password hashes, or other private data.
