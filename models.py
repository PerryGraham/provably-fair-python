from pydantic import BaseModel, model_validator
import random
import json
from typing import Dict
from typing import Optional
import hashlib
import string


class User(BaseModel):
    id: str
    new_seed: bool = False

    def get_server_seed(self):
        user_session = get_user_session(self)

        return user_session.hashed_server_seed


class Bet(BaseModel):
    coin_flip: bool
    client_seed: str
    nonce: int
    outcome: Optional[bool] = None
    server_seed: Optional[str] = None


class VerifyRequest(BaseModel):
    client_seed: str
    server_seed: str
    nonce: int
    hashed_server_seed: str
    result: bool

    def process(self):
        honest = True
        # Check hashed seed matches
        h = hashlib.new("sha256")
        h.update(str.encode(self.server_seed))
        actual_hashed_server_seed = h.hexdigest()
        if actual_hashed_server_seed != self.hashed_server_seed:
            honest = False

        # Combine seeds and hash
        h = hashlib.new("sha256")
        h.update(str.encode(self.server_seed))
        h.update(str.encode(self.client_seed))
        h.update(str.encode(str(self.nonce)))
        actual_hashed_game_seed = h.hexdigest()

        # Calculate result
        game_seed_as_int = int(actual_hashed_game_seed, 16)
        actual_result = bool(game_seed_as_int % 2)

        if actual_result != self.result:
            honest = False

        return honest


class UserSession(BaseModel):
    user: User
    server_seed: Optional[str] = None
    hashed_server_seed: Optional[str] = None

    class Config:
        validate_assignment = True

    @model_validator(mode="before")
    def set_seeds(cls, values):
        if values.get("server_seed") is not None:
            return values

        server_seed = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=20)
        )
        h = hashlib.new("sha256")
        h.update(str.encode(server_seed))
        hashed_server_seed = h.hexdigest()

        values["server_seed"] = server_seed
        values["hashed_server_seed"] = hashed_server_seed

        return values


class UserBet(BaseModel):
    user: User
    bet: Bet

    def process(self) -> Dict:
        user_session = get_user_session(self.user)

        # Combine seeds and hash
        h = hashlib.new("sha256")
        h.update(str.encode(user_session.server_seed))
        h.update(str.encode(self.bet.client_seed))
        h.update(str.encode(str(self.bet.nonce)))
        hashed_game_seed = h.hexdigest()

        # Calculate game result from hashed game seed
        game_seed_as_int = int(hashed_game_seed, 16)
        result = bool(game_seed_as_int % 2)

        self.bet.outcome = result == self.bet.coin_flip
        self.bet.server_seed = user_session.server_seed

        return self.bet.model_dump()


def get_sessions():
    with open("db/sessions.json", "r") as f:
        data = json.load(f)
    return data


def save_user_session(session: UserSession) -> None:
    sessions = get_sessions()

    sessions[session.user.id] = session.model_dump()

    with open("db/sessions.json", "w") as f:
        json.dump(sessions, f, indent=4)


def get_user_session(user: User) -> UserSession:
    sessions = get_sessions()

    user_session_data = sessions.get(user.id)
    if user_session_data is None or user.new_seed:
        user_session = UserSession(user=user)
        save_user_session(session=user_session)
    else:
        user_session = UserSession(**user_session_data)

    return user_session
