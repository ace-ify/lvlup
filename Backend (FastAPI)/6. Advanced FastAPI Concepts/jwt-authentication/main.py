from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import create_access_token, verify_token
from utils import get_user, verify_password

app = FastAPI()
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='token')

@app.post('/token')
def login(data: OAuth2PasswordRequestForm=Depends()):
    user_dict=get_user(data.username)
    
    # PRODUCTION FIX (Security): Always use generic error messages for authentication
    # to prevent "Username Enumeration" (where hackers can guess valid usernames).
    # Also, return 401 Unauthorized instead of 400 Bad Request.
    if not user_dict or not verify_password(data.password, user_dict['hashed_password']):
        raise HTTPException(
            status_code=401, 
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    access_token=create_access_token(data={'sub':data.username})
    return {'access_token':access_token,'token_type':'bearer'}
    
@app.get('/users')
def read_users(token:str=Depends(oauth2_scheme)):
    username=verify_token(token)
    
    # PRODUCTION FIX (Integrity): Even if the token signature is valid, 
    # check if the user actually exists in the database. 
    # A user might have been deleted/suspended while their token is still active.
    user_dict=get_user(username)
    if not user_dict:
        raise HTTPException(status_code=401, detail='User not found or deactivated')
        
    return {'username':username}