export type RolUsuario = 'OPERADOR' | 'ADMINISTRADOR';

export interface UsuarioSesion {
  id: string;
  username: string;
  nombreCompleto: string;
  rol: RolUsuario;
  token?: string;
}
