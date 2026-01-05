import { Component } from '@angular/core';
import { trigger, transition, style, animate, query, stagger, keyframes } from '@angular/animations';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-landing-page',
  imports: [CommonModule],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.css',
  // animations:[  trigger('fadeIn', [
  //     transition(':enter', [
  //       style({ opacity: 0, transform: 'translateY(20px)' }),
  //       animate('0.8s ease-out', style({ opacity: 1, transform: 'translateY(0)' }))
  //     ])
  //   ]),
  //   trigger('slideInLeft', [
  //     transition(':enter', [
  //       style({ opacity: 0, transform: 'translateX(-50px)' }),
  //       animate('0.8s ease-out', style({ opacity: 1, transform: 'translateX(0)' }))
  //     ])
  //   ]),
  //   trigger('slideInRight', [
  //     transition(':enter', [
  //       style({ opacity: 0, transform: 'translateX(50px)' }),
  //       animate('0.8s ease-out', style({ opacity: 1, transform: 'translateX(0)' }))
  //     ])
  //   ]),
  //   trigger('staggerItems', [
  //     transition(':enter', [
  //       query('.stagger-item', [
  //         style({ opacity: 0, transform: 'translateY(20px)' }),
  //         stagger('100ms', [
  //           animate('0.6s ease-out', style({ opacity: 1, transform: 'translateY(0)' }))
  //         ])
  //       ])
  //     ])
  //   ]),
  //   trigger('pulse', [
  //     transition(':enter', [
  //       animate('2s ease-in-out', keyframes([
  //         style({ transform: 'scale(1)', offset: 0 }),
  //         style({ transform: 'scale(1.05)', offset: 0.5 }),
  //         style({ transform: 'scale(1)', offset: 1 })
  //       ]))
  //     ])
  //   ]),
  //   trigger('float', [
  //     transition(':enter', [
  //       animate('3s ease-in-out', keyframes([
  //         style({ transform: 'translateY(0px)', offset: 0 }),
  //         style({ transform: 'translateY(-15px)', offset: 0.5 }),
  //         style({ transform: 'translateY(0px)', offset: 1 })
  //       ]))
  //     ])
  //   ])
  // ]
})
export class LandingPageComponent {
    title = 'FinDash - AI-Powered Financial Insights';

  constructor(private router: Router) { }

  // AI Features Data
  aiFeatures = [
    {
      icon: 'fas fa-chart-line',
      title: 'Predictive Analytics',
      description: 'Forecast stock prices, currency movements, and macroeconomic trends using advanced ML models.',
      color: 'blue'
    },
    {
      icon: 'fas fa-shield-alt',
      title: 'Risk Assessment',
      description: 'Automate credit scoring and risk profiling by analyzing customer behavior and market conditions.',
      color: 'red'
    },
    {
      icon: 'fas fa-user-secret',
      title: 'Fraud Detection',
      description: 'Implement anomaly detection algorithms to identify suspicious transactions in real-time.',
      color: 'yellow'
    },
    {
      icon: 'fas fa-chart-pie',
      title: 'Portfolio Optimization',
      description: 'Recommend optimal investment strategies based on market data, risk tolerance, and client goals.',
      color: 'green'
    },
    {
      icon: 'fas fa-language',
      title: 'Natural Language Processing',
      description: 'Extract insights from financial news, earnings calls, and reports to aid investment decisions.',
      color: 'purple'
    },
    {
      icon: 'fas fa-robot',
      title: 'AI Financial Assistant',
      description: 'Get personalized financial advice and insights from our advanced AI assistant.',
      color: 'indigo'
    }
  ];

  // Core Features Data
  coreFeatures = [
    {
      icon: 'fas fa-calculator',
      title: 'Salary Calculator',
      description: 'Quickly calculate your weekly, monthly, and yearly earnings with tax estimates.',
      color: 'indigo'
    },
    {
      icon: 'fas fa-receipt',
      title: 'Expense Tracking',
      description: 'Log and categorize expenses to understand your spending habits.',
      color: 'green'
    },
    {
      icon: 'fas fa-chart-bar',
      title: 'Expense Predictions',
      description: 'AI-powered predictions to forecast your future spending patterns.',
      color: 'yellow'
    },
    {
      icon: 'fas fa-comments',
      title: 'Financial Assistant',
      description: 'Get personalized financial advice from our AI-powered chatbot.',
      color: 'red'
    }
  ];

  // Testimonials Data
  testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Small Business Owner',
      initials: 'SJ',
      quote: 'FinDash helped me understand my business finances better than any other tool. The salary calculator alone saved me hours each month.'
    },
    {
      name: 'Michael Chen',
      role: 'Freelance Developer',
      initials: 'MC',
      quote: 'As a freelancer, tracking irregular income was challenging. FinDash\'s predictions helped me plan my finances with confidence.'
    },
    {
      name: 'David Wilson',
      role: 'Financial Consultant',
      initials: 'DW',
      quote: 'I recommend FinDash to all my clients. The financial assistant provides excellent advice and helps users make better decisions.'
    }
  ];

  // Footer Links Data
  footerLinks = {
    product: ['Features', 'Pricing', 'API', 'Documentation'],
    company: ['About', 'Blog', 'Careers', 'Press'],
    legal: ['Privacy', 'Terms', 'Security'],
    connect: ['Twitter', 'Facebook', 'LinkedIn', 'Instagram']
  };

  // Get color class for feature icons
  getColorClass(color: string): string {
    const colorMap: { [key: string]: string } = {
      blue: 'bg-blue-500',
      red: 'bg-red-500',
      yellow: 'bg-yellow-500',
      green: 'bg-green-500',
      purple: 'bg-purple-500',
      indigo: 'bg-indigo-500'
    };
    return colorMap[color] || 'bg-indigo-500';
  }

  // Navigation methods
  navigateToLogin() {
    this.router.navigate(['/auth/login']);
  }

  navigateToSignup() {
    this.router.navigate(['/auth/signup']);
  }

  navigateToGetStarted() {
    // Implement get started navigation
    console.log('Navigate to get started');
  }
}
