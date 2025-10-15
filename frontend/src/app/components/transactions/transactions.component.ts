import { Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatRadioModule } from '@angular/material/radio';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { HttpErrorResponse } from '@angular/common/http';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { TransactionFormDialogComponent } from './transaction-form-dialog/transaction-form-dialog.component';
import { ConfirmationDialogComponent } from './confirmation-dialog/confirmation-dialog.component';

@Component({
  selector: 'app-transactions',
  templateUrl: './transactions.component.html',
  styleUrls: ['./transactions.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatIconModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatProgressSpinnerModule,
    MatRadioModule,
    MatDialogModule,
  ]
})
export class TransactionsComponent implements OnInit {
  transactions: any[] = [];
  categories: any[] = [];
  displayedColumns: string[] = ['date', 'description', 'category', 'type', 'amount', 'actions'];
  loading = false;
  errorMessage: string | null = null;
  filterForm: FormGroup;
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;
  
  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private dialog: MatDialog
  ) {
    this.filterForm = this.fb.group({
      start_date: [''],
      end_date: [''],
      category: [''],
      transaction_type: ['']
    });
  }

  ngOnInit(): void {
    this.loadCategories();
    this.loadTransactions();
  }

  ngAfterViewInit() {
    this.paginator.page.subscribe(() => this.loadTransactions());
    this.sort.sortChange.subscribe(() => {
      this.paginator?.firstPage();
      this.loadTransactions();
    });
  }

  loadCategories(): void {
    this.apiService.getCategories().subscribe({
      next: (data: { results: any[]; }) => {
        this.categories = data.results;
      },
      error: (error: any) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  loadTransactions(filters?: any): void {
    this.loading = true;
    this.errorMessage = null; // Clear any previous errors
    const params: any = {
      page: this.paginator ? this.paginator.pageIndex + 1 : 1,
      page_size: this.paginator ? this.paginator.pageSize : 10,
      ordering: this.sort && this.sort.active ? (this.sort.direction === 'desc' ? '-' : '') + this.sort.active : '',
      ...filters
    };
    this.apiService.getTransactions(params).subscribe({
      next: (data: { results: any[]; }) => {
        this.transactions = data.results;
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Error loading transactions:', error);
        this.errorMessage = 'Failed to load transactions. Please try again.';
        this.loading = false;
      }
    });
  }

  openAddTransactionDialog(): void {
    const dialogRef = this.dialog.open(TransactionFormDialogComponent, {
      width: '400px',
      data: { isEditing: false }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadTransactions();
      }
    });
  }

  editTransaction(transaction: any): void {
    const dialogRef = this.dialog.open(TransactionFormDialogComponent, {
      width: '400px',
      data: { isEditing: true, transaction: transaction }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadTransactions();
      }
    });
  }

  deleteTransaction(id: number): void {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Confirm Deletion',
        message: 'Are you sure you want to delete this transaction?'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loading = true; // Set loading state for delete operation
        this.errorMessage = null; // Clear any previous errors
        this.apiService.deleteTransaction(id).subscribe({
          next: () => {
            this.loadTransactions();
            this.loading = false; // Clear loading state
          },
          error: (error: any) => {
            console.error('Error deleting transaction:', error);
            this.errorMessage = 'Failed to delete transaction. Please try again.';
            this.loading = false; // Clear loading state
          }
        });
      }
    });
  }

  applyFilters(): void {
    const filters = this.filterForm.value;
    this.loadTransactions(filters);
  }

  resetFilters(): void {
    this.filterForm.reset();
    this.loadTransactions();
  }
    getCategoryName(category_id: number): string {
    const category = this.categories.find((item: any) => item.id === category_id);
    return category ? category.name : 'Unknown';
  }

  onSortChange(sort: any) {
    this.sort.active = sort.active;
    this.sort.direction = sort.direction;
    this.loadTransactions();
  }
}