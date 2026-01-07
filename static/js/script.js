/* ============================================================================
   LOANVISTA - INTERACTIVE FUNCTIONALITY
   ============================================================================ */

// ============================================================================
// SLIDER VALUE UPDATES
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all sliders
    const sliders = {
        'person_age': { suffix: ' years', format: (v) => Math.round(v) },
        'person_income': { suffix: '', format: (v) => '₹' + Number(v).toLocaleString() },
        'person_emp_exp': { suffix: ' years', format: (v) => Math.round(v) },
        'loan_amnt': { suffix: '', format: (v) => '₹' + Number(v).toLocaleString() },
        'credit_score': { suffix: '', format: (v) => Math.round(v) },
        'cb_person_cred_hist_length': { suffix: ' years', format: (v) => Number(v).toFixed(1) }
    };

    // Update slider values
    Object.keys(sliders).forEach(sliderId => {
        const slider = document.getElementById(sliderId);
        const valueDisplay = document.getElementById(sliderId + '_value');
        const config = sliders[sliderId];

        if (slider && valueDisplay) {
            // Update on input
            slider.addEventListener('input', function() {
                valueDisplay.textContent = config.format(this.value) + config.suffix;
            });

            // Initialize display
            valueDisplay.textContent = config.format(slider.value) + config.suffix;
        }
    });
});

// ============================================================================
// SMOOTH SCROLLING
// ============================================================================

function scrollToApplication() {
    document.getElementById('application').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Navigation link smooth scrolling
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetSection = document.querySelector(targetId);

        if (targetSection) {
            targetSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });

            // Update active link
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        }
    });
});

// Update active nav link on scroll
window.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('section[id]');
    const scrollPos = window.scrollY + 100;

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');

        if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
});

// ============================================================================
// FORM SUBMISSION & PREDICTION
// ============================================================================

document.getElementById('loanForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // Get form data
    const formData = {
        person_age: parseFloat(document.getElementById('person_age').value),
        person_gender: document.getElementById('person_gender').value,
        person_education: document.getElementById('person_education').value,
        person_income: parseFloat(document.getElementById('person_income').value),
        person_emp_exp: parseInt(document.getElementById('person_emp_exp').value),
        person_home_ownership: document.getElementById('person_home_ownership').value,
        loan_amnt: parseFloat(document.getElementById('loan_amnt').value),
        loan_intent: document.getElementById('loan_intent').value,
        cb_person_cred_hist_length: parseFloat(document.getElementById('cb_person_cred_hist_length').value),
        credit_score: parseInt(document.getElementById('credit_score').value),
        previous_loan_defaults_on_file: document.getElementById('previous_loan_defaults_on_file').value
    };

    // Show loading state
    const submitButton = this.querySelector('.submit-button');
    const buttonText = submitButton.querySelector('span');
    const buttonLoader = submitButton.querySelector('.button-loader');

    buttonText.style.display = 'none';
    buttonLoader.style.display = 'block';
    submitButton.disabled = true;

    try {
        // Send prediction request
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            displayResult(data.result);

            // Trigger confetti if approved
            if (data.result.prediction === 1) {
                triggerConfetti();
            }
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Error processing application: ' + error.message);
    } finally {
        // Reset button state
        buttonText.style.display = 'inline';
        buttonLoader.style.display = 'none';
        submitButton.disabled = false;
    }
});

// ============================================================================
// DISPLAY RESULT
// ============================================================================

function displayResult(result) {
    const resultSection = document.getElementById('resultSection');
    const resultContent = document.getElementById('resultContent');

    const isApproved = result.prediction === 1;
    const probability = (result.probability * 100).toFixed(1);

    let confidenceText = '';
    if (isApproved) {
        if (result.probability < 0.6) {
            confidenceText = 'Marginal approval - Additional review recommended';
        } else if (result.probability < 0.75) {
            confidenceText = 'Moderate confidence approval';
        } else {
            confidenceText = 'High confidence approval';
        }
    } else {
        if (result.probability > 0.4) {
            confidenceText = 'Borderline case - Manual review suggested';
        } else if (result.probability > 0.3) {
            confidenceText = 'Moderate confidence rejection';
        } else {
            confidenceText = 'High confidence rejection';
        }
    }

    const html = `
        <div class="result-header">
            <div class="result-icon">${isApproved ? '✅' : '❌'}</div>
            <h2 class="result-title">${isApproved ? 'Loan Approved!' : 'Loan Rejected'}</h2>
            <p class="result-probability">Confidence: ${probability}%</p>
            <p style="color: var(--gray-700); margin-top: 0.5rem;">${confidenceText}</p>
        </div>

        <div class="result-details">
            <div class="detail-row">
                <span class="detail-label">Applicant Age</span>
                <span class="detail-value">${result.application_data.person_age} years</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Annual Income</span>
                <span class="detail-value">$${result.application_data.person_income.toLocaleString()}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Loan Amount</span>
                <span class="detail-value">$${result.application_data.loan_amnt.toLocaleString()}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Credit Score</span>
                <span class="detail-value">${result.application_data.credit_score}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Loan Purpose</span>
                <span class="detail-value">${result.application_data.loan_intent}</span>
            </div>
        </div>

        ${result.risk_factors.length > 0 ? `
            <div class="risk-factors">
                <h4>Risk Factors</h4>
                <ul>
                    ${result.risk_factors.map(factor => `<li>${factor}</li>`).join('')}
                </ul>
            </div>
        ` : `
            <div class="risk-factors" style="background: #d4edda; color: #155724;">
                <h4>✓ No Major Risk Factors Identified</h4>
            </div>
        `}
    `;

    resultContent.innerHTML = html;
    resultSection.style.display = 'block';

    // Add appropriate class
    const resultCard = resultSection.querySelector('.result-card');
    resultCard.classList.remove('result-approved', 'result-rejected');
    resultCard.classList.add(isApproved ? 'result-approved' : 'result-rejected');

    // Scroll to result
    setTimeout(() => {
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 300);
}

// ============================================================================
// CONFETTI ANIMATION
// ============================================================================

function triggerConfetti() {
    const duration = 3000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 10000 };

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        const particleCount = 50 * (timeLeft / duration);

        // Confetti from left
        confetti({
            ...defaults,
            particleCount,
            origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
            colors: ['#d4af37', '#e6c75a', '#f5e1a4', '#0a1628', '#ffffff']
        });

        // Confetti from right
        confetti({
            ...defaults,
            particleCount,
            origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
            colors: ['#d4af37', '#e6c75a', '#f5e1a4', '#0a1628', '#ffffff']
        });
    }, 250);
}

