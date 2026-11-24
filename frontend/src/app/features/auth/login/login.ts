import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class LoginComponent implements OnInit {
  readonly loginForm = inject(FormBuilder).nonNullable.group({
    username: ['', Validators.required],
    password: ['', Validators.required]
  });
  cargando = false;
  errorMensaje = '';
  mostrarPassword = false;
  returnUrl = '/panel';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    if (this.authService.estaAutenticado()) {
      this.router.navigate(['/panel']);
      return;
    }

    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/panel';
  }

  get usernameInvalido(): boolean {
    const control = this.loginForm.get('username');
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  get passwordInvalido(): boolean {
    const control = this.loginForm.get('password');
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  toggleMostrarPassword(): void {
    this.mostrarPassword = !this.mostrarPassword;
  }

  onSubmit(): void {
    if (this.cargando) return;

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.cargando = true;
    this.errorMensaje = '';

    this.authService.login(this.loginForm.getRawValue()).subscribe({
      next: () => {
        this.cargando = false;
        this.router.navigateByUrl(this.returnUrl);
      },
      error: (err: HttpErrorResponse) => {
        this.cargando = false;
        if (err.status === 401) {
          this.errorMensaje = 'Usuario o contraseña incorrectos.';
        } else if (err.status === 0 || err.status >= 500) {
          this.errorMensaje = 'No se pudo conectar con el servidor. Intenta nuevamente.';
        } else {
          this.errorMensaje = 'No fue posible iniciar sesión. Intenta nuevamente.';
        }
      }
    });
  }
}
