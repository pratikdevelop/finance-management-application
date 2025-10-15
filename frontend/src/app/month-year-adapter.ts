import { MomentDateAdapter } from '@angular/material-moment-adapter';
import { MAT_DATE_FORMATS, DateAdapter } from '@angular/material/core';

export const MONTH_YEAR_FORMATS = {
  parse: {
    dateInput: 'MM/YYYY',
  },
  display: {
    dateInput: 'MM/YYYY',
    monthYearLabel: 'MMM YYYY',
    dateA11yLabel: 'LL',
    monthYearA11yLabel: 'MMMM YYYY',
  },
};

import { Injectable } from '@angular/core';

@Injectable()
export class MonthYearDateAdapter extends MomentDateAdapter {
  // Override the format method to display only month and year
  override format(date: moment.Moment, displayFormat: string): string {
    if (displayFormat === 'MM/YYYY') {
      return date.format('MM/YYYY');
    }
    return super.format(date, displayFormat);
  }
}