import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { UserService } from '../services/user.service';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  profileForm!: FormGroup;

  constructor(private fb: FormBuilder, private userService: UserService) { }

  ngOnInit(): void {
    this.profileForm = this.fb.group({
      username: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      memberSince: [''],
    });

    this.userService.getProfile().subscribe(data => {
      this.profileForm.patchValue(data);
      this.profileForm.get('memberSince')?.setValue(data.member_since);
      this.profileForm.get('email')?.setValue(data.email);
      this.profileForm.get('username')?.setValue(data.username);

    });
  }

  onSubmit(): void {
    if (this.profileForm.valid) {
      this.userService.updateProfile(this.profileForm.value).subscribe(response => {
        console.log('Profile updated successfully:', response);
        // Optionally, show a success message
      }, error => {
        console.error('Error updating profile:', error);
        // Optionally, show an error message
      });
    }
  }
}
