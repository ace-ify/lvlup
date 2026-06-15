from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

fake_user_db = {
    'johndoe': {
        'username': 'johndoe',
        'hashed_password': pwd_context.hash('secret123')
    },
    'smitha': {
        'username': 'smitha',
        'hashed_password': pwd_context.hash('devops')
    }
}


def get_user(username: str):
    return fake_user_db.get(username)


def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)