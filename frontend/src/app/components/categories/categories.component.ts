import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from  '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { HttpErrorResponse } from '@angular/common/http';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CategoryFormDialogComponent } from './category-form-dialog/category-form-dialog.component';
import { ConfirmationDialogComponent } from '../transactions/confirmation-dialog/confirmation-dialog.component';
import { ReactiveFormsModule, FormGroup, FormControl } from '@angular/forms';

@Component({
  selector: 'app-categories',
  templateUrl: './categories.component.html',
  styleUrls: ['./categories.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatTableModule,
    MatIconModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    MatPaginatorModule,
    MatSortModule,
    MatSnackBarModule,
    ReactiveFormsModule
  ]
})
export class CategoriesComponent implements OnInit, AfterViewInit {
  categories: any[] = [];
  displayedColumns: string[] = ['color', 'name', 'type', 'actions'];
  loading = false;
  errorMessage: string | null = null;
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  filterForm = new FormGroup({
    name: new FormControl(''),
    type: new FormControl('')
  });

  constructor(
    private apiService: ApiService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    console.log('CategoriesComponent: ngOnInit called');
    this.filterForm.valueChanges.subscribe(() => {
      this.paginator?.firstPage();
      this.loadCategories();
    });
  }

  ngAfterViewInit() {
    console.log('CategoriesComponent: ngAfterViewInit called');
    console.log('CategoriesComponent: this.sort in ngAfterViewInit (before Promise):', this.sort);
    console.log('CategoriesComponent: this.paginator in ngAfterViewInit (before Promise):', this.paginator);

    Promise.resolve().then(() => {
      console.log('CategoriesComponent: Inside Promise.resolve().then()');
      console.log('CategoriesComponent: this.sort inside Promise:', this.sort);
      console.log('CategoriesComponent: this.paginator inside Promise:', this.paginator);
      this.loadCategories();
      if (this.paginator) {
        this.paginator.page.subscribe(() => this.loadCategories());
      }
      if (this.sort) {
        this.sort.sortChange.subscribe(() => {
          this.paginator.firstPage();
          this.loadCategories();
        });
      }
    });
  }

  loadCategories(): void {
    this.loading = true;
    this.errorMessage = null; // Clear any previous errors
    const params: any = {
      page: this.paginator ? this.paginator.pageIndex + 1 : 1,
      page_size: this.paginator ? this.paginator.pageSize : 10,
      ordering: this.sort && this.sort.active ? (this.sort.direction === 'desc' ? '-' : '') + this.sort.active : '',
    };

    const formValues = this.filterForm.value;
    if (formValues.name) {
      params.name = formValues.name;
    }
    if (formValues.type) {
      params.type = formValues.type;
    }

    this.apiService.getCategories(params).subscribe({
      next: (data) => {
        this.categories = data.results; // Extract categories from the 'results' key
        this.loading = false;
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error loading categories:', error);
        this.errorMessage = 'Failed to load categories. Please try again.';
        this.loading = false;
      }
    });
  }

  openCategoryDialog(category?: any): void {
    const dialogRef = this.dialog.open(CategoryFormDialogComponent, {
      width: '600px',
      data: category ? { category: category, isEditing: true } : { isEditing: false }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadCategories();
        this.snackBar.open(`Category ${result.name} ${result.isEditing ? 'updated' : 'added'} successfully!`, 'Close', { duration: 3000 });
      }
    });
  }

  deleteCategory(id: number): void {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Confirm Deletion',
        message: 'Are you sure you want to delete this category? This will affect all transactions and budgets associated with this category.'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loading = true; // Set loading state for delete operation
        this.errorMessage = null; // Clear any previous errors
        this.apiService.deleteCategory(id).subscribe({
          next: () => {
            this.loadCategories();
            this.loading = false; // Clear loading state
            this.snackBar.open('Category deleted successfully!', 'Close', { duration: 3000 });
          },
          error: (error: HttpErrorResponse) => {
            console.error('Error deleting category:', error);
            this.errorMessage = 'Failed to delete category. Please try again.';
            this.loading = false; // Clear loading state
            this.snackBar.open('Failed to delete category.', 'Close', { duration: 3000 });
          }
        });
      }
    });
  }

  editCategory(category: any): void {
    this.openCategoryDialog(category);
  }
}