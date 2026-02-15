# Backend Integration Guide for Conversation Sidebar

## Overview
This guide provides step-by-step instructions for integrating the frontend conversation sidebar with your FastAPI backend.

## API Endpoints Required

### 1. Get All Conversations
**Endpoint**: `GET /api/conversations`

**Description**: Retrieves all conversations for the current user, grouped by time periods.

**Request Headers**:
```http
Authorization: Bearer <jwt_token>
```

**Response**:
```json
{
  "conversations": [
    {
      "id": "conv_123",
      "title": "أعراض نزلات البرد",
      "preview": "ما هي الأعراض الشائعة لنزلات البرد؟",
      "last_message_at": "2026-02-03T13:00:00Z",
      "message_count": 5,
      "is_active": true
    },
    {
      "id": "conv_124",
      "title": "فوائد فيتامين د",
      "preview": "ما هي الفوائد الصحية لفيتامين د؟",
      "last_message_at": "2026-02-03T10:00:00Z",
      "message_count": 3,
      "is_active": false
    }
  ],
  "total": 8
}
```

**Backend Implementation** (FastAPI):
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/api/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversations = db.query(Conversation)\
        .filter(Conversation.user_id == current_user.id)\
        .order_by(Conversation.last_message_at.desc())\
        .all()
    
    return {
        "conversations": [
            {
                "id": str(conv.id),
                "title": conv.title or conv.messages[0].content[:50],
                "preview": conv.messages[0].content[:100] if conv.messages else "",
                "last_message_at": conv.last_message_at.isoformat(),
                "message_count": len(conv.messages),
                "is_active": conv.is_active
            }
            for conv in conversations
        ],
        "total": len(conversations)
    }
```

### 2. Get Conversation Messages
**Endpoint**: `GET /api/conversations/{conversation_id}`

**Description**: Retrieves all messages from a specific conversation.

**Path Parameters**:
- `conversation_id`: UUID of the conversation

**Response**:
```json
{
  "id": "conv_123",
  "title": "أعراض نزلات البرد",
  "created_at": "2026-02-03T12:00:00Z",
  "messages": [
    {
      "id": "msg_1",
      "role": "user",
      "content": "ما هي الأعراض الشائعة لنزلات البرد؟",
      "created_at": "2026-02-03T12:00:00Z"
    },
    {
      "id": "msg_2",
      "role": "assistant",
      "content": "الأعراض الشائعة لنزلات البرد تشمل...",
      "created_at": "2026-02-03T12:00:15Z"
    }
  ]
}
```

**Backend Implementation**:
```python
@router.get("/api/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation)\
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )\
        .first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in conversation.messages
        ]
    }
```

### 3. Create New Conversation
**Endpoint**: `POST /api/conversations`

**Description**: Creates a new conversation for the user.

**Request Body**:
```json
{
  "title": "محادثة جديدة" // Optional, can be auto-generated
}
```

**Response**:
```json
{
  "id": "conv_125",
  "title": "محادثة جديدة",
  "created_at": "2026-02-03T14:00:00Z",
  "messages": []
}
```

**Backend Implementation**:
```python
from pydantic import BaseModel
from typing import Optional

class CreateConversationRequest(BaseModel):
    title: Optional[str] = None

@router.post("/api/conversations")
async def create_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = Conversation(
        user_id=current_user.id,
        title=request.title or "محادثة جديدة",
        created_at=datetime.utcnow(),
        last_message_at=datetime.utcnow(),
        is_active=True
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "messages": []
    }
