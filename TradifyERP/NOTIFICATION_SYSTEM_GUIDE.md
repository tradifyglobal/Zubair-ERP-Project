# Notification System Implementation

## Overview
A comprehensive notification system has been implemented to alert users with review and approval permissions about pending capital contributions awaiting their action.

## Features

### 1. **Automatic Notification Detection**
- **For Reviewers**: Shows contributions in SUBMITTED or FIRST_REVIEW_COMPLETED status that need review
- **For Approvers**: Shows contributions in REVIEWED status (both reviews complete) that need approval
- Users only see notifications for which they have appropriate permissions
- Filtered by current entity/organization

### 2. **Notification Bell Badge**
- Located in the top-right header bar
- Red badge displays count of pending items
- Badge auto-hides when no pending items
- Updates every 30 seconds automatically

### 3. **Dynamic Notification Dropdown**
- Click the bell icon to view detailed notifications
- Shows two sections:
  - **Awaiting Review** (with count) - shows all contributions pending first/second review
  - **Awaiting Approval** (with count) - shows all contributions ready for approval
- Each notification displays:
  - Stakeholder name
  - Contribution amount
  - Action type (Review or Approval)
  - Direct link to the contribution for action

### 4. **Real-Time Updates**
- Notifications refresh automatically every 30 seconds
- No page reload needed
- Badge count updates in real-time
- All active users see current status

### 5. **File Preview on Detail Page**
- Capital contribution detail page now shows file preview
- Supports:
  - **PDF**: Inline preview with embedded viewer (600px height)
  - **Images** (.jpg, .png, .gif, .jpeg): Visual thumbnail with proper scaling
  - **Other files**: File type indicator with info
- Download button easily accessible in card header
- File name and size displayed

## Technical Implementation

### Backend Components

**1. `shareholder/notifications.py`**
- `get_pending_reviews_for_user()`: Fetches reviews awaiting user
- `get_pending_approvals_for_user()`: Fetches approvals awaiting user  
- `get_all_pending_for_user()`: Combined count and QuerySets

**2. `shareholder/context_processors.py`**
- `pending_notifications()`: Injects notification data into all templates
- Runs on every page load for authenticated users
- Respects user permissions and selected entity

**3. `shareholder/views.py` - NotificationAPIView**
- REST endpoint at `/shareholder/api/notifications/`
- Returns JSON with:
  - `pending_reviews_count`: Number of pending reviews
  - `pending_approvals_count`: Number of pending approvals
  - `total_pending`: Combined count
  - `review_items`: Array of review details (first 5)
  - `approval_items`: Array of approval details (first 5)

### Frontend Components

**1. `templates/partials/header.html`**
- Updated notification bell dropdown
- Dynamic badge with count
- Two-section layout (Reviews and Approvals)
- "View All Contributions" footer link

**2. `templates/partials/base.html`**
- JavaScript notification system
- Automatic fetch every 30 seconds
- UI update functions
- Smooth badge count updates

**3. Settings Configuration**
- Added context processor to `TradifyERP/settings.py`
- Ensures notifications available on all pages

## Permission Requirements

Users see notifications if they have:
- `accounting.review_capitalcontribution` permission → See pending reviews
- `accounting.approve_capitalcontribution` permission → See pending approvals

## How It Works

1. **On Page Load**:
   - Context processor calculates pending reviews/approvals
   - Badge displays count in header
   - Notification dropdown shows grouped items

2. **Every 30 Seconds**:
   - JavaScript calls `/shareholder/api/notifications/` API
   - API recalculates pending items for current user
   - UI updates with latest counts and items
   - Badge shows/hides based on count

3. **User Action**:
   - User clicks notification item
   - Directed to capital contribution detail or review/approval page
   - Can take action on the contribution
   - Notification automatically disappears after action

## Workflow Status Integration

Notifications based on workflow status:
- **SUBMITTED** → First reviewer needs to review
- **FIRST_REVIEW_COMPLETED** → Second reviewer needs to review  
- **REVIEWED** → Approver needs to approve
- **APPROVED/REJECTED** → No further action needed

## Usage

1. User logs in with review or approver permissions
2. Bell icon appears with red badge if pending items exist
3. Click bell to see details of pending contributions
4. Click any item to navigate directly to that contribution
5. Complete the action (review/approve)
6. Notification auto-updates and disappears

## File Preview Features

On capital contribution detail page:
- Upload a document (PDF, image, etc.)
- Detail page automatically shows preview
- PDF files display in embedded viewer
- Images show as thumbnails
- Other files show type indicator
- Download button always available

## Future Enhancements

- Email notifications when items assigned
- Browser notifications for urgent items
- Bulk actions on multiple pending items
- Notification history/archive
- Notification preferences per user
