from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    database_url:str
    secret_key:str
    lst_org:str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

# setting chi chua dang string -> khi dung thi dung split