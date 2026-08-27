# Hosting the Reorg Workspace demo (interview review)

Prefer the **live demo URL**. Design doc remains `docs/design.md`.

Demo login: **demouser** / **test123**

## Live demo (primary)

https://jlehga-reorg-workspace-demo-app-ggbknu.streamlit.app/

Open that URL first. Sign in with **demouser** / **test123**.

Public mirror (source for the hosted app):

https://github.com/jlehga/reorg-workspace-demo

No secrets are required for the walkthrough. Optional live LLM via Streamlit secrets / env (`LLM_API_KEY`).

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

Only if access has been granted (private repo is version-controlled; not required for review):

Private: https://github.com/jlehga/reorg-execution-system  
Public mirror: https://github.com/jlehga/reorg-workspace-demo  

See `RUN.txt` quickstart. Prefer zip above when the live demo is down.

### Other hosts (maintainer)

Render free web service: connect GitHub to `jlehga/reorg-workspace-demo` (or the private repo), or use Blueprint with `render.yaml`. Share the resulting `onrender.com` URL.
