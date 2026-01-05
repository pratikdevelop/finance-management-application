import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RecurringTransactionsService } from '../../services/recurring-transactions.service';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RecurringTransactionFormDialogComponent } from './recurring-transaction-form-dialog/recurring-transaction-form-dialog.component';

@Component({
  selector: 'app-recurring-transactions-list',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatSlideToggleModule,
    MatSelectModule,
    MatTooltipModule
  ],
  templateUrl: './recurring-transactions-list.component.html',
  styleUrls: ['./recurring-transactions-list.component.css']
})
export class RecurringTransactionsListComponent implements OnInit {
  recurringTransactions: any[] = [];
  displayedColumns: string[] = ['description', 'amount', 'category', 'frequency', 'nextOccurrence', 'isActive', 'actions'];

  constructor(
    private recurringTransactionsService: RecurringTransactionsService,
    private snackBar: MatSnackBar,
    public dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.loadRecurringTransactions();
  }

  loadRecurringTransactions(): void {
    this.recurringTransactionsService.getRecurringTransactions().subscribe({
      next: (data) => {
        this.recurringTransactions = data.results;
      },
      error: (err) => {
        this.snackBar.open('Error loading recurring transactions: ' + err.message, 'Close', { duration: 3000 });
      }
    });
  }

  openRecurringTransactionForm(recurringTransaction?: any): void {
    const dialogRef = this.dialog.open(RecurringTransactionFormDialogComponent, {
      width: '500px',
      data: recurringTransaction ? { ...recurringTransaction } : {}
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadRecurringTransactions();
      }
    });
  }

  toggleActive(transaction: any): void {
    this.recurringTransactionsService.toggleActive(transaction.id).subscribe({
      next: () => {
        this.snackBar.open('Recurring transaction status updated successfully!', 'Close', { duration: 3000 });
        this.loadRecurringTransactions();
      },
      error: (err) => {
        this.snackBar.open('Error updating recurring transaction status: ' + err.message, 'Close', { duration: 3000 });
      }
    });
  }

  editRecurringTransaction(transaction: any): void {
    this.openRecurringTransactionForm(transaction);
  }

  deleteRecurringTransaction(id: any): void {
    if (confirm('Are you sure you want to delete this recurring transaction?')) {
      this.recurringTransactionsService.deleteRecurringTransaction(id).subscribe({
        next: () => {
          this.snackBar.open('Recurring transaction deleted successfully!', 'Close', { duration: 3000 });
          this.loadRecurringTransactions();
        },
        error: (err) => {
          this.snackBar.open('Error deleting recurring transaction: ' + err.message, 'Close', { duration: 3000 });
        }
      });
    }
  }

  // Helper methods for the template
  getActiveCount(): number {
    return this.recurringTransactions.filter((t: any) => t.is_active).length;
  }

  getMonthlyTotal(): number {
    return this.recurringTransactions
      .filter((t: any) => t.is_active)
      .reduce((sum: number, transaction: any) => {
        const multiplier = this.getMonthlyMultiplier(transaction.frequency);
        return sum + (transaction.amount * multiplier);
      }, 0);
  }

  private getMonthlyMultiplier(frequency: string): number {
    switch(frequency) {
      case 'daily': return 30;
      case 'weekly': return 4;
      case 'monthly': return 1;
      case 'yearly': return 1/12;
      default: return 1;
    }
  }

  getUpcomingCount(): number {
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 7);
    return this.recurringTransactions.filter((t: any) => 
      new Date(t.next_occurrence) <= nextWeek && t.is_active
    ).length;
  }

  getCategoryColor(category: string): string {
    const colors: {[key: string]: string} = {
      'Bills': 'bg-red-500',
      'Entertainment': 'bg-purple-500',
      'Food': 'bg-green-500',
      'Shopping': 'bg-blue-500',
      'Transportation': 'bg-orange-500',
      'Utilities': 'bg-yellow-500',
      'Income': 'bg-emerald-500',
      'Healthcare': 'bg-pink-500',
      'Education': 'bg-indigo-500'
    };
    return colors[category] || 'bg-gray-500';
  }

  getAmountColor(amount: number): string {
    return amount >= 0 ? 'text-green-600' : 'text-red-600';
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

  getDaysUntil(nextOccurrence: string): string {
    const today = new Date();
    const nextDate = new Date(nextOccurrence);
    const diffTime = nextDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays < 0) return `${Math.abs(diffDays)} days ago`;
    return `In ${diffDays} days`;
  }

  viewTransactionDetails(transaction: any): void {
    // You can implement a detailed view dialog here
    console.log('View transaction details:', transaction);
    // Optional: Open a details dialog
    // this.openTransactionDetailsDialog(transaction);
  }
}