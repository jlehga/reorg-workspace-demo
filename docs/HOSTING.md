# Hosting the Reorg Workspace demo (interview review)

Prefer a **hosted URL** or the **zip** over `git clone`. Design doc remains `docs/design.md`.

## Option A — Streamlit Community Cloud (recommended, free)

Exact clicks:

1. Open https://share.streamlit.io and sign in with GitHub (account with access to `jlehga/reorg-execution-system`).
2. Click **New app**.
3. **Repository:** `jlehga/reorg-execution-system`  
   - If the private repo does not appear: GitHub → **Settings → Applications → Streamlit** (or authorize when prompted) and grant access to this repository.  
   - Fallback: temporarily set the repo to **Public** (Settings → General → Danger Zone), deploy, then set **Private** again.
4. **Branch:** `main`
5. **Main file path:** `app.py`
6. Optional: set App URL slug to `reorg-workspace` (or similar).
7. Click **Deploy**. Wait until status is **Running**.
8. Share the `https://….streamlit.app` URL with reviewers.

One-click deep link (still requires the Streamlit GitHub App to see the repo):

https://share.streamlit.io/deploy?repository=jlehga/reorg-execution-system&branch=main&mainModule=app.py

No secrets are required for the walkthrough. Optional: add `LLM_API_KEY` or `OPENAI_API_KEY` in Streamlit Cloud → App settings → Secrets if you want live LLM interpretation.

Demo login: **ops.demo** / **reorg-demo**

## Option B — Render (free web service)

1. https://dashboard.render.com → **New → Web Service** → connect GitHub → select this repo.
2. Runtime: **Python 3**. Build: `pip install -r requirements.txt`. Start: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
3. Deploy and share the `onrender.com` URL.

`render.yaml` in the repo root is a Blueprint if you prefer one-click from the Render dashboard.

## Option C — Zip (no clone)

```bash
./make_zip.sh   # writes dist/reorg-execution-system.zip
```

Or download the latest GitHub Release asset `reorg-execution-system.zip` from:

https://github.com/jlehga/reorg-execution-system/releases

Unzip, then:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8765
```

## Option D — Git clone (optional)

See `RUN.txt` quickstart. Only needed if reviewers want full git history.
