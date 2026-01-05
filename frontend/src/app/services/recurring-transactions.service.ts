import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RecurringTransactionsService {
  private apiUrl = `${environment.apiUrl}api/recurring-transactions/`;

  constructor(private http: HttpClient, private apiService: ApiService) { }

  getRecurringTransactions(): Observable<any> {
    return this.http.get(this.apiUrl, { headers: this.apiService.getHeaders() });
  }

  createRecurringTransaction(data: any): Observable<any> {
    return this.http.post(this.apiUrl, data, { headers: this.apiService.getHeaders() });
  }

  getRecurringTransactionById(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}${id}/`, { headers: this.apiService.getHeaders() });
  }

  updateRecurringTransaction(id: number, data: any): Observable<any> {
    return this.http.put(`${this.apiUrl}${id}/`, data, { headers: this.apiService.getHeaders() });
  }

  deleteRecurringTransaction(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}${id}/`, { headers: this.apiService.getHeaders() });
  }

  toggleActive(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}${id}/toggle_active/`, {}, { headers: this.apiService.getHeaders() });
  }
}