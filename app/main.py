from fastapi import FastAPI


app = FastAPI()


# test api
@app.get('/hello')
def HelloWorld():
    return {"data": "Hello World !"}