import { Routes } from '@angular/router';
import { SignupComponent } from './components/signup/signup.component';
import { LoginComponent } from './components/login/login.component';
import { authGuard } from './auth.guard';
import { publicGuard } from './public.guard';
import { LandingPageComponent } from './landing-page/landing-page.component';

export const routes: Routes = [
  { path: 'auth/signup', 
    component: SignupComponent,
    canActivate: [publicGuard]
   },
  {
    path: 'dashboard', 
    loadComponent: () => import('./dashboard/dashboard.component').then((m) => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: "auth/login",
    loadComponent: () => import('./components/login/login.component').then((m) => m.LoginComponent),
    canActivate: [publicGuard]
  },
  {
    path:'transactions',
    loadComponent:() => import('./components/transactions/transactions.component').then(m => m.TransactionsComponent),
    canActivate: [authGuard]
  },
  {
    path:'profile',
    loadComponent:() => import('./profile/profile.component').then(m => m.ProfileComponent),
    canActivate: [authGuard]
  },
  {
    path: "recurring-transactions",
    loadComponent: () => import('./components/recurring-transactions/recurring-transactions-list.component').then(m => m.RecurringTransactionsListComponent),
    canActivate: [authGuard]
  },
  {
    path: "transactions",
    loadComponent: () => import('./components/transactions/transactions.component').then(m => m.TransactionsComponent),
    canActivate: [authGuard]
  },
  {
    path: "budgets",
    loadComponent: () => import('./components/budgets/budgets.component').then(m => m.BudgetsComponent),
    canActivate: [authGuard]
  },
  {
    path: "categories",
    loadComponent: () => import('./components/categories/categories.component').then(m => m.CategoriesComponent),
    canActivate: [authGuard]
  },
  {
    path: "predictive-analytics",
    loadComponent: () => import('./components/predictive-analytics/predictive-analytics.component').then(m => m.PredictiveAnalyticsComponent),
    canActivate: [authGuard]
  },
  {
    path: '',
    component: LandingPageComponent,
    canActivate: [publicGuard]
  },
  { path: '**', redirectTo: '' }
];
