from fastapi import FastAPI
from models import User, UserBet, VerifyRequest


app = FastAPI()


@app.post("/server_seed")
def get_hashed_server_seed(request: User):
    resp = request.get_server_seed()
    return resp


@app.post("/bet")
def bet(request: UserBet):
    resp = request.process()
    return resp


@app.post("/verify")
def verify(request: VerifyRequest):
    resp = request.process()
    return resp
