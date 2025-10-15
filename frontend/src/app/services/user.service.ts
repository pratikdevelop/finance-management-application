import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'http://localhost:8000/api'; // Adjust your API URL as needed

  constructor(private http: HttpClient, private apiService: ApiService) { }

  updateProfile(profileData: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/profile/`, profileData, { headers: this.apiService.getHeaders() });
  }

  updateSettings(settingsData: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/settings/`, settingsData, { headers: this.apiService.getHeaders() });
  }

  getProfile(): Observable<any> {
    return this.http.get(`${this.apiUrl}/profile/`, { headers: this.apiService.getHeaders() });
  }

  getSettings(): Observable<any> {
    return this.http.get(`${this.apiUrl}/settings/`, { headers: this.apiService.getHeaders() });
  }
}