// ============================================================================
// DOWNLOAD REPORT
// ============================================================================

document.getElementById('downloadReport').addEventListener('click', async function() {
    try {
        // Show loading state
        const button = this;
        const originalText = button.innerHTML;
        button.innerHTML = '<span>Generating Report...</span>';
        button.disabled = true;

        const response = await fetch('/api/download-report');

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            // Get filename from response header or use default
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'loan_application_report.png';
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Reset button
            button.innerHTML = originalText;
            button.disabled = false;
        } else {
            // Try to get error message from response
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.message || 'Error downloading report';
            alert(errorMessage);

            // Reset button
            button.innerHTML = originalText;
            button.disabled = false;
        }
    } catch (error) {
        console.error('Download error:', error);
        alert('Error downloading report: ' + error.message);

        // Reset button
        this.innerHTML = this.innerHTML.replace('Generating Report...', '');
        this.disabled = false;
    }
});

// ============================================================================
// CHATBOT FUNCTIONALITY
// ============================================================================

let chatbotVisible = false;
let popupTimeout;

const chatbotToggle = document.getElementById('chatbotToggle');
const chatbotWindow = document.getElementById('chatbotWindow');
const closeChatbot = document.getElementById('closeChatbot');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatMessages = document.getElementById('chatMessages');

// Auto-popup after 10 seconds
popupTimeout = setTimeout(() => {
    if (!chatbotVisible) {
        chatbotWindow.classList.add('active');
        chatbotVisible = true;
    }
}, 10000);

// Toggle chatbot
chatbotToggle.addEventListener('click', function() {
    chatbotVisible = !chatbotVisible;
    chatbotWindow.classList.toggle('active');

    // Clear the auto-popup timeout if user manually opens
    clearTimeout(popupTimeout);

    if (chatbotVisible) {
        chatInput.focus();
    }
});

// Close chatbot
closeChatbot.addEventListener('click', function() {
    chatbotVisible = false;
    chatbotWindow.classList.remove('active');
});

// Handle chat form submission
chatForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message
    addChatMessage('user', message);
    chatInput.value = '';

    // Show typing indicator
    const typingIndicator = addTypingIndicator();

    try {
        // Send message to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // Remove typing indicator
        typingIndicator.remove();

        if (data.success) {
            addChatMessage('bot', data.message);
        } else {
            addChatMessage('bot', 'Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        typingIndicator.remove();
        addChatMessage('bot', 'Sorry, I\'m having trouble connecting. Please try again.');
    }
});

// Add chat message to UI
function addChatMessage(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Format the message with proper line breaks and lists
    const formattedMessage = formatChatMessage(message);
    contentDiv.innerHTML = formattedMessage;

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format chat message for better display
function formatChatMessage(message) {
    // Replace numbered lists (1., 2., etc.) with HTML list items
    let formatted = message.replace(/(\d+\.\s+[^\n]+)/g, '<div class="chat-list-item">$1</div>');

    // Replace bullet points (-, *, •) with styled bullets
    formatted = formatted.replace(/^[\-\*•]\s+(.+)$/gm, '<div class="chat-bullet">• $1</div>');

    // Replace double line breaks with paragraph breaks
    formatted = formatted.replace(/\n\n/g, '</p><p>');

    // Replace single line breaks with <br>
    formatted = formatted.replace(/\n/g, '<br>');

    // Wrap in paragraph if not already wrapped
    if (!formatted.includes('<p>')) {
        formatted = '<p>' + formatted + '</p>';
    }

    // Bold text between asterisks or double asterisks
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    return formatted;
}

// Add typing indicator
function addTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot-message';
    messageDiv.id = 'typingIndicator';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<span style="opacity: 0.6;">Typing...</span>';

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}

// ============================================================================
// FADE-IN ANIMATIONS ON SCROLL
// ============================================================================

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for fade-in animation
document.querySelectorAll('.feature-card, .form-section').forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(30px)';
    element.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(element);
});