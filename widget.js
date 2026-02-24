document.addEventListener('DOMContentLoaded', () => {
    const chatArea = document.getElementById('chatArea');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const userTierDisplay = document.getElementById('userTierDisplay');

    // 1) Initialize State from SessionStorage
    let currentToken = sessionStorage.getItem('widget_token') || null;
    let currentTier = sessionStorage.getItem('widget_tier') || 'Guest';

    // Update UI immediately on load
    updateTierUI(currentTier);

    // 2) Listen for messages from parent window
    window.addEventListener('message', (event) => {
        // Dynamic origin validation
        // In an embedded iframe context, event.origin gives the parent's origin.
        // We compare it against document.referrer (which contains the full parent URL in cross-origin iframes depending on policy, or at least the origin)
        const parentOrigin = event.origin;
        const referrer = document.referrer;

        // Simple dynamic validation: Ensure the referring document matches the event origin
        // If referrer is empty (e.g. direct load or strict policy), we allow it cautiously or check allowed lists.
        if (referrer && !referrer.startsWith(parentOrigin)) {
            console.warn('⚠️ Origin validation failed. Untrusted parent window:', parentOrigin);
            return;
        }

        // Must be a valid object with data
        if (!event.data || typeof event.data !== 'object') return;

        // Check for specific AUTH_DATA payload
        if (event.data.type === 'AUTH_DATA') {
            const { tier, token } = event.data;

            // Store received token securely in sessionStorage
            if (token) {
                currentToken = token;
                sessionStorage.setItem('widget_token', token);
            }

            // Update tier
            if (tier) {
                currentTier = tier;
                sessionStorage.setItem('widget_tier', tier);
            }

            console.log('✅ Auth data securely received in widget.');

            // Update the local chat state/UI to reflect user's tier
            updateTierUI(currentTier);
        }
    });

    // 3) UI Update Logic
    function updateTierUI(tier) {
        if (!tier) tier = 'Guest';

        if (tier.toLowerCase().includes('pro')) {
            userTierDisplay.textContent = '💎 مستخدم Pro';
            userTierDisplay.style.background = 'linear-gradient(135deg, #18c1f5, #009abb)';
            userTierDisplay.style.color = 'white';
            userTierDisplay.style.border = 'none';
        } else if (tier.toLowerCase().includes('free') || tier.includes('مجاني')) {
            userTierDisplay.textContent = '📋 مسجل مجاني';
            userTierDisplay.style.background = 'rgba(72, 187, 120, 0.15)';
            userTierDisplay.style.color = '#2f855a';
            userTierDisplay.style.border = '1px solid rgba(72, 187, 120, 0.3)';
        } else {
            userTierDisplay.textContent = '👤 زائر';
            userTierDisplay.style.background = 'rgba(24, 193, 245, 0.15)';
            userTierDisplay.style.color = 'var(--webteb-dark-cyan)';
            userTierDisplay.style.border = '1px solid rgba(24, 193, 245, 0.3)';
        }
    }

    // 4) Chat Interface Logic
    function appendMessage(text, sender) {
        if (!text.trim()) return;

        // Create message row
        const msgRow = document.createElement('div');
        msgRow.className = `message ${sender}`;

        // Create bubble
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;

        msgRow.appendChild(bubble);
        chatArea.appendChild(msgRow);

        // Auto-scroll to bottom
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    function handleSendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // Add user message to UI
        appendMessage(text, 'user');
        userInput.value = '';

        // Mocking bot response (Here you'd call your actual FastAPI backend with `currentToken`)
        setTimeout(() => {
            if (currentToken) {
                appendMessage('هذا رد اختباري. لقد تم مصادقة حسابك بنجاح باستخدام الـ Token الممرر.', 'bot');
            } else {
                appendMessage('هذا رد اختباري. أنت تتحدث الآن كزائر. يرجى تمرير التوكن للحصول على المزايا.', 'bot');
            }
        }, 800);
    }

    // 5) Event Listeners
    sendBtn.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent form submission
            handleSendMessage();
        }
    });
});
