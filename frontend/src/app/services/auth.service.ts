import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Router } from '@angular/router';
import { tap, map } from 'rxjs/operators';

interface AuthResponse {
  token: string;
  username: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private tokenSubject: BehaviorSubject<string | null> = new BehaviorSubject<string | null>(localStorage.getItem('token'));
  public token$: Observable<string | null> = this.tokenSubject.asObservable();
  private usernameSubject = new BehaviorSubject<string | null>(localStorage.getItem('username'));
  public username$ = this.usernameSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    // The tokenSubject is now initialized directly from localStorage, so this check is no longer needed.
    const token = localStorage.getItem('token');
    if (token) {
      this.setToken(token);
    }
  }

  public setUsername(username: string): void {
    localStorage.setItem('username', username);
    this.usernameSubject.next(username);
  }

  signup(userData: any): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${environment.apiUrl}/api/signup/`, userData).pipe(
      tap(response => {
        if (response.token && response.username) {
          this.setToken(response.token);
          this.setUsername(response.username);
        }
      })
    );
  }

  loginUser(userData: any): Observable<any> {
    return this.http.post(`${environment.apiUrl}/api/login/`, userData);
  }
  
  isLoggedIn(): Observable<boolean> {
    return this.token$.pipe(
      map(token => !!token)
    );
  }

  logout(): void {
    localStorage.removeItem('token');
    this.tokenSubject.next(null);
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  setToken(token: string): void {
    localStorage.setItem('token', token);
    this.tokenSubject.next(token);
  }
}