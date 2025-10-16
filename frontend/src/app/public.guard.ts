import { CanActivateFn, Router, UrlTree } from '@angular/router';
import { inject, Injectable } from '@angular/core';
import { AuthService } from './services/auth.service';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class PublicGuard {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(): Observable<boolean | UrlTree> {
    return this.authService.isLoggedIn().pipe(
      map(isLoggedIn => {
        if (isLoggedIn) {
          return this.router.createUrlTree(['/dashboard']);
        }
        return true;
      })
    );
  }
}

export const publicGuard: CanActivateFn = (route, state) => {
  return inject(PublicGuard).canActivate();
};