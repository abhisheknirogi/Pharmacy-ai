# backend/app/main.py

from fastapi import FastAPI
from app.api.routes import sales, inventory, reorder

app = FastAPI(title="Pharmarec AI")

app.include_router(sales.router, prefix="/sales")
app.include_router(inventory.router, prefix="/inventory")
app.include_router(reorder.router, prefix="/reorder")

@app.get("/")
def home():
    return {"status": "Pharmarec AI running"}
add_to_startup()
if __name__ == "__main__":
    add_to_startup()   # run once for setup
    main_agent_loop()  # your watcher + uploader
