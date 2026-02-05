from fastapi import FastAPI


app = FastAPI()

@app.get("/users/")
def read_users():
    return "hi"