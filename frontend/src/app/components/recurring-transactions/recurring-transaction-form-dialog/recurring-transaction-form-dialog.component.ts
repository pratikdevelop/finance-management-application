import { Component, OnInit, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { RecurringTransactionsService } from '../../../services/recurring-transactions.service';
import { ApiService } from '../../../services/api.service';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-recurring-transaction-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatIconModule,
  ],
  templateUrl: './recurring-transaction-form-dialog.component.html',
  styleUrls: ['./recurring-transaction-form-dialog.component.css']
})
export class RecurringTransactionFormDialogComponent implements OnInit {
  recurringTransactionForm: FormGroup;
  categories: any[] = [];
  frequencies: string[] = ['daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly'];
  isEditing: boolean;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<RecurringTransactionFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private recurringTransactionsService: RecurringTransactionsService,
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) {
    this.isEditing = data.isEditing;
    this.recurringTransactionForm = this.fb.group({
      amount: [data.transaction?.amount || '', [Validators.required, Validators.min(0.01)]],
      description: [data.transaction?.description || '', Validators.required],
      category: [data.transaction?.category || '', Validators.required],
      frequency: [data.transaction?.frequency || '', Validators.required],
      start_date: [data.transaction?.start_date ? new Date(data.transaction.start_date) : '', Validators.required],
      end_date: [data.transaction?.end_date ? new Date(data.transaction.end_date) : null],
    });
  }

  ngOnInit(): void {
    this.loadCategories();
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

  onSubmit(): void {
    if (this.recurringTransactionForm.invalid) {
      return;
    }

    const formData = { ...this.recurringTransactionForm.value };
    formData.start_date = this.formatDate(formData.start_date);
    formData.end_date = formData.end_date ? this.formatDate(formData.end_date) : null;

    if (this.isEditing && this.data.transaction?.id) {
      this.recurringTransactionsService.updateRecurringTransaction(this.data.transaction.id, formData).subscribe({
        next: () => {
          this.snackBar.open('Recurring transaction updated successfully!', 'Close', { duration: 3000 });
          this.dialogRef.close(true);
        },
        error: (error) => {
          console.error('Error updating recurring transaction:', error);
          this.snackBar.open('Failed to update recurring transaction.', 'Close', { duration: 3000 });
        }
      });
    } else {
      this.recurringTransactionsService.createRecurringTransaction(formData).subscribe({
        next: () => {
          this.snackBar.open('Recurring transaction created successfully!', 'Close', { duration: 3000 });
          this.dialogRef.close(true);
        },
        error: (error) => {
          console.error('Error creating recurring transaction:', error);
          this.snackBar.open('Failed to create recurring transaction.', 'Close', { duration: 3000 });
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  private formatDate(date: Date): string {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = ('0' + (d.getMonth() + 1)).slice(-2);
    const day = ('0' + d.getDate()).slice(-2);
    return `${year}-${month}-${day}`;
  }
  getFrequencyIcon(frequency: string): string {
  switch(frequency) {
    case 'daily': return 'today';
    case 'weekly': return 'date_range';
    case 'monthly': return 'event_note';
    case 'yearly': return 'calendar_today';
    default: return 'update';
  }
}
}