// Configuration
const API_BASE_URL = 'http://localhost:8000'; // Change this to your deployed backend URL

// Persisted success message configuration
const SUB_SUCCESS_KEY = 'newsletter_sub_success_v1';
const SUB_SUCCESS_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours

// DOM Elements
const subscribeForm = document.getElementById('subscribeForm');
const subscribeBtn = document.getElementById('subscribeBtn');
const emailInput = document.getElementById('email');
const successMessage = document.getElementById('successMessage');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

const unsubscribeForm = document.getElementById('unsubscribeForm');
const unsubscribeBtn = document.getElementById('unsubscribeBtn');
const unsubscribeEmail = document.getElementById('unsubscribeEmail');
const unsubscribeSuccess = document.getElementById('unsubscribeSuccess');
const unsubscribeError = document.getElementById('unsubscribeError');
const unsubscribeErrorText = document.getElementById('unsubscribeErrorText');
const alternatives = document.getElementById('alternatives');

// Utility Functions
function showLoading(button) {
    button.disabled = true;
    const btnText = button.querySelector('.btn-text');
    const btnLoading = button.querySelector('.btn-loading');
    if (btnText) btnText.style.display = 'none';
    if (btnLoading) btnLoading.style.display = 'flex';
}

function hideLoading(button) {
    button.disabled = false;
    const btnText = button.querySelector('.btn-text');
    const btnLoading = button.querySelector('.btn-loading');
    if (btnText) btnText.style.display = 'inline';
    if (btnLoading) btnLoading.style.display = 'none';
}

function showMessage(element) {
    element.style.display = 'block';
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideMessage(element) {
    if (element) {
        element.style.display = 'none';
    }
}

function hideAllMessages() {
    hideMessage(successMessage);
    hideMessage(errorMessage);
    hideMessage(unsubscribeSuccess);
    hideMessage(unsubscribeError);
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function persistSubscribeSuccess(email) {
    try {
        const payload = { ts: Date.now(), email: email || '' };
        localStorage.setItem(SUB_SUCCESS_KEY, JSON.stringify(payload));
    } catch {}
}

function restoreSubscribeSuccessIfRecent() {
    try {
        const raw = localStorage.getItem(SUB_SUCCESS_KEY);
        if (!raw) return;
        const payload = JSON.parse(raw);
        if (!payload || !payload.ts) return;
        if (Date.now() - payload.ts > SUB_SUCCESS_TTL_MS) {
            localStorage.removeItem(SUB_SUCCESS_KEY);
            return;
        }
        if (subscribeForm && successMessage) {
            subscribeForm.style.display = 'none';
            showMessage(successMessage);
        }
    } catch {}
}

function clearSubscribeSuccess() {
    try { localStorage.removeItem(SUB_SUCCESS_KEY); } catch {}
}

// API Functions
async function makeAPIRequest(endpoint, method, data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || `HTTP error! status: ${response.status}`);
        }

        return result;
    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Unable to connect to the server. Please check your internet connection and try again.');
        }
        throw error;
    }
}

// Subscribe Functionality
async function handleSubscribe(event) {
    event.preventDefault();
    
    const email = emailInput.value.trim();
    
    // Validate email
    if (!email) {
        errorText.textContent = 'Please enter your email address.';
        showMessage(errorMessage);
        return;
    }
    
    if (!validateEmail(email)) {
        errorText.textContent = 'Please enter a valid email address.';
        showMessage(errorMessage);
        return;
    }
    
    hideAllMessages();
    showLoading(subscribeBtn);
    
    try {
        const result = await makeAPIRequest('/subscribe', 'POST', { email });
        
        hideLoading(subscribeBtn);
        
        if (result.success) {
            // Persist success state to keep message visible for a long time
            persistSubscribeSuccess(email);
            
            subscribeForm.style.display = 'none';
            showMessage(successMessage);
            
            // Track subscription (optional analytics)
            if (typeof gtag !== 'undefined') {
                gtag('event', 'subscribe', {
                    'event_category': 'newsletter',
                    'event_label': 'email_subscription'
                });
            }
        } else {
            throw new Error(result.message || 'Failed to subscribe');
        }
    } catch (error) {
        hideLoading(subscribeBtn);
        
        // Handle specific error cases
        if (error.message.includes('already subscribed')) {
            errorText.textContent = 'This email is already subscribed to our newsletter.';
        } else if (error.message.includes('invalid email')) {
            errorText.textContent = 'Please enter a valid email address.';
        } else {
            errorText.textContent = error.message || 'Something went wrong. Please try again later.';
        }
        
        showMessage(errorMessage);
        
        // Track error (optional analytics)
        if (typeof gtag !== 'undefined') {
            gtag('event', 'subscribe_error', {
                'event_category': 'newsletter',
                'event_label': error.message
            });
        }
    }
}

