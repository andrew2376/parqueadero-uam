
import httpx

from app.configuracion import Configuracion


class MercadoPagoError(Exception):
    """Error controlado al comunicarse con Mercado Pago."""


class MercadoPagoCliente:
    def __init__(self, configuracion: Configuracion):
        self.access_token = configuracion.mercado_pago_access_token
        self.base_url = configuracion.mercado_pago_base_url.rstrip("/")

    def _obtener_headers(
        self, clave_idempotencia: str | None = None
    ) -> dict[str, str]:
        if not self.access_token:
            raise MercadoPagoError(
                "No está configurado el Access Token de Mercado Pago."
            )

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        if clave_idempotencia:
            headers["X-Idempotency-Key"] = clave_idempotencia

        return headers

    def crear_orden(
        self, datos: dict, clave_idempotencia: str
    ) -> dict:
        url = f"{self.base_url}/v1/orders"

        try:
            respuesta = httpx.post(
                url,
                headers=self._obtener_headers(clave_idempotencia),
                json=datos,
                timeout=20.0,
            )
            respuesta.raise_for_status()
            return respuesta.json()

        except httpx.HTTPStatusError as error:
            raise MercadoPagoError(
                "Mercado Pago rechazó la creación de la orden. "
                f"Código HTTP: {error.response.status_code}."
            ) from error

        except httpx.RequestError as error:
            raise MercadoPagoError(
                "No fue posible conectar con Mercado Pago."
            ) from error

    def consultar_orden(self, proveedor_order_id: str) -> dict:
        url = f"{self.base_url}/v1/orders/{proveedor_order_id}"

        try:
            respuesta = httpx.get(
                url,
                headers=self._obtener_headers(),
                timeout=20.0,
            )
            respuesta.raise_for_status()
            return respuesta.json()

        except httpx.HTTPStatusError as error:
            raise MercadoPagoError(
                "No fue posible consultar la orden en Mercado Pago. "
                f"Código HTTP: {error.response.status_code}."
            ) from error

        except httpx.RequestError as error:
            raise MercadoPagoError(
                "No fue posible conectar con Mercado Pago."
            ) from error
