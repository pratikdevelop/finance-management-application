import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatTooltipModule } from '@angular/material/tooltip';
import { environment } from '../../../environments/environment';

interface Category {
  id: number;
  name: string;
  type: 'income' | 'expense';
}

interface Budget {
  id: number;
  category: number;
  amount: number;
  month: number;
  year: number;
  category_name?: string;
}

interface ComparisonData {
  category_id: number;
  category_name: string;
  budget_amount: number;
  actual_amount: number;
  difference: number;
  year: number;
  month: number;
}

@Component({
  selector: 'app-budgets',
  templateUrl: './budgets.component.html',
  styleUrls: ['./budgets.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatProgressBarModule,
    MatPaginatorModule,
    MatSortModule,
    MatProgressSpinnerModule,
    MatDialogModule,
    MatSnackBarModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatTooltipModule
  ]
})
export class BudgetsComponent implements OnInit {
  budgets: Budget[] = [];
  categories: Category[] = [];
  newBudget: Partial<Budget> = {};
  selectedMonth: number;
  selectedYear: number;
  comparisonData: ComparisonData[] = [];
  filterForm: FormGroup;
  loading: boolean = false;
  errorMessage: string = '';
  pageIndex: number = 0;
  pageSize: number = 5;
  totalItems: number = 0;
  displayedColumns: string[] = ['category', 'period', 'allocatedAmount', 'spentAmount', 'remainingAmount', 'progress', 'status', 'actions'];

  constructor(private http: HttpClient, private authService: AuthService) {
    const today = new Date();
    this.selectedMonth = today.getMonth() + 1; // Month is 0-indexed
    this.selectedYear = today.getFullYear();
    this.filterForm = new FormGroup({
      category: new FormControl(''),
      period: new FormControl(new Date())
    });
  }

  ngOnInit(): void {
    this.loadCategories();
    this.loadBudgets();
    this.loadBudgetComparison();
  }

  onMonthSelected(event: any, datepicker: any) {
    this.filterForm.controls['period'].setValue(event);
    datepicker.close();
  }

  applyFilter(): void {
    this.loadBudgets();
    this.loadBudgetComparison();
  }

  clearFilter(): void {
    this.filterForm.controls['category'].setValue('');
    this.filterForm.controls['period'].setValue(new Date());
    this.selectedMonth = new Date().getMonth() + 1;
    this.selectedYear = new Date().getFullYear();
    this.loadBudgets();
    this.loadBudgetComparison();
  }

  isFilterActive(): boolean {
    return this.filterForm.controls['category'].value !== '' ||
           (this.filterForm.controls['period'].value &&
            (this.filterForm.controls['period'].value.getMonth() + 1 !== new Date().getMonth() + 1 ||
             this.filterForm.controls['period'].value.getFullYear() !== new Date().getFullYear()));
  }

  onSortChange(event: any): void {
    // Implement sorting logic here if needed
    console.log('Sort change event:', event);
  }

  onPageChange(event: any): void {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadBudgets();
  }

  getCategoryName(categoryId: number): string {
    return this.categories.find(cat => cat.id === categoryId)?.name || 'N/A';
  }

  getMonthName(monthNumber: number): string {
    const date = new Date();
    date.setMonth(monthNumber - 1);
    return date.toLocaleString('default', { month: 'long' });
  }

  getRemainingAmount(budget: Budget): number {
    const spent = this.getSpentAmount(budget);
    return budget.amount - spent;
  }

  getSpentPercentage(budget: Budget): number {
    const spent = this.getSpentAmount(budget);
    if (budget.amount === 0) {
      return 0;
    }
    return (spent / budget.amount) * 100;
  }

  getBudgetStatus(budget: Budget): 'on-track' | 'warning' | 'exceeded' {
    const spent = this.getSpentAmount(budget);
    const percentage = (spent / budget.amount) * 100;

    if (percentage >= 100) {
      return 'exceeded';
    } else if (percentage >= 80) {
      return 'warning';
    } else {
      return 'on-track';
    }
  }

  loadCategories(): void {
    const token = this.authService.getToken();
    this.http.get<any>(`${environment.apiUrl}/api/categories/`, {
      headers: { Authorization: `Token ${token}` }
    }).subscribe(
      data => {
        this.categories = data.results.filter((category: any) => category.type === 'expense');
      },
      error => {
        console.error('Error loading categories:', error);
      }
    );
  }

