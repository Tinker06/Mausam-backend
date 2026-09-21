from fastapi import FastAPI

app = FastAPI(title="MAUSAM API")

@app.get("/")
def root():
    return {"message": "MAUSAM Backend is running!"}