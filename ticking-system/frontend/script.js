// Replace this string with your Terraform API Gateway Output URL when deploying!
const AWS_API_GATEWAY_URL = '';
const API_URL = AWS_API_GATEWAY_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000/api' : '/api');
const form = document.getElementById('ticket-form');
const submitBtn = document.getElementById('submit-btn');
const btnText = document.querySelector('.btn-text');
const loader = document.querySelector('.loader');
const formMessage = document.getElementById('form-message');
const ticketsList = document.getElementById('tickets-list');

// Auth Check
const token = localStorage.getItem('token');
const username = localStorage.getItem('username');

if (!token) {
    window.location.href = 'login.html';
}

document.getElementById('user-info').innerHTML = `
    <span>User: <strong>${username}</strong></span>
    <a href="#" class="logout-btn" onclick="logout()" style="background: rgba(239, 68, 68, 0.2); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.3); padding: 0.25rem 0.75rem; border-radius: 5px; cursor: pointer; text-decoration: none; font-size: 0.8rem;">Logout</a>
`;

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = 'login.html';
}

// Listeners
form.addEventListener('submit', handleFormSubmit);

// Initial Load
document.addEventListener('DOMContentLoaded', fetchTickets);

async function handleFormSubmit(e) {
    e.preventDefault();

    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();

    if (!title || !description) return;

    setLoading(true);

    try {
        const response = await fetch(`${API_URL}/tickets/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ title, description }),
        });

        if (response.status === 401 || response.status === 403) {
            logout();
            return;
        }

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Network response was not ok');
        }

        const newTicket = await response.json();

        showMessage(`Ticket classified as ${newTicket.category} successfully!`, 'success');
        form.reset();

        // Refresh list
        fetchTickets();
    } catch (error) {
        console.error('Error submitting ticket:', error);
        showMessage(error.message || 'Failed to submit ticket. Please try again.', 'error');
    } finally {
        setLoading(false);
    }
}

async function fetchTickets() {
    try {
        const response = await fetch(`${API_URL}/tickets/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.status === 401 || response.status === 403) {
            logout();
            return;
        }
        if (!response.ok) throw new Error('Failed to fetch tickets');

        const tickets = await response.json();
        renderTickets(tickets);
    } catch (error) {
        console.error('Error fetching tickets:', error);
        ticketsList.innerHTML = `<div class="message-error" style="padding:1rem; border-radius: 0.5rem; text-align:center;">Failed to load tickets. Backend might be unreachable.</div>`;
    }
}

function renderTickets(tickets) {
    if (tickets.length === 0) {
        ticketsList.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 2rem;">No tickets found.</div>';
        return;
    }

    ticketsList.innerHTML = tickets.map(ticket => `
        <div class="ticket-item">
            <div class="ticket-content">
                <div class="ticket-title">${escapeHTML(ticket.title)}</div>
                <div class="ticket-desc">${escapeHTML(ticket.description)}</div>
                <div class="ticket-date">${new Date(ticket.created_at).toLocaleString()}</div>
            </div>
            <div>
                <span class="ticket-badge badge-${ticket.category.toLowerCase()}">${ticket.category}</span>
            </div>
        </div>
    `).join('');
}

function setLoading(isLoading) {
    if (isLoading) {
        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        formMessage.classList.add('hidden');
    } else {
        submitBtn.disabled = false;
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
    }
}

function showMessage(msg, type) {
    formMessage.textContent = msg;
    formMessage.className = '';
    formMessage.classList.add(`message-${type}`);

    setTimeout(() => {
        formMessage.classList.add('hidden');
    }, 5000);
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g,
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag])
    );
}
