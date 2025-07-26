
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.dependencies import authenticate_user
from app.schemas.auth import ResponseLoggin, ForgotPasswordRequest, ForgotPasswordResponse, ValidateResetTokenRequest, ValidateResetTokenResponse, ResetPasswordSchema, ResetPasswordResponse
from app.crud.users import get_user_by_email, reset_password, get_user_by_id
from core.security import create_access_token, create_reset_password_token, verify_reset_password_token
from core.database import get_db
from core.email import send_email_async
from core.config import settings
from fastapi.security import OAuth2PasswordRequestForm
import logging
from datetime import datetime
from jose import jwt, JWTError

logger = logging.getLogger(__name__)


router = APIRouter()

@router.post("/token", response_model=ResponseLoggin)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Datos Incorrectos en email o password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id_usuario), "rol":user.id_rol}
    )

    return ResponseLoggin(
        user=user,
        access_token=access_token
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para recuperación de contraseña.
    Envía un correo con enlace de recuperación si el usuario existe.
    """
    try:
        # Buscar usuario por email
        user = get_user_by_email(db, request.email)
        
        # Siempre devolver el mismo mensaje para no revelar si el correo existe
        success_message = "Si el correo electrónico está registrado, recibirás un enlace de recuperación."
        
        if user:
            # Crear token de recuperación de 15 minutos incluyendo password_changed_at
            reset_token = create_reset_password_token(
                user_id=user.id_usuario, 
                expire_minutes=15,
                password_changed_at=user.password_changed_at
            )
            
            # Construir enlace de recuperación usando la URL del frontend configurada
            reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
            
            # Preparar el contenido del correo
            subject = "Recuperación de contraseña - Gestión Formación"
            email_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #2c3e50;">Gestión Formación</h1>
                        </div>
                        
                        <h2 style="color: #2c3e50;">Recuperación de contraseña</h2>
                        
                        <p>Hola <strong>{user.nombre_completo}</strong>,</p>
                        
                        <p>Hemos recibido una solicitud para restablecer tu contraseña. Si no fuiste tú quien realizó esta solicitud, puedes ignorar este correo.</p>
                        
                        <p>Para crear una nueva contraseña, haz clic en el siguiente enlace:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" 
                               style="background-color: #3498db; color: white; padding: 12px 24px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Restablecer contraseña
                            </a>
                        </div>
                        
                        <p><strong>Este enlace expirará en 15 minutos por seguridad.</strong></p>
                        
                        <p>Si el botón no funciona, puedes copiar y pegar el siguiente enlace en tu navegador:</p>
                        <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px;">
                            {reset_url}
                        </p>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                        
                        <p style="color: #666; font-size: 12px; text-align: center;">
                            Este es un mensaje automático, por favor no responda a este correo.<br>
                            © 2025 Gestión Formación. Todos los derechos reservados.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Enviar correo de forma asíncrona
            email_sent = await send_email_async(
                recipients=[request.email],
                subject=subject,
                body=email_body
            )
            
            if email_sent:
                logger.info(f"Correo de recuperación enviado a: {request.email}")
            else:
                logger.error(f"Error al enviar correo de recuperación a: {request.email}")
                # No revelamos el error al usuario por seguridad
        else:
            # Usuario no existe, pero no lo revelamos
            logger.info(f"Intento de recuperación para email no registrado: {request.email}")
        
        return ForgotPasswordResponse(message=success_message)
        
    except Exception as e:
        logger.error(f"Error en forgot_password: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor. Inténtalo de nuevo más tarde."
        )


@router.post("/validate-reset-token", response_model=ValidateResetTokenResponse)
async def validate_reset_token(request: ValidateResetTokenRequest, db: Session = Depends(get_db)):
    """
    Endpoint para validar un token de recuperación de contraseña.
    Útil para verificar si un token es válido antes de mostrar el formulario de nueva contraseña.
    """
    try:
        token_data = verify_reset_password_token(request.token, db)
        
        if token_data:
            return ValidateResetTokenResponse(
                valid=True,
                message="Token válido"
            )
        else:
            return ValidateResetTokenResponse(
                valid=False,
                message="Token inválido o expirado"
            )
            
    except Exception as e:
        logger.error(f"Error al validar token de recuperación: {str(e)}")
        return ValidateResetTokenResponse(
            valid=False,
            message="Error al validar el token"
        )


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password_endpoint(
    request: ResetPasswordSchema,
    db: Session = Depends(get_db)
):
    """
    Endpoint para restablecer contraseña usando un token de recuperación.
    
    Args:
        request: Schema con token y nueva contraseña
        db: Sesión de base de datos
    
    Returns:
        Mensaje de éxito o error
    """
    try:
        # Validaciones básicas
        if not request.token or not request.new_password:
            raise HTTPException(
                status_code=400,
                detail="Token y nueva contraseña son requeridos"
            )
        
        # Validar longitud mínima de contraseña
        if len(request.new_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="La nueva contraseña debe tener al menos 6 caracteres"
            )
        
        # Verificar la validez del token y extraer información
        token_data = verify_reset_password_token(request.token, db)
        if not token_data:
            logger.warning("Intento de reset con token inválido")
            raise HTTPException(
                status_code=400,
                detail="Token inválido o expirado. Solicita un nuevo enlace de recuperación."
            )
        
        user_id = token_data.get("sub")
        token_password_changed_at = token_data.get("password_changed_at")
        
        if not user_id:
            logger.warning("Token sin user_id válido")
            raise HTTPException(
                status_code=400,
                detail="Token inválido. Solicita un nuevo enlace de recuperación."
            )
        
        # Obtener el usuario actual de la base de datos
        current_user = get_user_by_id(db, user_id)
        if not current_user:
            logger.warning(f"Usuario con ID {user_id} no encontrado")
            raise HTTPException(
                status_code=400,
                detail="Usuario no encontrado. Solicita un nuevo enlace de recuperación."
            )
        
        # Verificar que el password_changed_at del token coincida con el de la base de datos
        db_password_changed_at = current_user.password_changed_at
        
        # Convertir ambas fechas a strings para comparación
        if db_password_changed_at and token_password_changed_at:
            # Si ambas fechas existen, deben coincidir
            if hasattr(db_password_changed_at, 'isoformat'):
                db_date_str = db_password_changed_at.isoformat()
            else:
                db_date_str = str(db_password_changed_at)
            
            if db_date_str != token_password_changed_at:
                logger.warning(f"Token inválido: password_changed_at no coincide para usuario {user_id}")
                raise HTTPException(
                    status_code=400,
                    detail="Token inválido: la contraseña ya fue cambiada. Solicita un nuevo enlace de recuperación."
                )
        elif db_password_changed_at is None and token_password_changed_at is not None:
            # Usuario no tiene fecha pero token sí - token inválido
            logger.warning(f"Token inválido: usuario {user_id} no tiene password_changed_at pero token sí")
            raise HTTPException(
                status_code=400,
                detail="Token inválido: la contraseña ya fue cambiada. Solicita un nuevo enlace de recuperación."
            )
        elif db_password_changed_at is not None and token_password_changed_at is None:
            # Usuario tiene fecha pero token no - token inválido
            logger.warning(f"Token inválido: usuario {user_id} tiene password_changed_at pero token no")
            raise HTTPException(
                status_code=400,
                detail="Token inválido: la contraseña ya fue cambiada. Solicita un nuevo enlace de recuperación."
            )
        # Si ambos son None, está permitido (usuario nunca cambió contraseña)
        
        # Llamar a la función CRUD para restablecer contraseña
        result = reset_password(db, request.token, request.new_password)
        
        if result is None:
            # Token inválido, expirado o usuario no encontrado
            logger.warning(f"Intento de reset con token inválido")
            raise HTTPException(
                status_code=400,
                detail="Token inválido o expirado. Solicita un nuevo enlace de recuperación."
            )
        
        if result is True:
            # Éxito
            logger.info("Contraseña restablecida exitosamente")
            return ResetPasswordResponse(
                message="Contraseña actualizada exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.",
                success=True
            )
        else:
            # Caso inesperado
            logger.error("Resultado inesperado de reset_password")
            raise HTTPException(
                status_code=500,
                detail="Error interno del servidor"
            )
            
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        # Manejo de errores inesperados
        logger.error(f"Error inesperado en reset_password_endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor. Inténtalo de nuevo más tarde."
        )

