// CSRF token helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Add Transaction Modal AJAX logic
const addTransactionForm = document.getElementById('addTransactionForm');
addTransactionForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const type = document.getElementById('addTransactionType').value;
    let data = {
        transaction_type: type,
        amount: document.getElementById('addTransactionAmount').value,
        description: document.getElementById('addTransactionDescription').value,
        transaction_date: document.getElementById('addTransactionDate').value
    };
    if (type === 'INCOME' || type === 'EXPENSE') {
        data.account_id = document.getElementById('addTransactionAccount').value;
    } else if (type === 'TRANSFER') {
        data.from_account_id = document.getElementById('addTransactionFromAccount').value;
        data.to_account_id = document.getElementById('addTransactionToAccount').value;
    }
    fetch('/ajax/add-transaction/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        const errorDiv = document.getElementById('addTransactionError');
        if (data.success) {
            errorDiv.style.display = 'none';
            addTransactionForm.reset();
            var modal = bootstrap.Modal.getInstance(document.getElementById('addTransactionModal'));
            modal.hide();
            window.location.reload();
        } else {
            errorDiv.textContent = data.message;
            errorDiv.style.display = 'block';
        }
    });
});

// AJAX delete for transaction
function setupDeleteButtons() {
    document.querySelectorAll('.transaction-row form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!confirm('Are you sure you want to delete this transaction?')) return;
            const action = form.getAttribute('action');
            fetch(`/ajax/delete-transaction/${action.split('/').filter(Boolean).pop()}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    alert(data.message);
                }
            });
        });
    });
}
document.addEventListener('DOMContentLoaded', setupDeleteButtons); 