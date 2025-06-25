# Avigilon UI Workspace

This is a Streamlit-based UI for exploring and visualizing Avigilon API endpoints and event data.

## Folder Structure

- `pages/` - Contains Streamlit pages for each API group or feature.
- `components/` - (Optional) For reusable Streamlit UI components.
- `utils/` - (Optional) For helper functions (API calls, formatting, etc).
- `requirements.txt` - Python dependencies for the UI.
- `README.md` - Project overview and usage instructions.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the UI:
   ```bash
   streamlit run Home.py
   ```

## Pages
- Home: Overview and navigation.
- Endpoints: Interact with all Avigilon API endpoints.
- Active Events: Visualize ACTIVE events from all servers.

---

## Duke Frontend Service Setup (NSSM)

Use [NSSM](https://nssm.cc) to run Duke Central as Windows services:

* **Service Name**: `DukeFarmingFrontend`
* **Path**: `C:\path\to\venv\Scripts\python.exe`
* **Startup Dir**: `C:\path\to\Duke-Frontend`
* **Arguments**:

  ```
  -m streamlit run Home.py --server.port 8501 --server.headless true
  ```

### Manage Services

```bash

net stop DukeFarmingFrontend
net start DukeFarmingFrontend
```

---
