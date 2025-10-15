import { Component, OnInit, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner'; // Add this line
import { ApiService } from '../../../services/api.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatIcon, MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-category-form-dialog',
  templateUrl: './category-form-dialog.component.html',
  styleUrls: ['./category-form-dialog.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatDialogModule,
    MatProgressSpinnerModule ,// Add this line,
    MatIconModule
  ]
})
export class CategoryFormDialogComponent implements OnInit {
  categoryForm: FormGroup;
  isEditing: boolean;
  loading = false;
  isSubmitting = false; // Add this line
  errorMessage: string | null = null; // Add this line

  constructor(
    public dialogRef: MatDialogRef<CategoryFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private fb: FormBuilder,
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) {
    this.isEditing = data.isEditing;
    this.categoryForm = this.fb.group({
      name: [data.category?.name || '', [Validators.required, Validators.minLength(2)]],
      type: [data.category?.type || 'expense', [Validators.required]],
      description: [data.category?.description || ''],
      color: [data.category?.color || '']
    });
  }

  ngOnInit(): void {}

  onCancel(): void {
    this.dialogRef.close();
  }

  onSubmit(): void {
    if (this.categoryForm.invalid) {
      return;
    }
    this.loading = true;
    this.isSubmitting = true; // Set to true on submission
    this.errorMessage = null; // Clear previous errors
    const categoryData = this.categoryForm.value;

    if (this.isEditing) {
      this.apiService.updateCategory(this.data.category.id, categoryData).subscribe({
        next: (response) => {
          this.snackBar.open('Category updated successfully!', 'Close', { duration: 3000 });
          this.dialogRef.close({ ...response, isEditing: true });
          this.isSubmitting = false; // Set to false on success
        },
        error: (error) => {
          console.error('Error updating category:', error);
          this.errorMessage = 'Failed to update category.'; // Set error message
          this.snackBar.open('Failed to update category.', 'Close', { duration: 3000 });
          this.loading = false;
          this.isSubmitting = false; // Set to false on error
        }
      });
    } else {
      this.apiService.createCategory(categoryData).subscribe({
        next: (response) => {
          this.snackBar.open('Category added successfully!', 'Close', { duration: 3000 });
          this.dialogRef.close({ ...response, isEditing: false });
          this.isSubmitting = false; // Set to false on success
        },
        error: (error) => {
          console.error('Error creating category:', error);
          this.errorMessage = 'Failed to add category.'; // Set error message
          this.snackBar.open('Failed to add category.', 'Close', { duration: 3000 });
          this.loading = false;
          this.isSubmitting = false; // Set to false on error
        }
      });
    }
  }
}