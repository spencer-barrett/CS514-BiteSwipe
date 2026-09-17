# BiteSwipe — Web App

The React frontend for BiteSwipe. It lives in `apps/biteswipe-app` within the monorepo.

## Prerequisites

Install these before anything else.

| Tool | Version | Check |
| --- | --- | --- |
| [Git](https://git-scm.com/downloads) | any recent | `git --version` |
| [Node.js](https://nodejs.org/) | 22 LTS or newer | `node --version` |
| npm | ships with Node | `npm --version` |


## 1. Clone the repository

```bash
git clone https://github.com/spencer-barrett/CS514-BiteSwipe
cd CS514-Biteswipe
```

## 2. Install dependencies

```bash
cd apps/biteswipe-app
npm install
```

## 3. Run the dev server

```bash
npm run dev
```

Open the URL printed in the terminal (usually http://localhost:5173). The page reloads automatically when you save changes.

## Other scripts

| Command | What it does |
| --- | --- |
| `npm run dev` | Start the dev server with hot reload |
| `npm run build` | Type-check and build for production into `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint |


## Troubleshooting

**`command not found: npm` or `node`** — Node isn't installed or isn't on your PATH. If you used nvm, restart your terminal or run `nvm use --lts`.

**Errors after pulling new changes** — dependencies may have changed. Run `npm install` again.

**Port 5173 already in use** — another dev server is running. Stop it, or Vite will pick the next free port automatically.

**Blank page or Firebase errors in the console** — check that every value in `.env` is filled in, then restart `npm run dev`. Vite only reads `.env` at startup.