```

### 4. Delete Conversation (Optional)
**Endpoint**: `DELETE /api/conversations/{conversation_id}`

**Description**: Soft deletes a conversation.

**Response**:
```json
{
  "success": true,
  "message": "تم حذف المحادثة بنجاح"
}
```

**Backend Implementation**:
```python
@router.delete("/api/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation)\
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )\
        .first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.is_deleted = True
    db.commit()
    
    return {
        "success": True,
        "message": "تم حذف المحادثة بنجاح"
    }
```

## Frontend JavaScript Updates

### 1. Initialize and Load Conversations

Replace the static HTML in `index.html` with this dynamic loader:

```javascript
// Configuration
const API_BASE_URL = 'http://localhost:8000';
let currentConversationId = null;

// Helper function to get auth token
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

// Helper function to format relative time in Arabic
function formatRelativeTime(timestamp) {
    const now = new Date();
    const date = new Date(timestamp);
    const diffInMs = now - date;
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
    
    if (diffInHours < 1) return 'منذ دقائق';
    if (diffInHours < 24) return `منذ ${diffInHours} ساعة`;
    if (diffInDays === 1) return 'أمس';
    if (diffInDays < 7) return `منذ ${diffInDays} أيام`;
    if (diffInDays < 30) return `منذ ${Math.floor(diffInDays / 7)} أسبوع`;
    return `منذ ${Math.floor(diffInDays / 30)} شهر`;
}

// Group conversations by time period
function groupConversationsByTime(conversations) {
    const now = new Date();
    const groups = {
        today: [],
        yesterday: [],
        lastWeek: [],
        older: []
    };
    
    conversations.forEach(conv => {
        const date = new Date(conv.last_message_at);
        const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
        
        if (diffInDays === 0) groups.today.push(conv);
        else if (diffInDays === 1) groups.yesterday.push(conv);
        else if (diffInDays < 7) groups.lastWeek.push(conv);
        else groups.older.push(conv);
    });
    
    return groups;
}

// Render conversations in sidebar
function renderConversations(conversations) {
    const groups = groupConversationsByTime(conversations);
    const conversationsList = document.getElementById('conversationsList');
    
    let html = '';
    
    // Today
    if (groups.today.length > 0) {
        html += `
            <div class="conversation-group">
                <div class="conversation-group-title">اليوم</div>
                ${groups.today.map(conv => renderConversationItem(conv)).join('')}
            </div>
        `;
    }
    
    // Yesterday
    if (groups.yesterday.length > 0) {
        html += `
            <div class="conversation-group">
                <div class="conversation-group-title">أمس</div>
                ${groups.yesterday.map(conv => renderConversationItem(conv)).join('')}
            </div>
        `;
    }
    
    // Last Week
    if (groups.lastWeek.length > 0) {
        html += `
            <div class="conversation-group">
                <div class="conversation-group-title">آخر 7 أيام</div>
                ${groups.lastWeek.map(conv => renderConversationItem(conv)).join('')}
            </div>
        `;
    }
    
    // Older
    if (groups.older.length > 0) {
        html += `
            <div class="conversation-group">
                <div class="conversation-group-title">أقدم</div>
                ${groups.older.map(conv => renderConversationItem(conv)).join('')}
            </div>
        `;
    }
    
    conversationsList.innerHTML = html;
    
    // Re-attach event listeners
    attachConversationListeners();
}

// Render individual conversation item
function renderConversationItem(conversation) {
    const isActive = conversation.id === currentConversationId ? 'active' : '';
    return `
        <div class="conversation-item ${isActive}" data-conversation-id="${conversation.id}">
            <div class="conversation-item-title">${conversation.title}</div>
            <div class="conversation-item-preview">${conversation.preview}</div>
            <div class="conversation-item-time">${formatRelativeTime(conversation.last_message_at)}</div>
        </div>
    `;
}

// Attach event listeners to conversation items
function attachConversationListeners() {
    const items = document.querySelectorAll('.conversation-item');
    items.forEach(item => {
        item.addEventListener('click', function() {
            const conversationId = this.getAttribute('data-conversation-id');
            loadConversation(conversationId);
        });
    });
}

// Load conversations from API
async function loadConversations() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/conversations`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load conversations');
        
        const data = await response.json();
        renderConversations(data.conversations);
    } catch (error) {
        console.error('Error loading conversations:', error);
        // Show error message to user
    }
}

// Load specific conversation
async function loadConversation(conversationId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load conversation');
        
        const conversation = await response.json();
        currentConversationId = conversationId;
        
        // Update UI
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-conversation-id="${conversationId}"]`)?.classList.add('active');
        
        // Display messages in chat interface
        displayMessages(conversation.messages);
        
        // Close sidebar
        setTimeout(() => {
            document.getElementById('conversationsSidebar').classList.remove('open');
        }, 300);
        
    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

// Create new conversation
async function createNewConversation() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/conversations`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: 'محادثة جديدة'
            })
        });
        
        if (!response.ok) throw new Error('Failed to create conversation');
        
        const newConversation = await response.json();
        currentConversationId = newConversation.id;
        
        // Clear current chat
        clearChatInterface();
        
        // Reload conversations list
        await loadConversations();
        
        // Close sidebar
        setTimeout(() => {
            document.getElementById('conversationsSidebar').classList.remove('open');
        }, 300);
        
    } catch (error) {
        console.error('Error creating conversation:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadConversations();
    
    // Update new conversation button
    document.getElementById('newConversationBtn').addEventListener('click', createNewConversation);
});
```

### 2. Helper Functions

Add these helper functions to your JavaScript:

```javascript
// Display messages in chat interface
function displayMessages(messages) {
    const chatContainer = document.getElementById('chatMessages');
    if (!chatContainer) return;
    
    chatContainer.innerHTML = messages.map(msg => `
        <div class="message ${msg.role}">
            <div class="message-content">${msg.content}</div>
            <div class="message-time">${formatTime(msg.created_at)}</div>
        </div>
    `).join('');
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Clear chat interface
function clearChatInterface() {
    const chatContainer = document.getElementById('chatMessages');
    if (chatContainer) {
        chatContainer.innerHTML = '';
    }
    currentConversationId = null;
}

// Format time
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ar-EG', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}
```

## Database Schema Updates

Make sure your database has these tables:

```sql
-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    INDEX idx_user_conversations (user_id, last_message_at DESC),
    INDEX idx_active_conversations (user_id, is_active, is_deleted)
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_conversation_messages (conversation_id, created_at ASC)
);
```

## Testing Checklist

- [ ] Load conversations on page load
- [ ] Group conversations correctly by time period
- [ ] Click conversation loads messages
- [ ] Create new conversation works
- [ ] Active state updates correctly
- [ ] Sidebar closes after actions
- [ ] Relative time formatting is correct
- [ ] Authentication tokens are included
- [ ] Error handling works
- [ ] Real-time updates (if WebSocket implemented)

## Environment Variables

Add to your `.env` file:

```env
# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30000

# Feature Flags
ENABLE_CONVERSATION_HISTORY=true
MAX_CONVERSATIONS_DISPLAY=50
```

## Next Steps

1. ✅ Implement API endpoints in FastAPI backend
2. ✅ Update frontend JavaScript with API calls
3. ✅ Test authentication flow
4. ✅ Add error handling and loading states
5. ✅ Implement WebSocket for real-time updates (optional)
6. ✅ Add conversation search functionality
7. ✅ Add conversation deletion with confirmation
8. ✅ Add conversation export feature

---

**Status**: Ready for Integration
**Priority**: High
**Estimated Time**: 2-3 hours
