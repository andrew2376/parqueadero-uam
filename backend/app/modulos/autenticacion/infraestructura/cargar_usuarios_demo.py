from collections.abc import Mapping
from getpass import getpass
from os import getenv
from sys import stderr

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.configuracion import obtener_configuracion
from app.modulos.autenticacion.infraestructura.password_hasher_argon2 import PasswordHasherArgon2
from app.modulos.autenticacion.infraestructura.usuarios_demo import USUARIOS_DEMO


def cargar_usuarios_demo(sesion: Session, passwords: Mapping[str, str]) -> int:
    from app.modulos.autenticacion.infraestructura.usuario_modelo import UsuarioModelo

    hasher = PasswordHasherArgon2()
    filas = []
    for demo in USUARIOS_DEMO:
        password = passwords.get(demo.username)
        if not password or not password.strip():
            raise ValueError(f"Falta la contraseña de demostración para {demo.username}.")
        filas.append(
            {
                "id": demo.id,
                "username": demo.username,
                "nombre_completo": demo.nombre_completo,
                "rol": demo.rol.value,
                "password_hash": hasher.hashear(password),
            }
        )

    insertar = insert(UsuarioModelo).values(filas).on_conflict_do_nothing()
    ids_insertados = sesion.scalars(insertar.returning(UsuarioModelo.id)).all()
    for demo in USUARIOS_DEMO:
        existente = sesion.get(UsuarioModelo, demo.id)
        if existente is None or existente.username != demo.username:
            raise ValueError(f"El UUID o nombre de usuario de {demo.username} está en uso.")

    return len(ids_insertados)


def main() -> int:
    try:
        configuracion = obtener_configuracion()
        if configuracion.entorno != "desarrollo":
            raise ValueError("La carga de usuarios demo requiere ENTORNO=desarrollo.")

        url = make_url(configuracion.url_base_datos)
        if url.get_backend_name() != "postgresql":
            raise ValueError("La carga de usuarios demo requiere una URL de PostgreSQL.")

        passwords = {
            demo.username: getenv(f"AUTH_DEMO_PASSWORD_{demo.username.upper()}")
            or getpass(f"Contraseña demo para {demo.username}: ")
            for demo in USUARIOS_DEMO
        }
        motor = create_engine(url, hide_parameters=True)
        try:
            with Session(motor) as sesion, sesion.begin():
                insertados = cargar_usuarios_demo(sesion, passwords)
        finally:
            motor.dispose()
    except ValidationError as error:
        campos = ", ".join(
            str(item["loc"][0]).upper() for item in error.errors(include_input=False)
        )
        print(f"Revisa las variables de configuración: {campos}.", file=stderr)
        return 1
    except ValueError as error:
        print(f"Configuración o carga demo inválida: {error}", file=stderr)
        return 1
    except SQLAlchemyError:
        print("No se pudo cargar usuarios. Revisa la conexión y la migración de S115.", file=stderr)
        return 1

    print(f"Carga demo completada. Usuarios nuevos: {insertados}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
