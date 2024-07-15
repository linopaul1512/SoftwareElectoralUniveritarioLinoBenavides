
from fastapi import Depends, FastAPI, File, Request, HTTPException, Form, Response, UploadFile, status, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware import Middleware
from sqlalchemy import Double
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
#from excepciones import Exception_No_Apto_Para_Artesano, Exception_No_Apto_Para_Cliente
#from excepcionesUsuario import LoginExpired, Requires_el_Login_de_Exception
import schemas
import  models, seguridad.auth as auth, crudUsuario
import seguridad.auth
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from typing import Annotated, Optional, Union
import shutil
import os
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import date, datetime, timedelta, timezone
from sqlApp.database import SessionLocal, engine






# Crear todas las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI con el middleware de sesión
app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key="your_secret_key")
])

# Montar el directorio estático para servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurar Jinja2 para la renderización de plantillas
templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="iniciar_sesion_post")

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/usuario/create/", response_model=schemas.User)
async def crear_usuario(request: Request, 
                        CI: str = Form(...), 
                        Nombres: str = Form(...), 
                        Apellidos: str = Form(...), 
                        Correo_electronico: str = Form(...), 
                        Direccion_hab: str = Form(...), 
                        Direccion_electoral: str = Form(...), 
                        Fecha_nacimiento: str = Form(...), 
                        Telefono : str = Form(...),
                        Imagen : str = Form(...),
                        Habilitado : str = Form(...),
                        Contrasena : str = Form(...),
                        Estado : str = Form(...),
                        db: Session = Depends(get_db)):
    print("Usuario: ", Correo_electronico)
    user = schemas.UserCreate(CI=CI, 
                              Nombres=Nombres, 
                              Apellidos=Apellidos, 
                              Correo_electronico=Correo_electronico, 
                              Direccion_hab=Direccion_hab,
                              Direccion_electoral=Direccion_electoral, 
                              Fecha_nacimiento=Fecha_nacimiento,
                              Telefono=Telefono,
                              Imagen=Imagen,
                              Habilitado=Habilitado,
                              Contrasena=Contrasena,
                              Estado=Estado)
    db_user = crudUsuario.get_user_by_email(db, email=user.Correo_electronico)
    print("Db user: ", db_user)
    if db_user: 
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crudUsuario.get_user_by_ci(db, user_id=user.cedula_identidad)
    if db_user: 
        raise HTTPException(status_code=400, detail="CI already registered")
    crudUsuario.create_user(db=db, user=user)
    return templates.TemplateResponse("crearUsuario.html.jinja", {"request": request})


@app.get("/usuario/create/", response_class=HTMLResponse)
async def create_usuario_template(request: Request):
    print("Usuario get: ", )
    return templates.TemplateResponse("crearUsuario.html.jinja", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def home_no_iniciado(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("homeNoIniciado.html.jinja", {"request": request})


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def read_usuario(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = crudUsuario.get_user_by_ci(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("perfilUsuario.html", {"request": request, "item": item})

@app.get("/base/administrador/", response_class=HTMLResponse)
async def base_administrador_iniciado(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("baseAdministrador.html.jinja", {"request": request})

@app.get("/base/votante/", response_class=HTMLResponse)
async def base_votante_iniciado(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("baseVotante.html.jinja", {"request": request})

    

# Iniciar sesión
@app.get("/iniciarsesion/", response_class=HTMLResponse)
async def iniciar_sesion_template(request: Request):
    return templates.TemplateResponse("login-v2.html", {"request": request})



@app.post('/iniciar_sesion', response_class=HTMLResponse)
async def iniciar_sesion_post(request: Request,
                   Correo_electronico: str = Form(...),               
                   Contrasena: str = Form(...), 
                   db: Session = Depends(get_db)):
    user = auth.autenticar_usuario(db, Correo_electronico, Contrasena)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Error, Incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"}
        )
    tiempo_expiracion = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    nombre= f'{user.Nombres} {user.Apellidos}'
    token_acceso = auth.crear_token_acceso(
        data={'CI': user.CI,
              'Nombre': nombre,
              'IdRole': user.IdRole},
        expires_delta=tiempo_expiracion
    )
    request.session['CI'] = user.CI
    request.session['IdRole'] = user.IdRole
    
    if user.IdRole == "1":
        return RedirectResponse(url="/base/votante/", status_code=status.HTTP_303_SEE_OTHER)
    elif user.IdRole == "2":
        return RedirectResponse(url="/base/administrador/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        print("user", user.IdRole )
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.middleware("http")
async def create_auth_header(request: Request, call_next):
    if ("Authorization" not in request.headers 
        and "Authorization" in request.cookies):
        access_token = request.cookies["Authorization"]
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer {access_token}".encode(),
            )
        )
    elif ("Authorization" not in request.headers 
        and "Authorization" not in request.cookies): 
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer 12345".encode(),
            )
        )
        
    response = await call_next(request)
    return response
