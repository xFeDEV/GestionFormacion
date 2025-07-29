from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import users
from app.api import auth
from app.api import ambiente
from app.api import cargar_archivos
from app.api import grupos
from app.api import programas
from app.api import grupo_instructor
from app.api import centro_formacion
from app.api import programacion
from app.api import competencia
from app.api import resultado_aprendizaje
from app.api import festivos
from app.api import notificacion




app = FastAPI()

# Incluir en el objeto app los routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/access", tags=["Login"])
app.include_router(ambiente.router, prefix="/ambientes", tags=["Ambientes"])
app.include_router(cargar_archivos.router, prefix="/files", tags=["Cargar Archivos"])
app.include_router(grupos.router, prefix="/grupos", tags=["Grupos"])
app.include_router(programas.router, prefix="/programas", tags=["Programas"])
app.include_router(grupo_instructor.router, prefix="/grupo-instructor", tags=["Grupos Instructor"])
app.include_router(centro_formacion.router, prefix="/centro-formacion", tags=["Centros Formacion"])
app.include_router(programacion.router, prefix="/programacion", tags=["Programacion"])
app.include_router(competencia.router, prefix="/competencias", tags=["Competencias"])
app.include_router(resultado_aprendizaje.router, prefix="/resultados", tags=["Resultados de Aprendizaje"])
app.include_router(festivos.router, prefix="/festivos", tags=["Festivos"])
app.include_router(notificacion.router, prefix="/notificaciones", tags=["Notificaciones"])

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
