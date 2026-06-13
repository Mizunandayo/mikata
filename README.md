# Mikata (味方)

Continuous Clinical Automation Testing System — built for UiPath AgentHack, Track 3 (UiPath Test Cloud).

## Structure

- `frontend/` — Next.js 15 app
- `backend/` — FastAPI service

## Local development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## License

MIT — see [LICENSE](./LICENSE).