  loadBudgets(): void {
    const token = this.authService.getToken();
    this.http.get<any>(`${environment.apiUrl}/api/budgets/`, {
      headers: { Authorization: `Token ${token}` },
      params: {
        month: this.selectedMonth.toString(),
        year: this.selectedYear.toString(),
        page: (this.pageIndex + 1).toString(),
        page_size: this.pageSize.toString()
      }
    }).subscribe(
      data => {
        this.budgets = data.results.map((budget: any) => ({
          ...budget,
          category_name: this.categories.find(cat => cat.id === budget.category)?.name
        }));
        this.totalItems = data.count;
      },
      error => {
        console.error('Error loading budgets:', error);
      }
    );
  }

  loadBudgetComparison(): void {
    const token = this.authService.getToken();
    this.http.get<ComparisonData[]>(`${environment.apiUrl}/api/budget-comparison/`, {
      headers: { Authorization: `Token ${token}` },
      params: { month: `${this.selectedYear}-${this.formatMonth(this.selectedMonth)}` }
    }).subscribe(
      data => {
        console.log('Comparison Data:', data); // Add this line
        this.comparisonData = data;
      },
      error => {
        console.error('Error loading budget comparison:', error);
      }
    );
  }

  getSpentAmount(budget: Budget): number {
    console.log(
      budget
    );
    
    const comparison = this.comparisonData.find(item =>
      item.category_id === budget.category &&
      Number(item.year) === Number(budget.year) &&
      Number(item.month) === Number(budget.month)
    );
    console.log(comparison);
    
    return comparison ? comparison.actual_amount : 0;
  }

  getProgressBarValue(budget: Budget): number {
    const spent = this.getSpentAmount(budget);
    if (budget.amount === 0) {
      return 0;
    }
    return (spent / budget.amount) * 100;
  }

  getProgressBarClass(budget: Budget): string {
    const value = this.getProgressBarValue(budget);
    if (value < 80) {
      return 'progress-green';
    } else if (value < 100) {
      return 'progress-yellow';
    } else {
      return 'progress-red';
    }
  }

  addBudget(): void {
    const token = this.authService.getToken();
    if (this.newBudget.category && this.newBudget.amount) {
      this.newBudget.month = this.selectedMonth;
      this.newBudget.year = this.selectedYear;
      this.http.post<Budget>(`${environment.apiUrl}/api/budgets/`, this.newBudget, {
        headers: { Authorization: `Token ${token}` }
      }).subscribe(
        response => {
          this.loadBudgets();
          this.loadBudgetComparison();
          this.newBudget = {}; // Clear form
        },
        error => {
          console.error('Error adding budget:', error);
        }
      );
    }
  }

  updateBudget(budget: Budget): void {
    const token = this.authService.getToken();
    this.http.put<Budget>(`${environment.apiUrl}/api/budgets/${budget.id}/`, budget, {
      headers: { Authorization: `Token ${token}` }
    }).subscribe(
      response => {
        this.loadBudgets();
        this.loadBudgetComparison();
      },
      error => {
        console.error('Error updating budget:', error);
      }
    );
  }

  deleteBudget(id: number): void {
    const token = this.authService.getToken();
    this.http.delete(`${environment.apiUrl}/api/budgets/${id}/`, {
      headers: { Authorization: `Token ${token}` }
    }).subscribe(
      response => {
        this.loadBudgets();
        this.loadBudgetComparison();
      },
      error => {
        console.error('Error deleting budget:', error);
      }
    );
  }

  onMonthChange(event: Event): void {
    this.selectedMonth = +(event.target as HTMLSelectElement).value;
    this.loadBudgets();
    this.loadBudgetComparison();
  }

  onYearChange(event: Event): void {
    this.selectedYear = +(event.target as HTMLSelectElement).value;
    this.loadBudgets();
    this.loadBudgetComparison();
  }

  formatMonth(month: number): string {
    return month < 10 ? `0${month}` : `${month}`;
  }

  getYears(): number[] {
    const currentYear = new Date().getFullYear();
    return Array.from({ length: 5 }, (_, i) => currentYear - 2 + i);
  }

  editBudget(budget: Budget): void {
    // Implement edit budget logic here
    console.log('Edit budget:', budget);
  }
}


