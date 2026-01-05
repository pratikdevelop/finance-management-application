import { Component, OnInit, ElementRef, ViewChild, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import * as d3 from 'd3';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../services/auth.service';
import { Subscription } from 'rxjs';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDatepicker } from '@angular/material/datepicker';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-financial-summary',
  templateUrl: './financial-summary.component.html',
  styleUrls: ['./financial-summary.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatFormFieldModule,
    MatInputModule,
    MatTooltipModule,
    MatIconModule
  ]
})
export class FinancialSummaryComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('incomeExpenseChart') private incomeExpenseChartContainer!: ElementRef;
  @ViewChild('categoryChart') private categoryChartContainer!: ElementRef;
  @ViewChild('trendChart') private trendChartContainer!: ElementRef;
  
  summaryData: any = null;
  loading = true;
  error: string | null = null;
  tokenSubscription: Subscription | undefined;
  recurringTransactionSummary: any;

  selectedDate: Date | null = new Date();
  startDate: Date | null = new Date();
  endDate: Date | null = new Date();

  constructor(private apiService: ApiService, private authService: AuthService) {
    const today = new Date();
    this.startDate = new Date(today.getFullYear(), today.getMonth(), 1);
    this.endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  }

  ngOnInit(): void {
    this.tokenSubscription = this.authService.token$.subscribe(token => {
      if (token) {
        this.loadFinancialSummary();
        this.loadRecurringTransactionSummary();
      }
    });
  }

  ngOnDestroy(): void {
    if (this.tokenSubscription) {
      this.tokenSubscription.unsubscribe();
    }
  }

  ngAfterViewInit(): void {
    // Charts will be created after data is loaded
  }

  onMonthSelected(event: any): void {
    this.selectedDate = event.value;
    this.loadFinancialSummary();
  }

  onStartDateSelected(event: any): void {
    this.startDate = event.value;
    this.loadFinancialSummary();
  }

  onEndDateSelected(event: any): void {
    this.endDate = event.value;
    this.loadFinancialSummary();
  }

  loadFinancialSummary(): void {
    this.loading = true;
    this.error = null;
    
    let year: number | undefined;
    let month: number | undefined;
    let start_date: string | undefined;
    let end_date: string | undefined;

    if (this.startDate) {
      start_date = this.startDate.toISOString().split('T')[0];
    }

    if (this.endDate) {
      end_date = this.endDate.toISOString().split('T')[0];
    }

    this.apiService.getFinancialSummary(start_date, end_date).subscribe({
      next: (data) => {
        this.summaryData = data;
        this.loading = false;
        
        // Create charts after data is loaded
        setTimeout(() => {
          this.createIncomeExpenseChart();
          this.createCategoryChart();
          this.createTrendChart();
        }, 100);
      },
      error: (err) => {
        this.error = 'Failed to load financial summary. Please try again later.';
        this.loading = false;
        console.error('Error loading financial summary:', err);
      }
    });
  }

  // Balance calculation helper methods
  getBalance(): number {
    if (!this.summaryData) return 0;
    return this.summaryData.total_income - this.summaryData.total_expenses;
  }

  getBalanceCardClass(): string {
    const balance = this.getBalance();
    return balance >= 0 
      ? 'summary-card bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-blue-500'
      : 'summary-card bg-gradient-to-br from-orange-50 to-orange-100 border-l-4 border-orange-500';
  }

  getBalanceIconClass(): string {
    const balance = this.getBalance();
    return balance >= 0 
      ? 'p-2 rounded-lg bg-blue-500 bg-opacity-10 mr-3 text-blue-600'
      : 'p-2 rounded-lg bg-orange-500 bg-opacity-10 mr-3 text-orange-600';
  }

  getBalanceTextClass(): string {
    const balance = this.getBalance();
    return balance >= 0 
      ? 'text-2xl md:text-3xl font-bold text-gray-800'
      : 'text-2xl md:text-3xl font-bold text-gray-800';
  }

  getBalanceTrendClass(): string {
    const balance = this.getBalance();
    return balance >= 0 ? 'text-blue-600' : 'text-orange-600';
  }

  getBalanceTrendIcon(): string {
    const balance = this.getBalance();
    return balance >= 0 ? 'arrow_upward' : 'arrow_downward';
  }

  getBalanceTrendText(): string {
    const balance = this.getBalance();
    return balance >= 0 ? 'Positive cash flow' : 'Negative cash flow';
  }

  // Chart creation methods
  createIncomeExpenseChart(): void {
    if (!this.summaryData || !this.incomeExpenseChartContainer) return;

    const element = this.incomeExpenseChartContainer.nativeElement;
    const data = [
      { label: 'Income', value: this.summaryData.total_income, color: '#4CAF50' },
      { label: 'Expenses', value: this.summaryData.total_expenses, color: '#F44336' },
      { label: 'Transfers', value: this.summaryData.total_transfers || 0, color: '#2196F3' },
      { label: 'Investments', value: this.summaryData.total_investments || 0, color: '#FFC107' },
      { label: 'Loans', value: this.summaryData.total_loans || 0, color: '#9C27B0' },
      { label: 'Savings', value: this.summaryData.total_savings || 0, color: '#00BCD4' }
    ];

    // Clear previous chart if any
    d3.select(element).selectAll('*').remove();

    const width = element.clientWidth;
    const height = 300;
    const margin = { top: 30, right: 30, bottom: 40, left: 60 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const svg = d3.select(element)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const chart = svg.append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // X scale
    const x = d3.scaleBand()
      .domain(data.map(d => d.label))
      .range([0, chartWidth])
      .padding(0.3);

    // Y scale
    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value) || 0])
      .range([chartHeight, 0]);

    // X axis
    chart.append('g')
      .attr('transform', `translate(0, ${chartHeight})`)
      .call(d3.axisBottom(x));

    // Y axis with currency formatting
    chart.append('g')
      .call(d3.axisLeft(y).tickFormat(d => `$${d}`));

    // Bars
    chart.selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.label) || 0)
      .attr('y', d => y(d.value))
      .attr('width', x.bandwidth())
      .attr('height', d => chartHeight - y(d.value))
      .attr('fill', d => d.color)
      .attr('rx', 4) // Rounded corners
      .attr('ry', 4);

    // Value labels on bars
    chart.selectAll('.label')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'label')
      .attr('x', d => (x(d.label) || 0) + x.bandwidth() / 2)
      .attr('y', d => y(d.value) - 10)
      .attr('text-anchor', 'middle')
      .style('font-weight', 'bold')
      .style('fill', '#374151')
      .text(d => {
        const value = parseFloat(d.value);
        return `$${isNaN(value) ? 0 : value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      });

    // Title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 20)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .style('fill', '#374151')
      .text('Income vs Expenses');
  }

  createCategoryChart(): void {
    if (!this.summaryData || !this.categoryChartContainer || !this.summaryData.expenses_by_category) return;

    const element = this.categoryChartContainer.nativeElement;
    const data = this.summaryData.expenses_by_category;

    // Clear previous chart if any
    d3.select(element).selectAll('*').remove();

    const width = element.clientWidth;
    const height = 300;
    const radius = Math.min(width, height) / 2 - 50;

    const svg = d3.select(element)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    // Color scale with better colors
    const color = d3.scaleOrdinal()
      .domain(data.map((d: any, i: number) => i.toString()))
      .range(['#EF4444', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']);

    // Pie chart layout
    const pie = d3.pie<any>()
      .value((d: any) => d.amount)
      .sort(null);

    // Arc generator
    const arc = d3.arc<any>()
      .innerRadius(0)
      .outerRadius(radius);

    // Outer arc for labels
    const outerArc = d3.arc<any>()
      .innerRadius(radius * 1.1)
      .outerRadius(radius * 1.1);

    // Create pie chart
    const arcs = svg.selectAll('.arc')
      .data(pie(data))
      .enter()
      .append('g')
      .attr('class', 'arc');

    // Add slices with hover effects
    arcs.append('path')
      .attr('d', arc)
      .attr('fill', (d: any, i: number) => color(i.toString()) as string)
      .style('opacity', 0.8)
      .on('mouseover', function(event, d: any) {
        d3.select(this).style('opacity', 1);
      })
      .on('mouseout', function(event, d: any) {
        d3.select(this).style('opacity', 0.8);
      });

    // Add labels
    arcs.append('text')
      .attr('transform', (d: any) => {
        const pos = outerArc.centroid(d);
        const midAngle = d.startAngle + (d.endAngle - d.startAngle) / 2;
        pos[0] = radius * 0.8 * (midAngle < Math.PI ? 1 : -1);
        return `translate(${pos})`;
      })
      .attr('dy', '.35em')
      .style('text-anchor', (d: any) => {
        const midAngle = d.startAngle + (d.endAngle - d.startAngle) / 2;
        return midAngle < Math.PI ? 'start' : 'end';
      })
      .style('font-size', '12px')
      .style('fill', '#374151')
      .text((d: any) => {
        const total = d3.sum(data.map((item: any) => item.amount));
        const percentage = ((d.data.amount / total) * 100).toFixed(1);
        return `${d.data.category} (${percentage}%)`;
      });

    // Add polylines between slices and labels
    arcs.append('polyline')
      .attr('points', function(d: any) {
        const pos = outerArc.centroid(d);
        const midAngle = d.startAngle + (d.endAngle - d.startAngle) / 2;
        pos[0] = radius * 0.75 * (midAngle < Math.PI ? 1 : -1);
        return [arc.centroid(d), outerArc.centroid(d), pos].join(',');
      })
      .style('fill', 'none')
      .style('stroke', '#9CA3AF')
      .style('stroke-width', '1px');

    // Title
    svg.append('text')
      .attr('x', 0)
      .attr('y', -height / 2 + 25)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .style('fill', '#374151')
      .text('Expenses by Category');
  }

  createTrendChart(): void {
    if (!this.summaryData || !this.trendChartContainer || !this.summaryData.monthly_trend) return;

    const element = this.trendChartContainer.nativeElement;
    const data = this.summaryData.monthly_trend;

    // Clear previous chart if any
    d3.select(element).selectAll('*').remove();

    const width = element.clientWidth;
    const height = 300;
    const margin = { top: 40, right: 80, bottom: 50, left: 60 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const svg = d3.select(element)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const chart = svg.append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // X axis
    const x = d3.scaleBand()
      .domain(data.map((d: any) => d.month))
      .range([0, chartWidth])
      .padding(0.1);

    // Y scale
    const y = d3.scaleLinear()
      .domain([0, d3.max(data, (d: any) => Math.max(d.income, d.expenses)) || 0])
      .range([chartHeight, 0]);

    // X axis with rotated labels
    chart.append('g')
      .attr('transform', `translate(0, ${chartHeight})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)');

    // Y axis with currency formatting
    chart.append('g')
      .call(d3.axisLeft(y).tickFormat(d => `$${d}`));

    // Income line
    const incomeLine = d3.line<any>()
      .x(d => (x(d.month) || 0) + x.bandwidth() / 2)
      .y(d => y(d.income))
      .curve(d3.curveMonotoneX);

    chart.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#10B981')
      .attr('stroke-width', 3)
      .attr('d', incomeLine);

    // Expense line
    const expenseLine = d3.line<any>()
      .x(d => (x(d.month) || 0) + x.bandwidth() / 2)
      .y(d => y(d.expenses))
      .curve(d3.curveMonotoneX);

    chart.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#EF4444')
      .attr('stroke-width', 3)
      .attr('d', expenseLine);

    // Transfer line
    const transferLine = d3.line<any>()
      .x(d => (x(d.month) || 0) + x.bandwidth() / 2)
      .y(d => y(d.transfers))
      .curve(d3.curveMonotoneX);

    chart.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#2196F3')
      .attr('stroke-width', 3)
      .attr('d', transferLine);

    // Investment line
    const investmentLine = d3.line<any>()
      .x(d => (x(d.month) || 0) + x.bandwidth() / 2)
      .y(d => y(d.investments))
      .curve(d3.curveMonotoneX);

    chart.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#FFC107')
      .attr('stroke-width', 3)
      .attr('d', investmentLine);

    // Loan line
    const loanLine = d3.line<any>()
      .x(d => (x(d.month) || 0) + x.bandwidth() / 2)
      .y(d => y(d.loans))
      .curve(d3.curveMonotoneX);

    chart.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#9C27B0')
      .attr('stroke-width', 3)
      .attr('d', loanLine);

    // Saving line
    const savingLine = d3.line<any>()
      .x(d => (x(d.month) || 0) + x.bandwidth() / 2)
      .y(d => y(d.savings))
      .curve(d3.curveMonotoneX);

    chart.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#00BCD4')
      .attr('stroke-width', 3)
      .attr('d', savingLine);

    // Add dots for data points
    chart.selectAll('.income-dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'income-dot')
      .attr('cx', (d: any) => (x(d.month) || 0) + x.bandwidth() / 2)
      .attr('cy', (d: any) => y(d.income))
      .attr('r', 4)
      .attr('fill', '#10B981')
      .on('mouseover', function(event, d: any) {
        // Show tooltip on hover
        const tooltip = d3.select('body').append('div')
          .attr('class', 'tooltip')
          .style('position', 'absolute')
          .style('background', 'white')
          .style('padding', '8px')
          .style('border-radius', '4px')
          .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
          .style('font-size', '12px')
          .html(`<strong>${d.month}</strong><br>Income: $${d.income.toLocaleString()}`);
        
        tooltip.style('left', (event.pageX + 10) + 'px')
               .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.tooltip').remove();
      });

    chart.selectAll('.expense-dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'expense-dot')
      .attr('cx', (d: any) => (x(d.month) || 0) + x.bandwidth() / 2)
      .attr('cy', (d: any) => y(d.expenses))
      .attr('r', 4)
      .attr('fill', '#EF4444')
      .on('mouseover', function(event, d: any) {
        const tooltip = d3.select('body').append('div')
          .attr('class', 'tooltip')
          .style('position', 'absolute')
          .style('background', 'white')
          .style('padding', '8px')
          .style('border-radius', '4px')
          .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
          .style('font-size', '12px')
          .html(`<strong>${d.month}</strong><br>Expenses: $${d.expenses.toLocaleString()}`);
        
        tooltip.style('left', (event.pageX + 10) + 'px')
               .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.tooltip').remove();
      });

    // Transfer dots
    chart.selectAll('.transfer-dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'transfer-dot')
      .attr('cx', (d: any) => (x(d.month) || 0) + x.bandwidth() / 2)
      .attr('cy', (d: any) => y(d.transfers))
      .attr('r', 4)
      .attr('fill', '#2196F3')
      .on('mouseover', function(event, d: any) {
        const tooltip = d3.select('body').append('div')
          .attr('class', 'tooltip')
          .style('position', 'absolute')
          .style('background', 'white')
          .style('padding', '8px')
          .style('border-radius', '4px')
          .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
          .style('font-size', '12px')
          .html(`<strong>${d.month}</strong><br>Transfers: $${d.transfers.toLocaleString()}`);
        
        tooltip.style('left', (event.pageX + 10) + 'px')
               .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.tooltip').remove();
      });

    // Investment dots
    chart.selectAll('.investment-dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'investment-dot')
      .attr('cx', (d: any) => (x(d.month) || 0) + x.bandwidth() / 2)
      .attr('cy', (d: any) => y(d.investments))
      .attr('r', 4)
      .attr('fill', '#FFC107')
      .on('mouseover', function(event, d: any) {
        const tooltip = d3.select('body').append('div')
          .attr('class', 'tooltip')
          .style('position', 'absolute')
          .style('background', 'white')
          .style('padding', '8px')
          .style('border-radius', '4px')
          .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
          .style('font-size', '12px')
          .html(`<strong>${d.month}</strong><br>Investments: $${d.investments.toLocaleString()}`);
        
        tooltip.style('left', (event.pageX + 10) + 'px')
               .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.tooltip').remove();
      });

    // Loan dots
    chart.selectAll('.loan-dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'loan-dot')
      .attr('cx', (d: any) => (x(d.month) || 0) + x.bandwidth() / 2)
      .attr('cy', (d: any) => y(d.loans))
      .attr('r', 4)
      .attr('fill', '#9C27B0')
      .on('mouseover', function(event, d: any) {
        const tooltip = d3.select('body').append('div')
          .attr('class', 'tooltip')
          .style('position', 'absolute')
          .style('background', 'white')
          .style('padding', '8px')
          .style('border-radius', '4px')
          .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
          .style('font-size', '12px')
          .html(`<strong>${d.month}</strong><br>Loans: $${d.loans.toLocaleString()}`);
        
        tooltip.style('left', (event.pageX + 10) + 'px')
               .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.tooltip').remove();
      });

    // Saving dots
    chart.selectAll('.saving-dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'saving-dot')
      .attr('cx', (d: any) => (x(d.month) || 0) + x.bandwidth() / 2)
      .attr('cy', (d: any) => y(d.savings))
      .attr('r', 4)
      .attr('fill', '#00BCD4')
      .on('mouseover', function(event, d: any) {
        const tooltip = d3.select('body').append('div')
          .attr('class', 'tooltip')
          .style('position', 'absolute')
          .style('background', 'white')
          .style('padding', '8px')
          .style('border-radius', '4px')
          .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
          .style('font-size', '12px')
          .html(`<strong>${d.month}</strong><br>Savings: $${d.savings.toLocaleString()}`);
        
        tooltip.style('left', (event.pageX + 10) + 'px')
               .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.tooltip').remove();
      });

    // Enhanced Legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - margin.right - 120}, ${margin.top})`);

    // Income legend
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', '#10B981')
      .attr('rx', 2);

    legend.append('text')
      .attr('x', 20)
      .attr('y', 12.5)
      .style('font-size', '12px')
      .style('fill', '#374151')
      .text('Income');

    // Expense legend
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 20)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', '#EF4444')
      .attr('rx', 2);

    legend.append('text')
      .attr('x', 20)
      .attr('y', 32.5)
      .style('font-size', '12px')
      .style('fill', '#374151')
      .text('Expenses');

    // Transfer legend
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 40)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', '#2196F3')
      .attr('rx', 2);

    legend.append('text')
      .attr('x', 20)
      .attr('y', 52.5)
      .style('font-size', '12px')
      .style('fill', '#374151')
      .text('Transfers');

    // Investment legend
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 60)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', '#FFC107')
      .attr('rx', 2);

    legend.append('text')
      .attr('x', 20)
      .attr('y', 72.5)
      .style('font-size', '12px')
      .style('fill', '#374151')
      .text('Investments');

    // Loan legend
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 80)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', '#9C27B0')
      .attr('rx', 2);

    legend.append('text')
      .attr('x', 20)
      .attr('y', 92.5)
      .style('font-size', '12px')
      .style('fill', '#374151')
      .text('Loans');

    // Saving legend
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 100)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', '#00BCD4')
      .attr('rx', 2);

    legend.append('text')
      .attr('x', 20)
      .attr('y', 112.5)
      .style('font-size', '12px')
      .style('fill', '#374151')
      .text('Savings');

    // Title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 20)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .style('fill', '#374151')
      .text('Monthly Income & Expenses Trend');
  }

  private loadRecurringTransactionSummary(): void {
    this.apiService.getRecurringTransactionSummary().subscribe({
      next: (data) => {
        this.recurringTransactionSummary = data;
        console.log('Recurring Transaction Summary:', this.recurringTransactionSummary);
      },
      error: (error) => {
        console.error('Error loading recurring transaction summary:', error);
      }
    });
  }
}