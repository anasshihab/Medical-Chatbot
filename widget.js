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

    async function handleSendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // Retrieve the token and tier securely from sessionStorage
        const token = sessionStorage.getItem('widget_token') || currentToken;
        const tier = sessionStorage.getItem('widget_tier') || currentTier || 'Guest';

        // 1) Enforce Exact UI Rate Limits based on tier
        const wordCount = text.split(/\s+/).filter(word => word.length > 0).length;
        let maxWords = 20; // Default for 'Guest'

        const tierLower = tier.toLowerCase();
        if (tierLower.includes('pro')) {
            maxWords = 1000;
        } else if (tierLower.includes('free') || tier.includes('مجاني') || tierLower.includes('registered')) {
            maxWords = 25;
        }

        if (wordCount > maxWords) {
            appendMessage(`عذراً، لقد تجاوزت الحد الأقصى للكلمات في هذه الرسالة. الحد المسموح به هو ${maxWords} كلمة.`, 'bot');
            return;
        }

        // Add user message to UI
        appendMessage(text, 'user');
        userInput.value = '';

        // Create an empty bot bubble for streaming the response chunk-by-chunk
        const msgRow = document.createElement('div');
        msgRow.className = 'message bot';
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        msgRow.appendChild(bubble);
        chatArea.appendChild(msgRow);
        chatArea.scrollTop = chatArea.scrollHeight;

        // 2) Connect to Custom Backend with fetch
        try {
            const headers = { 'Content-Type': 'application/json' };
            // Send the Authorization: Bearer <token> in the headers (if the token exists)
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            // Send the user's message in the JSON body
            const payload = { message: text };

            // To prevent throwing 401 when Guest mode is active in this project logic
            if (!token) {
                // Generate a persistent guest session locally if backend enforces it.
                // We'll safely attach guest_session_id based on typical requirements,
                // but if not required it normally ignores it.
                let localGuestId = sessionStorage.getItem('guest_session_id');
                if (!localGuestId) {
                    localGuestId = 'guest_' + Math.random().toString(36).substr(2, 9);
                    sessionStorage.setItem('guest_session_id', localGuestId);
                }
                payload.guest_session_id = localGuestId;
            }

            const response = await fetch('https://medical-chatbot-staging.onrender.com/api/chat', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                let errorMsg = 'عذراً، حدث خطأ أثناء الاتصال بالخادم.';
                try {
                    const errorData = await response.json();
                    if (errorData?.error?.message) errorMsg = errorData.error.message;
                } catch (e) { }
                bubble.textContent = errorMsg;
                return;
            }

            // 3) Handle Server-Sent Events (SSE) Streaming
            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const dataStr = line.replace('data: ', '').trim();
                        if (!dataStr || dataStr === '[DONE]') continue;

                        try {
                            const parsedData = JSON.parse(dataStr);
                            if (parsedData.type === 'content' && parsedData.data) {
                                bubble.textContent += parsedData.data;
                                chatArea.scrollTop = chatArea.scrollHeight;
                            } else if (parsedData.type === 'error' && parsedData.data?.error) {
                                bubble.textContent += '\n[خطأ: ' + parsedData.data.error + ']';
                                chatArea.scrollTop = chatArea.scrollHeight;
                            }
                        } catch (e) {
                            console.error('Error parsing SSE chunk:', e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Fetch error:', error);
            bubble.textContent = 'حدث خطأ في الاتصال بالخادم. الرجاء المحاولة لاحقاً.';
        }
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
