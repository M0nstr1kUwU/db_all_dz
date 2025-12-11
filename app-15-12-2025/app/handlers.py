from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.forms import UserForm, UserCreateForm, SnippetCreateForm, SnippetUpdateForm
from app.database import connect_db, User, AuthToken, Snippet, Like
from app.utils import get_password_hash
from app.auth import check_auth_token
from app.config import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Страницы
@router.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/snippets", response_class=HTMLResponse)
async def get_snippets_page(request: Request):
    return templates.TemplateResponse("snippets.html", {"request": request})


@router.get("/my-snippets", response_class=HTMLResponse)
async def get_my_snippets_page(request: Request):
    return templates.TemplateResponse("my_snippets.html", {"request": request})


@router.get("/create-snippet", response_class=HTMLResponse)
async def create_snippet_page(request: Request):
    return templates.TemplateResponse("create_snippet.html", {"request": request})


@router.post('/login')
def login(user_form: UserForm, db=Depends(connect_db)):
    user = db.query(User).filter(User.email == user_form.email).first()
    if not user or get_password_hash(user_form.password) != user.password:
        return {'error': 'Invalid email or password'}

    auth_token = AuthToken(token=AuthToken.generate_token(), user_id=user.id)
    db.add(auth_token)
    db.commit()
    return {'token': auth_token.token, 'user_id': user.id}


