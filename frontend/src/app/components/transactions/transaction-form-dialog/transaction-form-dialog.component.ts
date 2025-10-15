import { Component, OnInit, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../services/api.service';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatRadioModule } from '@angular/material/radio';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { HttpErrorResponse } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-transaction-form-dialog',
  templateUrl: './transaction-form-dialog.component.html',
  styleUrls: ['./transaction-form-dialog.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatRadioModule,
    MatProgressSpinnerModule,
    MatIconModule
  ]
})
export class TransactionFormDialogComponent implements OnInit {
  transactionForm: FormGroup;
  categories: any[] = [];
  isSubmitting = false;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<TransactionFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.transactionForm = this.fb.group({
      amount: ['', [Validators.required, Validators.min(0.01)]],
      description: ['', Validators.required],
      category: ['', Validators.required],
      date: ['', Validators.required],
      transaction_type: ['expense', Validators.required]
    });
  }

  ngOnInit(): void {
    this.loadCategories();
    if (this.data.isEditing && this.data.transaction) {
      this.patchForm(this.data.transaction);
    }
  }

  loadCategories(): void {
    this.apiService.getCategories().subscribe({
      next: (data) => {
        this.categories = data.results;
      },
      error: (error) => {
        console.error('Error loading categories:', error);
        this.snackBar.open('Failed to load categories.', 'Close', { duration: 3000 });
      }
    });
  }

  patchForm(transaction: any): void {
    this.transactionForm.patchValue({
      amount: transaction.amount,
      description: transaction.description,
      category: transaction.category.id,
      date: new Date(transaction.date),
      transaction_type: transaction.transaction_type
    });
  }

  onSubmit(): void {
    if (this.transactionForm.invalid) {
      return;
    }

    this.isSubmitting = true;
    this.errorMessage = null;
    let transactionData = this.transactionForm.value;
    const updatedDate = new Date(transactionData.date);
    transactionData.date = `${updatedDate.getFullYear()}-${updatedDate.getMonth() + 1}-${updatedDate.getDate()}`;

    if (this.data.isEditing && this.data.transaction && this.data.transaction.id) {
      this.apiService.updateTransaction(this.data.transaction.id, transactionData).subscribe({
        next: () => {
          this.snackBar.open('Transaction updated successfully!', 'Close', { duration: 3000 });
          this.dialogRef.close(true);
        },
        error: (error: HttpErrorResponse) => {
          console.error('Error updating transaction:', error);
          this.errorMessage = 'Failed to update transaction. Please try again.';
          this.snackBar.open('Failed to update transaction.', 'Close', { duration: 3000 });
          this.isSubmitting = false;
        }
      });
    } else {
      this.apiService.createTransaction(transactionData).subscribe({
        next: () => {
          this.snackBar.open('Transaction added successfully!', 'Close', { duration: 3000 });
          this.dialogRef.close(true);
        },
        error: (error: HttpErrorResponse) => {
          console.error('Error creating transaction:', error);
          this.errorMessage = 'Failed to create transaction. Please try again.';
          this.snackBar.open('Failed to create transaction.', 'Close', { duration: 3000 });
          this.isSubmitting = false;
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }
}
