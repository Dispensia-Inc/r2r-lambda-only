from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get('/test1')
async def test1():
    return {"message": "test"}

# export port 8080
handler = Mangum(app)