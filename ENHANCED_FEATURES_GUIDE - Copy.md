# SMRU College Portal - Enhanced Features Implementation Guide

## Overview
This document describes all the new features implemented in the college portal system, including setup instructions and usage guidelines for administrators and users.

## Table of Contents
1. [New User Registration System](#new-user-registration-system)
2. [Login Request Approval Workflow](#login-request-approval-workflow)
3. [Password Recovery System](#password-recovery-system)
4. [Complaint Management System](#complaint-management-system)
5. [Admin Panel Configuration](#admin-panel-configuration)
6. [User Roles and Permissions](#user-roles-and-permissions)

---

## New User Registration System

### Features
- **Comprehensive Student Registration**: Students must provide all information at once during signup
- **Engineering vs Medical College Separation**: College type selector filters available colleges
- **Document Verification**: Students upload ID card, PAN card, and live photo for verification
- **Hall Ticket Number**: Required for tracking student identity

### Student Registration Flow
1. **Access Signup Page**: Navigate to `/signup/`
2. **Select User Role**: Choose "Student" from the dropdown
3. **Enter Personal Information**:
   - First Name and Last Name
   - Email Address
   - Phone Number
   - Username
4. **Select College Type**: Choose "Engineering" or "Medical"
5. **Select College**: Dropdown auto-filters based on selected type
6. **Enter Academic Details**:
   - Branch
   - Year (1st, 2nd, 3rd, or 4th Year)
   - Hall Ticket Number
7. **Upload Documents**:
   - Either ID Card OR PAN Card (at least one required)
   - Live Photo for verification
8. **Create Password**: Set password (minimum 8 characters)
9. **Submit**: Account created, login request sent to admin

### College Setup (Admin Only)
To use the college filtering feature:
1. Go to Django Admin `/admin/`
2. Click on "Colleges"
3. Create colleges with appropriate types:
   - Type: "Engineering" for engineering colleges
   - Type: "Medical" for medical colleges
4. Add Branches under each college
5. Add Years under each branch
6. Add Subjects under each year

**Important**: Only colleges created in the admin panel will be available in the signup selector. Students from other colleges will be marked as "not from listed college."

---

## Login Request Approval Workflow

### How It Works
1. **Student Registers**: Creates account and automatically generates a login request (status: Pending)
2. **Admin Reviews**: Admin reviews login request in the admin panel
3. **Admin Approves/Rejects**: 
   - Approve: Student can now log in
   - Reject: Student cannot log in (should provide reason separately)
4. **Student Receives Notification**: Gets notified that their request was approved
5. **Student Logs In**: Can now access the portal

### Admin Actions

#### Approve Login Requests
1. Go to Django Admin `/admin/`
2. Click on "Login Requests"
3. Filter by "Status: Pending"
4. Select requests to approve
5. Choose action "Approve selected login requests"
6. Click "Go"

**What Happens**:
- Login request status changes to "Approved"
- Student profile is automatically marked as approved
- Student receives approval message on next login

#### Reject Login Requests
1. Follow steps 1-5 above
2. Choose action "Reject selected login requests"
3. Click "Go"

**What Happens**:
- Login request status changes to "Rejected"
- Student cannot log in
- Admin should notify student separately

### Viewing Login Activities
- Go to "Login Activities" in admin panel
- View all user login/logout times
- Filter by date range to see activity history
- Monitor suspicious login patterns

---

## Password Recovery System

### User Flow

#### Forgot Password Request
1. **Access Page**: User goes to login page and clicks "Forgot password?"
2. **Enter Username or Email**: Provide either username or email address
3. **Choose Contact Method**: Select Email or WhatsApp
4. **Submit**: System generates reset token and sends to user
5. **Click Link**: User receives link with unique token

#### Reset Password
1. **Open Reset Link**: Click the reset link from email/WhatsApp
2. **Enter New Password**: 
   - Minimum 8 characters
   - Must include uppercase, lowercase, numbers
   - Cannot be entirely numeric
3. **Confirm Password**: Re-enter to verify
4. **Submit**: Password updated successfully
5. **Login**: Use new password to log in

### Token Security
- Tokens expire after 24 hours
- One-time use tokens (invalidated after use)
- Unique token per reset request
- All reset requests logged in admin panel

### Admin Password Reset
Admins can also reset user passwords:
1. Go to "Users" in Django Admin
2. Search for user
3. Click on user
4. Change password directly
5. Save

---

## Complaint Management System

### Category Setup (By College Type)

#### For Listed Colleges (Students from colleges in admin)
Create these complaint categories in admin panel:
1. **HODs** - Head of Department issues
2. **Directors** - Director-level issues
3. **Staff** - General staff-related complaints
4. **Placement Department** - Placement cell issues
5. **Chairman** - Chairman-level issues
6. **Security** - Campus security issues
7. **Boys Hostel Incharge** - Boys hostel management
8. **Girls Hostel Incharge** - Girls hostel management
9. **Facilities** - Campus facilities issues
10. **Faculty** - Faculty-related complaints
11. **Academic** - Academic/curriculum issues
12. **Infrastructure** - Building/infrastructure issues
13. **Ragging Team** - Anti-ragging complaints
14. **She Team** - SHE program issues
15. **Others** - Miscellaneous

#### For Unlisted Colleges (Students from other colleges)
Create these complaint categories:
1. **Notes** - Study material requests
2. **Login Requests** - Access issues
3. **Others** - Other general requests

### Assigning Complaint Receivers

For each category, add "Complaint Persons":
1. Go to Admin → "Complaint Persons"
2. Click "Add Complaint Person"
3. **Name**: Full name of the person
4. **Designation**: Position/role
5. **Category**: Select which category
6. **Email**: Email address
7. **Phone**: Phone number
8. **WhatsApp Number**: WhatsApp contact
9. **Is Active**: Check to make person available
10. Save

**Example**:
- Category: "HODs"
- Person: "Dr. Sharma"
- Designation: "Head of Department - CSE"
- Email: dr.sharma@college.edu
- Phone: +91-XXXXXXXXXX
- WhatsApp: +91-XXXXXXXXXX

### Complaint Submission (Student)

1. **Access Complaints**: Navigate to "Submit Complaint"
2. **Select Category**: Choose appropriate complaint category
3. **Select Person**: Choose who to send complaint to
4. **Write Description**: Detail the issue
5. **Attach File** (Optional): Upload supporting documents
6. **Add Feedback** (Optional): Any additional feedback
7. **Submit**: Complaint is submitted

### Complaint Status Tracking (Student)

**View My Complaints**:
1. Go to "My Complaints"
2. View all your submitted complaints
3. See current status:
   - New
   - In Progress
   - Resolved
   - Closed
4. **Mark as Solved**: After issue is fixed, click "Mark as Solved by You"
5. View response from admin/HOD (if provided)

**Important**: 
- Both student AND admin must mark complaint as solved for it to be fully resolved
- Students can optionally provide feedback on the resolution

### Complaint Management (Admin/HOD)

**Access Complaints**:
1. Go to Admin → "Manage Complaints"
2. View complaints assigned to you (based on your role)
3. Or go to Admin → "Complaints" (if you're admin) to see all

**Available Actions**:
1. **Update Status**: Change status (New → In Progress → Resolved → Closed)
2. **Add Response**: Provide response/resolution details
3. **Mark as Solved**: Confirm issue is resolved on your end
4. See if student has marked it solved

**Complaint Resolution Flow**:
1. Receive complaint (status: New)
2. Review and start working (status: In Progress)
3. Provide solution and update status (status: Resolved)
4. Add response/feedback
5. **Click "Mark as Solved"** - You confirm resolution
6. Student receives notification
7. Student views and **clicks "Mark as Solved"** - Student confirms resolution
8. Complaint marked as "Fully Resolved"
9. Option to move to "Closed" status

---

## Admin Panel Configuration

### Dashboard Overview

Key Sections in Admin Panel (`/admin/`):

#### 1. Users & Roles
- **User Roles**: Manage user roles and departments
- **Login Requests**: Approve/reject student login requests
- **Login Activities**: Monitor who logged in/out and when
- **Student Profiles**: Approve students and verify documents

#### 2. Complaints
- **Complaint Categories**: Create complaint types
  - For Listed Colleges
  - For Other Colleges
- **Complaint Persons**: Assign people to receive complaints
- **Complaints**: View and manage all complaints
  - Filter by status, category, date
  - Bulk actions: mark resolved, closed, etc.

#### 3. Teams & People
- **Teams**: 
  - Anti Ragging Team
  - SHE Team
  - Event Managing Team
  - Discipline Team
- **Team Members**: Add members to each team
  - Provide contact details (email, phone, WhatsApp)
  - Manage active/inactive members

#### 4. Academics
- **Colleges**: Create engineering and medical colleges
- **Branches**: Add branches to colleges
- **Years**: Add years to branches
- **Subjects**: Add subjects with study materials

#### 5. Communication
- **Notifications**: Create system-wide notifications
- **Events**: Manage college events
- **Password Reset Requests**: Monitor password reset activity

### Quick Setup Checklist

- [ ] Create at least 2 Engineering colleges
- [ ] Create at least 2 Medical colleges
- [ ] Add Branches to each college
- [ ] Add Years (1-4) to each branch
- [ ] Create Complaint Categories for listed colleges
- [ ] Create Complaint Categories for other colleges
- [ ] Add Complaint Persons (HODs, Directors, etc.)
- [ ] Create Teams (Anti-ragging, SHE, etc.)
- [ ] Add Team Members
- [ ] Configure Login Activity monitoring

---

## User Roles and Permissions

### Role Types

1. **Student**
   - Can submit complaints
   - Can view/track complaints
   - Can mark complaint as solved
   - Can update profile
   - Can view study materials
   - Must be approved before accessing portal

2. **HOD** (Head of Department)
   - Receives complaints related to their department
   - Can view and manage relevant complaints
   - Can mark complaints as solved
   - Can update department information

3. **Chairman**
   - Receives complaints for chairman-level issues
   - Can view and manage assigned complaints
   - Can mark complaints as solved

4. **Principal/Director**
   - Can view administrative reports
   - Can manage high-level complaints
   - Can view college-wide analytics

5. **Faculty**
   - Can view complaints related to teaching
   - Can respond to academic complaints
   - Can manage class-related issues

6. **Security**
   - Can handle security-related complaints
   - Can view incident reports
   - Can manage security personnel

7. **Anti Ragging Team**
   - Handles ragging-related complaints
   - Can take preventive action
   - Can report to authorities

8. **SHE Team** (Safety, Health & Environment)
   - Handles health and safety issues
   - Can respond to environmental complaints
   - Can organize awareness programs

9. **Administrator**
   - Full access to admin panel
   - Can manage all users and complaints
   - Can configure system settings
   - Can reset passwords
   - Can approve/reject login requests

### Permission Matrix

| Action | Student | HOD | Admin | Others |
|--------|---------|-----|-------|--------|
| Submit Complaint | ✓ | ✓ | ✓ | ✓ |
| View Own Complaints | ✓ | ✓ | ✓ | ✓ |
| View Assigned Complaints | ✗ | ✓ | ✓ | ✓ |
| View All Complaints | ✗ | ✗ | ✓ | ✗ |
| Manage Complaints | ✗ | ✓ | ✓ | ✗ |
| Approve Students | ✗ | ✗ | ✓ | ✗ |
| Approve Login Requests | ✗ | ✗ | ✓ | ✗ |
| Create Categories | ✗ | ✗ | ✓ | ✗ |
| View Analytics | ✗ | ✗ | ✓ | ✗ |

---

## Important Notes

### Security
- Student accounts are disabled until admin approval
- Login requests must be explicitly approved
- Password tokens expire after 24 hours
- All login/logout activities are logged
- Admin can force password resets

### Email/WhatsApp Integration (To Be Configured)
The following features are ready for email/WhatsApp integration:
- Password reset links
- Login approval notifications
- Complaint status updates
- Team member notifications

**To Enable**:
1. Configure email settings in Django settings.py
2. Set up WhatsApp API (Twilio, etc.)
3. Implement sending logic in views

### Best Practices
1. **For Admins**:
   - Review login requests within 24 hours
   - Set clear complaint resolution timelines
   - Maintain team member contact information
   - Archive old complaints periodically
   - Monitor suspicious login activities

2. **For HODs/Staff**:
   - Check complaints regularly
   - Provide timely updates
   - Mark complaint as solved when complete
   - Document resolution reasons

3. **For Students**:
   - Use appropriate complaint category
   - Provide clear description and details
   - Attach supporting documents when needed
   - Mark as solved once issue is resolved

---

## Troubleshooting

### Student Can't Login
**Possible Reasons**:
- LoginRequest status is not "Approved"
- StudentProfile is not approved
- Account is deactivated

**Solution**:
1. Check Login Requests in admin
2. Approve pending request
3. Check StudentProfile approval status
4. Check if user account is active

### Complaints Not Showing
**Possible Reasons**:
- Category not created for user's college type
- Complaint Person not assigned to category

**Solution**:
1. Create appropriate complaint categories
2. Add complaint persons to categories
3. Ensure persons are marked as "Active"

### Password Reset Link Not Received
**Possible Reasons**:
- Email/WhatsApp integration not configured
- User email/phone not in database

**Solution**:
1. Set up email/WhatsApp integration
2. Verify user contact information
3. Check system logs for errors

---

## Support & Maintenance

For issues, refer to:
- Django Admin Panel for configuration
- Logs for debugging
- Database queries for data verification

---

**Last Updated**: April 16, 2026
**Version**: 2.0 (Enhanced Edition)
