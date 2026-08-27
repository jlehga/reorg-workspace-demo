# Hosting the Reorg Workspace demo (interview review)

Prefer a **hosted URL** or the **zip** over `git clone`. Design doc remains `docs/design.md`.

Demo login: **demouser** / **test123**

## Live demo URL (temporary tunnel)

While the review agent VM is running, a Cloudflare quick tunnel may be up:

https://notifications-developmental-diego-complicated.trycloudflare.com

This URL is **ephemeral** (dies when the tunnel/VM stops). For a durable link, use Streamlit Community Cloud below (one-time click).

## Option A — Streamlit Community Cloud (recommended durable host)

A **public review mirror** (no private-repo GitHub App needed):

https://github.com/jlehga/reorg-workspace-demo

Exact clicks:

1. Open the one-click deploy link:  
   https://share.streamlit.io/deploy?repository=jlehga/reorg-workspace-demo&branch=main&mainModule=app.py  
   Or: https://share.streamlit.io → sign in with GitHub → **New app**.
2. Confirm **Repository** `jlehga/reorg-workspace-demo`, **Branch** `main`, **Main file path** `app.py`.
3. Optional App URL slug: `reorg-workspace`.
4. Click **Deploy**. Wait until status is **Running**.
5. Share the resulting `https://….streamlit.app` URL with reviewers.

Deploying from the private repo instead (`jlehga/reorg-execution-system`) also works if you authorize the Streamlit GitHub App for that private repository (or temporarily make it Public).

No secrets are required for the walkthrough. Optional: add `LLM_API_KEY` / `OPENAI_API_KEY` under App settings → Secrets for live LLM interpretation.

## Option B — Render (free web service)

1. https://dashboard.render.com → **New → Web Service** → connect GitHub → select `jlehga/reorg-workspace-demo` (or the private repo).
2. Or use Blueprint: **New → Blueprint** → point at `render.yaml` in the repo.
3. Runtime Python 3. Build: `pip install -r requirements.txt`. Start is already in `render.yaml`.
4. Deploy and share the `onrender.com` URL.

## Option C — Zip (no clone)

```bash
./make_zip.sh   # writes dist/reorg-execution-system.zip
```

Or download the latest GitHub Release asset `reorg-execution-system.zip` from the private repo:

https://github.com/jlehga/reorg-execution-system/releases

(also mirrored on https://github.com/jlehga/reorg-workspace-demo/releases when published)

Unzip, then:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8765
```

## Option D — Git clone (optional)

Private: https://github.com/jlehga/reorg-execution-system  
Public mirror: https://github.com/jlehga/reorg-workspace-demo  

See `RUN.txt` quickstart. Only needed if reviewers want full source/history.
