# School AI Assistant

React, Vite, and Tailwind CSS frontend for the FastAPI chat endpoint.

## Run locally

Start the backend from `server/`:

```bash
uvicorn app.main:app --reload
```

Then start the frontend from `client/`:

```bash
npm install
npm run dev
```

The Vite development server proxies `/api` and `/health` to
`http://127.0.0.1:8000`. Set `VITE_API_PROXY_TARGET` to use a different local
backend URL.

For deployments where the API is on a different origin, set
`VITE_API_BASE_URL` at build time. Otherwise, serve the frontend and API behind
the same origin or a reverse proxy. Do not put credentials in `VITE_*`
variables; they are embedded in client-side assets.

## Chat behavior

The chat sends `{ "query": "..." }` to `POST /api/chat` and expects
`{ "answer": "..." }`. It validates empty input, reports API errors, supports
retry, and does not send tenant or branch identifiers from the browser.
