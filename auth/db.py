from beanie import Document
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from fastapi_users_db_beanie.access_token import BeanieAccessTokenDatabase, BeanieBaseAccessToken

class User(BeanieBaseUser, Document):
    # username: str
    pass

async def get_user_db():
    yield BeanieUserDatabase(User)

class AccessToken(BeanieBaseAccessToken, Document):
    pass

async def get_access_token_db():
    yield BeanieAccessTokenDatabase(AccessToken)