import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-navigation',
  standalone: true,
  imports: [RouterLink, CommonModule],
  templateUrl: './navigation.component.html',
  styleUrl: './navigation.component.css'
})
export class NavigationComponent {
  mobileMenuOpen = false;

  constructor(private router: Router) { }

  logout() {
    // Implement actual logout logic here (e.g., clear tokens, call auth service)
    console.log('User logged out');
    this.router.navigate(['/auth/login']);
  }

  toggleMobileMenu() {
    this.mobileMenuOpen = !this.mobileMenuOpen;
  }
}