@router.post('/register')
def register(user: UserCreateForm, db=Depends(connect_db)):
    if db.query(User.id).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail='Email already exists')

    new_user = User(
        email=user.email,
        password=get_password_hash(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
        nick_name=user.nick_name
    )
    db.add(new_user)
    db.commit()
    return {'user_id': new_user.id, 'message': 'User created successfully'}


@router.get('/user')
def get_user(auth_token: AuthToken = Depends(check_auth_token), db=Depends(connect_db)):
    user = db.query(User).filter(User.id == auth_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return {
        'id': user.id,
        'email': user.email,
        'nick_name': user.nick_name,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'created_at': user.created_at
    }


@router.post('/logout')
def logout(authorization: str = None, db=Depends(connect_db)):
    if authorization and authorization.startswith('Bearer '):
        token = authorization.replace('Bearer ', '')
        auth_token = db.query(AuthToken).filter(AuthToken.token == token).first()
        if auth_token:
            db.delete(auth_token)
            db.commit()
    return {'message': 'Logged out'}


@router.post('/snippets')
def create_snippet(
        snippet: SnippetCreateForm,
        auth_token: AuthToken = Depends(check_auth_token),
        db=Depends(connect_db)
):
    new_snippet = Snippet(
        user_id=auth_token.user_id,
        title=snippet.title,
        code=snippet.code,
        description=snippet.description
    )
    db.add(new_snippet)
    db.commit()
    db.refresh(new_snippet)

    return {
        'id': new_snippet.id,
        'title': new_snippet.title,
        'code': new_snippet.code,
        'description': new_snippet.description,
        'created_at': new_snippet.created_at,
        'like_count': 0
    }


@router.get('/snippets')
def list_snippets(db=Depends(connect_db), limit: int = 50, offset: int = 0):
    snippets = db.query(Snippet).order_by(Snippet.created_at.desc()).limit(limit).offset(offset).all()

    result = []
    for snippet in snippets:
        user = db.query(User).filter(User.id == snippet.user_id).first()
        like_count = db.query(Like).filter(Like.snippet_id == snippet.id).count()

        result.append({
            'id': snippet.id,
            'title': snippet.title,
            'code': snippet.code[:100] + '...' if len(snippet.code) > 100 else snippet.code,
            'description': snippet.description,
            'created_at': snippet.created_at,
            'like_count': like_count,
            'author': {
                'id': user.id if user else None,
                'nick_name': user.nick_name if user else 'Unknown',
                'email': user.email if user else 'unknown@example.com'
            }
        })

    return {'snippets': result, 'count': len(result)}


@router.get('/snippets/my')
def my_snippets(auth_token: AuthToken = Depends(check_auth_token), db=Depends(connect_db)):
    snippets = db.query(Snippet).filter(
        Snippet.user_id == auth_token.user_id
    ).order_by(Snippet.created_at.desc()).all()

    result = []
    for snippet in snippets:
        like_count = db.query(Like).filter(Like.snippet_id == snippet.id).count()
        result.append({
            'id': snippet.id,
            'title': snippet.title,
            'code': snippet.code,
            'description': snippet.description,
            'created_at': snippet.created_at,
            'like_count': like_count
        })

    return {'snippets': result}


@router.get('/snippets/{snippet_id}')
def get_snippet(snippet_id: int, db=Depends(connect_db)):
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail='Snippet not found')

    user = db.query(User).filter(User.id == snippet.user_id).first()
    like_count = db.query(Like).filter(Like.snippet_id == snippet_id).count()

    return {
        'id': snippet.id,
        'title': snippet.title,
        'code': snippet.code,
        'description': snippet.description,
        'created_at': snippet.created_at,
        'like_count': like_count,
        'author': {
            'id': user.id if user else None,
            'nick_name': user.nick_name if user else 'Unknown',
            'email': user.email if user else 'unknown@example.com'
        }
    }


@router.put('/snippets/{snippet_id}')
def update_snippet(
        snippet_id: int,
        snippet_update: SnippetUpdateForm,
        auth_token: AuthToken = Depends(check_auth_token),
        db=Depends(connect_db)
):
    snippet = db.query(Snippet).filter(
        Snippet.id == snippet_id,
        Snippet.user_id == auth_token.user_id
    ).first()

    if not snippet:
        raise HTTPException(status_code=404, detail='Snippet not found or access denied')

    if snippet_update.title is not None:
        snippet.title = snippet_update.title
    if snippet_update.code is not None:
        snippet.code = snippet_update.code
    if snippet_update.description is not None:
        snippet.description = snippet_update.description

    db.commit()
    db.refresh(snippet)

    like_count = db.query(Like).filter(Like.snippet_id == snippet_id).count()

    return {
        'id': snippet.id,
        'title': snippet.title,
        'code': snippet.code,
        'description': snippet.description,
        'created_at': snippet.created_at,
        'like_count': like_count
    }


@router.delete('/snippets/{snippet_id}')
def delete_snippet(
        snippet_id: int,
        auth_token: AuthToken = Depends(check_auth_token),
        db=Depends(connect_db)
):
    snippet = db.query(Snippet).filter(
        Snippet.id == snippet_id,
        Snippet.user_id == auth_token.user_id
    ).first()

    if not snippet:
        raise HTTPException(status_code=404, detail='Snippet not found or access denied')

    db.query(Like).filter(Like.snippet_id == snippet_id).delete()

    db.delete(snippet)
    db.commit()

    return {'message': 'Snippet deleted successfully'}


@router.post('/snippets/{snippet_id}/like')
def like_snippet(
        snippet_id: int,
        auth_token: AuthToken = Depends(check_auth_token),
        db=Depends(connect_db)
):
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail='Snippet not found')

    existing_like = db.query(Like).filter(
        Like.snippet_id == snippet_id,
        Like.user_id == auth_token.user_id
    ).first()

    if existing_like:
        db.delete(existing_like)
        db.commit()
        return {'liked': False, 'message': 'Like removed'}

    new_like = Like(snippet_id=snippet_id, user_id=auth_token.user_id)
    db.add(new_like)
    db.commit()

    return {'liked': True, 'message': 'Snippet liked'}


@router.get('/snippets/{snippet_id}/likes')
def get_snippet_likes(snippet_id: int, db=Depends(connect_db)):
    likes = db.query(Like).filter(Like.snippet_id == snippet_id).all()

    result = []
    for like in likes:
        user = db.query(User).filter(User.id == like.user_id).first()
        result.append({
            'id': like.id,
            'user': {
                'id': user.id if user else None,
                'nick_name': user.nick_name if user else 'Unknown'
            },
            'created_at': like.created_at
        })

    return {'likes': result, 'count': len(result)}
