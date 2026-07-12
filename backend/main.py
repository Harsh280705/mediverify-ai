from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.health import router as health_router
from api.users import router as users_router

app = FastAPI(title='MediVerify AI API', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health_router)
app.include_router(auth_router, prefix='/api')
app.include_router(users_router, prefix='/api')


@app.get('/')
def root() -> dict[str, str]:
    return {'status': 'running'}
