from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import users
from app.api import auth
from app.api import ambiente
from app.api import cargar_archivos
from app.api import grupos
from app.api import programas




app = FastAPI()

# Incluir en el objeto app los routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/access", tags=["login"])
app.include_router(ambiente.router, prefix="/ambientes", tags=["ambientes"])
app.include_router(cargar_archivos.router, prefix="/files", tags=["cargar_archivos"])
app.include_router(grupos.router, prefix="/grupos", tags=["grupos"])
app.include_router(programas.router, prefix="/programas", tags=["Programas"])

# Configuración de CORS para permitir todas las solicitudes desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Permitir estos métodos HTTP
    allow_headers=["*"],  # Permitir cualquier encabezado en las solicitudes
)

@app.get("/")
def read_root():
    return {
                "message": "ok",
                "autor": "ADSO 2847248"
            }
