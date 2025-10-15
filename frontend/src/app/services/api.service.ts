import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from './auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl + '/api/';

  constructor(private http: HttpClient, private authService: AuthService, private snackBar: MatSnackBar) { }

  public getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Token ${token}`,
    });
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred!';
    if (error.error instanceof ErrorEvent) {
      // Client-side errors
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side errors
      if (error.status === 0) {
        errorMessage = 'Cannot connect to the server. Please check your internet connection or try again later.';
      } else if (error.error && error.error.detail) {
        errorMessage = `Error ${error.status}: ${error.error.detail}`;
      } else if (error.error && typeof error.error === 'object') {
        errorMessage = `Error ${error.status}: ${JSON.stringify(error.error)}`;
      } else {
        errorMessage = `Error ${error.status}: ${error.message}`;
      }
    }
    this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
    return throwError(() => new Error(errorMessage));
  }

  getFinancialSummary(start_date?: string, end_date?: string): Observable<any> {
    let httpParams = new HttpParams();
    if (start_date) {
      httpParams = httpParams.set('start_date', start_date);
    }
    if (end_date) {
      httpParams = httpParams.set('end_date', end_date);
    }
    return this.http.get(`${this.baseUrl}summary/`, { headers: this.getHeaders(), params: httpParams })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  public getBudgets(params?: any): Observable<any> {
    let httpParams = new HttpParams();
    if (params) {
      for (const key in params) {
        if (params.hasOwnProperty(key)) {
          httpParams = httpParams.set(key, params[key]);
        }
      }
    }
    return this.http.get(`${this.baseUrl}budgets/`, { headers: this.getHeaders(), params: httpParams })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  public getCategories(params?: any): Observable<any> {
    let httpParams = new HttpParams();
    if (params) {
      for (const key in params) {
        if (params.hasOwnProperty(key)) {
          httpParams = httpParams.set(key, params[key]);
        }
      }
    }
    return this.http.get(`${this.baseUrl}categories/`, { headers: this.getHeaders(), params: httpParams })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  public getTransactions(params?: any): Observable<any> {
    let httpParams = new HttpParams();
    if (params) {
      for (const key in params) {
        if (params.hasOwnProperty(key)) {
          httpParams = httpParams.set(key, params[key]);
        }
      }
    }
    return this.http.get(`${this.baseUrl}transactions/`, { headers: this.getHeaders(), params: httpParams })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  addTransaction(transaction: any): Observable<any> {
    return this.http.post(`${this.baseUrl}transactions/`, transaction, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  updateTransaction(id: number, transaction: any): Observable<any> {
    return this.http.put(`${this.baseUrl}transactions/${id}/`, transaction, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  deleteTransaction(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}transactions/${id}/`, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  updateUserProfile(profile: any): Observable<any> {
    return this.http.put(`${this.baseUrl}profile/`, profile, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  signup(userData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}signup/`, userData)
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  login(credentials: any): Observable<any> {
    return this.http.post(`${this.baseUrl}login/`, credentials)
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

public getBudgetComparison(month: string, params?: any): Observable<any> {
    let httpParams = new HttpParams();
    if (params) {
      for (const key in params) {
        if (params.hasOwnProperty(key)) {
          httpParams = httpParams.set(key, params[key]);
        }
      }
    }
    httpParams = httpParams.set('month', month);
    return this.http.get(`${this.baseUrl}budget-comparison/`, { headers: this.getHeaders(), params: httpParams })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  public deleteBudget(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}budgets/${id}/`, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  public deleteCategory(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}categories/${id}/`, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  public createCategory(categoryData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}categories/`, categoryData, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  public updateCategory(id: number, categoryData: any): Observable<any> {
    return this.http.put(`${this.baseUrl}categories/${id}/`, categoryData, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  public updateBudget(id: number, budgetData: any): Observable<any> {
    return this.http.put(`${this.baseUrl}budgets/${id}/`, budgetData, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  public createBudget(budgetData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}budgets/`, budgetData, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  public createTransaction(transactionData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}transactions/`, transactionData, { headers: this.getHeaders() })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }
}