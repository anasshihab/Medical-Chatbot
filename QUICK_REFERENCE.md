# 🎯 Quick Reference Card - Conversation Sidebar

## Visual Elements

### 1. Sidebar Toggle Button
- **Location**: Fixed right side, vertically centered
- **Appearance**: White circular button with blue border and chat icon
- **Animation**: Gentle pulsing effect
- **Action**: Click to open sidebar

### 2. Sidebar Panel
- **Width**: 320px (desktop), 280px (tablet), 100% (mobile)
- **Position**: Slides in from right
- **Background**: White with glassmorphism (backdrop blur)
- **Sections**:
  - Header (gradient blue)
  - New conversation button
  - Scrollable conversation list

### 3. New Conversation Button
- **Text**: "محادثة جديدة" (New Conversation)
- **Icon**: Plus (+) symbol
- **Color**: White button with dark blue text
- **Behavior**: Creates fresh conversation, clears active states

### 4. Conversation Groups
Time-based organization:
- **اليوم** (Today) - Messages from today
- **أمس** (Yesterday) - Messages from yesterday  
- **آخر 7 أيام** (Last 7 Days) - Messages from past week
- **أقدم** (Older) - Messages older than a week

### 5. Conversation Cards
Each card shows:
- **Title** (bold) - Auto-generated from first message
- **Preview** (gray) - First 100 characters of question
- **Timestamp** (small, gray) - Relative time (e.g., "منذ ساعة")
- **Active State** - Light blue background when selected

## User Actions & Results

| Action | Result |
|--------|--------|
| Click toggle button | Sidebar slides in from right |
| Click close (✕) button | Sidebar slides out |
| Click outside sidebar | Sidebar closes automatically |
| Click conversation card | Loads that conversation, highlights card, closes sidebar |
| Click "محادثة جديدة" | Creates new conversation, clears all active states, closes sidebar |
| Hover over conversation | Card moves right 4px, border turns blue |

## Keyboard Shortcuts (Future)
| Key | Action |
|-----|--------|
| `Ctrl/Cmd + K` | Open sidebar |
| `Esc` | Close sidebar |
| `Ctrl/Cmd + N` | New conversation |
| `↑/↓` | Navigate conversations |
| `Enter` | Open selected conversation |

## CSS Classes Reference

```css
/* Main Components */
.sidebar              /* The sidebar container */
.sidebar.open         /* Sidebar in open state */
.sidebar-header       /* Blue gradient header section */
.sidebar-title        /* "المحادثات السابقة" title */
.close-sidebar-btn    /* X close button */
.new-conversation-btn /* New conversation button */
.conversations-list   /* Scrollable list container */

/* Conversation Grouping */
.conversation-group       /* Group container */
.conversation-group-title /* Time period label */

/* Conversation Items */
.conversation-item        /* Individual conversation card */
.conversation-item.active /* Active/selected conversation */
.conversation-item-title  /* Conversation title */
.conversation-item-preview /* Preview text */
.conversation-item-time   /* Timestamp */

/* Toggle Button */
.sidebar-toggle-btn   /* Floating toggle button */
```

## JavaScript Functions Reference

```javascript
// Core Functions
loadConversations()              // Fetch and display all conversations
loadConversation(id)             // Load specific conversation messages
createNewConversation()          // Create a new conversation
renderConversations(convs)       // Render conversations in sidebar
groupConversationsByTime(convs)  // Group by time periods

// Helper Functions
formatRelativeTime(timestamp)    // Format timestamp to Arabic relative time
renderConversationItem(conv)     // Generate HTML for single conversation
attachConversationListeners()    // Attach click handlers
displayMessages(messages)        // Display messages in chat
clearChatInterface()             // Clear current conversation
```

## State Management

```javascript
// Global Variables
currentConversationId  // ID of currently active conversation
API_BASE_URL          // Backend API base URL

// Local Storage
localStorage.getItem('auth_token')  // JWT authentication token
```

## API Calls Quick Reference

