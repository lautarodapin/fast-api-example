from pydantic import BaseModel

class Settings(BaseModel):
    authjwt_secret_key: str = "secret_key"
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False