// Unsubscribe Functionality
async function handleUnsubscribe(event) {
    event.preventDefault();
    
    const email = unsubscribeEmail.value.trim();
    
    // Validate email
    if (!email) {
        unsubscribeErrorText.textContent = 'Please enter your email address.';
        showMessage(unsubscribeError);
        return;
    }
    
    if (!validateEmail(email)) {
        unsubscribeErrorText.textContent = 'Please enter a valid email address.';
        showMessage(unsubscribeError);
        return;
    }
    
    hideAllMessages();
    showLoading(unsubscribeBtn);
    
    try {
        const result = await makeAPIRequest('/unsubscribe', 'POST', { email });
        
        hideLoading(unsubscribeBtn);
        
        if (result.success) {
            unsubscribeForm.style.display = 'none';
            if (alternatives) alternatives.style.display = 'none';
            showMessage(unsubscribeSuccess);
            
            // On unsubscribe, clear any previous subscribe success persistence
            clearSubscribeSuccess();
            
            // Track unsubscription (optional analytics)
            if (typeof gtag !== 'undefined') {
                gtag('event', 'unsubscribe', {
                    'event_category': 'newsletter',
                    'event_label': 'email_unsubscription'
                });
            }
        } else {
            throw new Error(result.message || 'Failed to unsubscribe');
        }
    } catch (error) {
        hideLoading(unsubscribeBtn);
        
        // Handle specific error cases
        if (error.message.includes('not found') || error.message.includes('not subscribed')) {
            unsubscribeErrorText.textContent = 'This email address is not in our subscriber list.';
        } else if (error.message.includes('already unsubscribed')) {
            unsubscribeErrorText.textContent = 'This email is already unsubscribed.';
        } else {
            unsubscribeErrorText.textContent = error.message || 'Something went wrong. Please try again later.';
        }
        
        showMessage(unsubscribeError);
        
        // Track error (optional analytics)
        if (typeof gtag !== 'undefined') {
            gtag('event', 'unsubscribe_error', {
                'event_category': 'newsletter',
                'event_label': error.message
            });
        }
    }
}

// Auto-fill unsubscribe email from URL parameter
function handleUnsubscribeAutoFill() {
    const urlParams = new URLSearchParams(window.location.search);
    const email = urlParams.get('email');
    
    if (email && unsubscribeEmail) {
        unsubscribeEmail.value = decodeURIComponent(email);
    }
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Form validation improvements
function addInputValidation() {
    // Real-time email validation
    [emailInput, unsubscribeEmail].forEach(input => {
        if (input) {
            input.addEventListener('input', function() {
                const email = this.value.trim();
                
                if (email && !validateEmail(email)) {
                    this.style.borderColor = '#ef4444';
                } else {
                    this.style.borderColor = '#e1e5e9';
                }
            });
            
            // Clear validation on focus
            input.addEventListener('focus', function() {
                this.style.borderColor = '#667eea';
            });
        }
    });
}

// Keyboard accessibility
function addKeyboardAccessibility() {
    // Allow Enter key to submit forms
    [emailInput, unsubscribeEmail].forEach(input => {
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const form = this.closest('form');
                    if (form) {
                        form.dispatchEvent(new Event('submit'));
                    }
                }
            });
        }
    });
}

// Loading animation for better UX
function addLoadingAnimations() {
    // Add subtle animations to cards
    const cards = document.querySelectorAll('.benefit-card, .option-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => observer.observe(card));
}

// Error recovery
function addErrorRecovery() {
    // Retry mechanism for failed requests
    let retryCount = 0;
    const maxRetries = 3;
    
    window.addEventListener('online', () => {
        if (retryCount > 0) {
            console.log('Connection restored. You can try again.');
            // Optionally show a toast notification
        }
    });
    
    window.addEventListener('offline', () => {
        console.log('Connection lost. Please check your internet connection.');
        // Optionally show a toast notification
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Restore a previously successful subscription state (show message for long time)
    restoreSubscribeSuccessIfRecent();

    // Add event listeners
    if (subscribeForm) {
        subscribeForm.addEventListener('submit', handleSubscribe);
    }
    
    if (unsubscribeForm) {
        unsubscribeForm.addEventListener('submit', handleUnsubscribe);
        handleUnsubscribeAutoFill();
    }
    
    // Initialize enhancements
    initSmoothScrolling();
    addInputValidation();
    addKeyboardAccessibility();
    addLoadingAnimations();
    addErrorRecovery();
    
    // Performance optimization: Preload API endpoint for faster response
    if ('requestIdleCallback' in window) {
        requestIdleCallback(() => {
            // Preload API endpoint for faster response
            fetch(`${API_BASE_URL}/health`).catch(() => {
                // Silently fail if health check fails
            });
        });
    }
});

// Expose functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateEmail,
        makeAPIRequest,
        handleSubscribe,
        handleUnsubscribe,
        persistSubscribeSuccess,
        restoreSubscribeSuccessIfRecent,
        clearSubscribeSuccess
    };
}