```javascript
// Get all conversations
GET /api/conversations
Headers: { Authorization: Bearer <token> }

// Get specific conversation  
GET /api/conversations/{id}
Headers: { Authorization: Bearer <token> }

// Create new conversation
POST /api/conversations
Headers: { Authorization: Bearer <token>, Content-Type: application/json }
Body: { title: "محادثة جديدة" }

// Delete conversation
DELETE /api/conversations/{id}
Headers: { Authorization: Bearer <token> }
```

## Animations & Transitions

| Element | Animation | Duration | Timing |
|---------|-----------|----------|--------|
| Sidebar open/close | translateX | 0.4s | cubic-bezier(0.4, 0, 0.2, 1) |
| Toggle button pulse | box-shadow | 2s | infinite |
| Conversation hover | transform + border | 0.3s | ease |
| Conversation shimmer | gradient slide | 0.5s | ease |
| Button click | scale | 0.15s | ease |

## Color Palette

```css
--primary-blue: #3b82f6;   /* Main blue */
--dark-blue: #1e40af;      /* Dark blue */
--light-blue: #60a5fa;     /* Light blue */
--white: #ffffff;          /* White */
--off-white: #f8fafc;      /* Off white */
--text-dark: #1e293b;      /* Dark text */
--text-light: #64748b;     /* Light/gray text */
```

## Responsive Breakpoints

```css
/* Desktop */
@media (min-width: 769px) {
  .sidebar { width: 320px; }
}

/* Tablet */
@media (max-width: 768px) {
  .sidebar { width: 280px; }
  .sidebar-toggle-btn { width: 45px; height: 45px; }
}

/* Mobile */
@media (max-width: 480px) {
  .sidebar { width: 100%; }
  .sidebar-title { font-size: 1.1rem; }
}
```

## Common Issues & Solutions

### Issue: Sidebar not opening
**Solution**: Check if JavaScript event listeners are attached. Console should show logs when clicking toggle button.

### Issue: Conversations not loading
**Solution**: 
1. Check API_BASE_URL is correct
2. Verify auth token exists: `localStorage.getItem('auth_token')`
3. Check browser console for CORS errors

### Issue: Active state not updating
**Solution**: Ensure `currentConversationId` is being set correctly in `loadConversation()`

### Issue: Timestamps not showing correctly
**Solution**: Verify `formatRelativeTime()` is receiving valid ISO timestamp strings

### Issue: Sidebar won't close on mobile
**Solution**: Check that click-outside detection is working, or use the X button

## Performance Tips

1. **Lazy Loading**: Load only recent conversations initially
2. **Virtual Scrolling**: For users with 100+ conversations
3. **Debouncing**: Debounce search input if adding search feature
4. **Caching**: Cache conversation list in localStorage
5. **Pagination**: Load conversations in batches of 20-30

## Testing Checklist

- [ ] Sidebar opens when clicking toggle button
- [ ] Sidebar closes when clicking X button
- [ ] Sidebar closes when clicking outside
- [ ] Conversations load and display correctly
- [ ] Time grouping works (Today, Yesterday, etc.)
- [ ] Clicking conversation loads messages
- [ ] Active state highlights correctly
- [ ] New conversation button creates new conversation
- [ ] New conversation clears active states
- [ ] Timestamps format correctly in Arabic
- [ ] Responsive design works on mobile
- [ ] Animations are smooth (60fps)
- [ ] Hover effects work properly
- [ ] Authentication token is sent with requests
- [ ] Error handling shows appropriate messages

## Browser DevTools Tips

```javascript
// Check current conversation
console.log('Current:', currentConversationId);

// Force open sidebar
document.getElementById('conversationsSidebar').classList.add('open');

// Force close sidebar
document.getElementById('conversationsSidebar').classList.remove('open');

// Get all conversations
document.querySelectorAll('.conversation-item');

// Trigger conversation load manually
loadConversation('conv_123');

// Create new conversation manually
createNewConversation();
```

---

**Print this card** and keep it handy while developing! 📋
