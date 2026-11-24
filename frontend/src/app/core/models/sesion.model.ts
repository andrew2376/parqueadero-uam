export type RolUsuario = 'OPERADOR' | 'ADMINISTRADOR';

export interface CredencialesLogin {
  username: string;
  password: string;
}

export interface UsuarioSesion {
  id: string;
  username: string;
  nombreCompleto: string;
  rol: RolUsuario;
  token?: string;
}

export interface RespuestaLogin {
  token: string;
  tipoToken?: string;
  usuario: UsuarioSesion;
}
