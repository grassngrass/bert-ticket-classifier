# AI Ticket Routing Portal — Frontend

React + TypeScript + Tailwind CSS UI for the FastAPI ticket classification backend.

## Develop

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

The dev server proxies `/api/*` to the FastAPI backend at `http://127.0.0.1:8000`
(see `vite.config.ts`), so start the backend first:

```bash
# from the project root
uvicorn app.main:app --reload
```

> The backend must have a trained model loaded, otherwise `/predict` returns
> HTTP 409 and the UI shows a "model not trained" message.

## Build

```bash
npm run build      # type-checks and outputs to dist/
npm run preview    # serve the production build
```

## Configuration

| Env var         | Default | Purpose                                  |
| --------------- | ------- | ---------------------------------------- |
| `VITE_API_BASE` | `/api`  | Backend base URL (set for non-proxy use) |
