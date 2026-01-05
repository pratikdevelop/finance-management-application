import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { ApiService } from '../../services/api.service';
import { MatSnackBar } from '@angular/material/snack-bar';

interface Expense {
  description: string;
  amount: number;
  date: string;
  category?: string;
}

interface AnalysisResult {
  expenses: Expense[];
  stats: { [key: string]: { sum: number; count: number } };
  recommendations: string[];
}

@Component({
  selector: 'app-predictive-analytics',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatListModule,
    MatIconModule
  ],
  templateUrl: './predictive-analytics.component.html',
  styleUrl: './predictive-analytics.component.css'
})
export class PredictiveAnalyticsComponent implements OnInit {
  expenses: Expense[] = [{ description: '', amount: 0, date: new Date().toISOString().split('T')[0] }];
  analysisResult: AnalysisResult | null = null;
  loading = false;

  constructor(private apiService: ApiService, private snackBar: MatSnackBar) { }

  ngOnInit(): void {
  }

  addExpense(): void {
    this.expenses.push({ description: '', amount: 0, date: new Date().toISOString().split('T')[0] });
  }

  removeExpense(index: number): void {
    this.expenses.splice(index, 1);
  }

  analyzeExpenses(): void {
    this.loading = true;
    const validExpenses = this.expenses.filter(exp => exp.description && exp.amount > 0);
    if (validExpenses.length === 0) {
      this.snackBar.open('Please add at least one valid expense.', 'Close', { duration: 3000 });
      this.loading = false;
      return;
    }

    this.apiService.analyzeExpenses({ expenses: validExpenses }).subscribe({
      next: (result: AnalysisResult) => {
        this.analysisResult = result;
        this.loading = false;
        this.snackBar.open('Expense analysis complete!', 'Close', { duration: 3000 });
      },
      error: (err) => {
        console.error('Error analyzing expenses:', err);
        this.snackBar.open('Failed to analyze expenses.', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }
}
