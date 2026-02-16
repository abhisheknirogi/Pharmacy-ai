from fastapi import APIRouter

router = APIRouter(tags=["Preview"])


@router.get("/preview", response_class="fastapi.responses.HTMLResponse")
def preview_page():
    html = """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>PharmaRec AI - Preview</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 2rem; }
        .box { border: 1px solid #ddd; padding: 1rem; margin-bottom: 1rem; }
        button { padding: 0.5rem 1rem; }
        pre { background:#f7f7f7; padding:1rem; }
      </style>
    </head>
    <body>
      <h1>PharmaRec AI — Quick Preview</h1>

      <div class="box">
        <h3>Health Check</h3>
        <button onclick="call('/health')">Call /health</button>
        <pre id="health">-</pre>
      </div>

      <div class="box">
        <h3>Reorder Suggestions (AI)</h3>
        <button onclick="call('/reorder/suggestions')">Get Suggestions</button>
        <pre id="reorder">-</pre>
      </div>

      <div class="box">
        <h3>Predict for medicine id=1</h3>
        <button onclick="call('/reorder/predict/1')">Predict</button>
        <pre id="predict">-</pre>
      </div>

      <script>
        async function call(path) {
          try {
            const res = await fetch(path);
            const txt = await res.text();
            const el = document.getElementById(path.includes('health')? 'health' : (path.includes('suggestions')? 'reorder' : 'predict'));
            el.textContent = txt;
          } catch (e) {
            console.error(e);
            alert('Request failed: ' + e.message);
          }
        }
      </script>
    </body>
    </html>
    """
    from fastapi.responses import HTMLResponse

    return HTMLResponse(content=html, status_code=200)
