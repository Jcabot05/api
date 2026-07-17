import os

import requests
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from supabase import Client, create_client


load_dotenv()

app = FastAPI()
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    email: str
    password: str


def get_supabase_url() -> str:
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_URL no está configurada",
        )
    return supabase_url


def get_supabase_key() -> str:
    supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    if not supabase_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_PUBLISHABLE_KEY no está configurada",
        )
    return supabase_key


def build_supabase_client() -> Client:
    return create_client(get_supabase_url(), get_supabase_key())


def get_supabase_client(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> Client:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de Supabase",
        )

    try:
        client = build_supabase_client()
        client.postgrest.auth(credentials.credentials)
        return client
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de Supabase inválido o expirado",
        ) from exc


@app.get("/")
def read_root():
    return {"message": "¡Hola, Fast API!"}


@app.post("/auth/login-temporal")
def login_temporal(payload: LoginRequest):
    url = f"{get_supabase_url()}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": get_supabase_key(),
        "Content-Type": "application/json",
    }
    response = requests.post(
        url,
        json={"email": payload.email, "password": payload.password},
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciales incorrectas en Supabase",
        )

    access_token = response.json().get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo obtener el access_token de Supabase",
        )

    return {"access_token": access_token}


@app.get("/tasks/", status_code=status.HTTP_200_OK)
def get_tasks(supabase: Client = Depends(get_supabase_client)):
    try:
        response = supabase.table("task").select("*").execute()
        return response.data
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar las tareas desde la base de datos.",
        ) from exc