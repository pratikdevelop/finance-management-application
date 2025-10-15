import { Component, OnInit, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';



@Component({
  selector: 'app-budget-form-dialog',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatIconModule, MatCardModule, MatFormFieldModule, MatInputModule, MatSelectModule, MatButtonModule, MatProgressSpinnerModule, MatDialogModule, MatSnackBarModule],
  templateUrl: './budget-form-dialog.component.html',
  styleUrl: './budget-form-dialog.component.css'
})
export class BudgetFormDialogComponent implements OnInit {
  budgetForm: FormGroup;
  isEditing = false;
  isSubmitting = false;
  errorMessage: string | null = null;
  categories: any[] = [];

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<BudgetFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private snackBar: MatSnackBar
  ) {
    this.budgetForm = this.fb.group({
      amount: ['', [Validators.required, Validators.min(0.01)]],
      category: ['', Validators.required],
      month: ['', Validators.required],
      year: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    this.categories = this.data.categories;
    if (this.data.budget) {
      this.isEditing = true;
      this.budgetForm.patchValue({
        amount: this.data.budget.amount,
        category: this.data.budget.category,
        month: this.data.budget.month,
        year: this.data.budget.year
      });
    } else {
      const currentDate = new Date();
      this.budgetForm.patchValue({
        month: (currentDate.getMonth() + 1).toString().padStart(2, '0'),
        year: currentDate.getFullYear().toString()
      });
    }
  }

  onSubmit(): void {
    console.log('BudgetFormDialog: onSubmit called');
    if (this.budgetForm.invalid) {
      console.log('BudgetFormDialog: Form is invalid', this.budgetForm.errors);
      return;
    }

    this.isSubmitting = true;
    this.errorMessage = null;
    console.log('BudgetFormDialog: Closing dialog with result', this.budgetForm.value);
    this.dialogRef.close(this.budgetForm.value);
  }

  onCancel(): void {
    console.log('BudgetFormDialog: Cancelling dialog');
    this.dialogRef.close();
  }
  showSnackBar(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
    });
  }
}
