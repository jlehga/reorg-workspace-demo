# Hosting the Reorg Workspace demo (interview review)

Prefer the **live demo URL**. Design doc remains `docs/design.md`.

Demo login: **demouser** / **test123**

## Live demo (primary)

https://jlehga-reorg-workspace-demo-app-ggbknu.streamlit.app/

Open that URL first. Sign in with **demouser** / **test123**.

Public mirror (source for the hosted app):

https://github.com/jlehga/reorg-workspace-demo

No secrets are required for the walkthrough. Optional: `LLM_API_KEY` under Streamlit App settings → Secrets for live LLM interpretation (`LLM_MODEL` / `LLM_BASE_URL` also optional).

## OPTIONAL — only if the live link does not work

### Zip (no clone)

```bash
./make_zip.sh   # writes dist/reorg-execution-system.zip
```

Or download the latest GitHub Release asset `reorg-execution-system.zip`:

https://github.com/jlehga/reorg-execution-system/releases

(also mirrored on https://github.com/jlehga/reorg-workspace-demo/releases when published)

Unzip, then:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8765
```

### Git clone

Private: https://github.com/jlehga/reorg-execution-system  
Public mirror: https://github.com/jlehga/reorg-workspace-demo  

See `RUN.txt` quickstart. Only needed if reviewers want full source/history.

### Other hosts (maintainer)

Render free web service: connect GitHub to `jlehga/reorg-workspace-demo` (or the private repo), or use Blueprint with `render.yaml`. Share the resulting `onrender.com` URL.
