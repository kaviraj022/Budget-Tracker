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

// Edit Transaction Modal logic
function openEditTransactionModal(transactionId) {
    fetch(`/ajax/get-transaction/${transactionId}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const t = data.transaction;
            document.getElementById('editTransactionId').value = t.id;
            document.getElementById('editTransactionType').value = t.transaction_type;
            document.getElementById('editTransactionAmount').value = t.amount;
            document.getElementById('editTransactionDescription').value = t.description;
            document.getElementById('editTransactionDate').value = t.transaction_date;
            // Show/hide account fields based on type
            if (t.transaction_type === 'INCOME' || t.transaction_type === 'EXPENSE') {
                document.getElementById('editTransactionAccountGroup').classList.remove('d-none');
                document.getElementById('editTransactionFromAccountGroup').classList.add('d-none');
                document.getElementById('editTransactionToAccountGroup').classList.add('d-none');
                document.getElementById('editTransactionAccount').value = t.account_id;
            } else if (t.transaction_type === 'TRANSFER') {
                document.getElementById('editTransactionAccountGroup').classList.add('d-none');
                document.getElementById('editTransactionFromAccountGroup').classList.remove('d-none');
                document.getElementById('editTransactionToAccountGroup').classList.remove('d-none');
                document.getElementById('editTransactionFromAccount').value = t.from_account_id;
                document.getElementById('editTransactionToAccount').value = t.to_account_id;
            }
            var modal = new bootstrap.Modal(document.getElementById('editTransactionModal'));
            modal.show();
        } else {
            alert('Failed to load transaction data.');
        }
    });
}

document.addEventListener('click', function(e) {
    const btn = e.target.closest('.edit-transaction-btn');
    if (btn) {
        const transactionId = btn.getAttribute('data-transaction-id');
        openEditTransactionModal(transactionId);
    }
});

document.getElementById('editTransactionType').addEventListener('change', function() {
    const type = this.value;
    if (type === 'INCOME' || type === 'EXPENSE') {
        document.getElementById('editTransactionAccountGroup').classList.remove('d-none');
        document.getElementById('editTransactionFromAccountGroup').classList.add('d-none');
        document.getElementById('editTransactionToAccountGroup').classList.add('d-none');
    } else if (type === 'TRANSFER') {
        document.getElementById('editTransactionAccountGroup').classList.add('d-none');
        document.getElementById('editTransactionFromAccountGroup').classList.remove('d-none');
        document.getElementById('editTransactionToAccountGroup').classList.remove('d-none');
    }
});

document.getElementById('editTransactionForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const id = document.getElementById('editTransactionId').value;
    const type = document.getElementById('editTransactionType').value;
    let data = {
        transaction_type: type,
        amount: document.getElementById('editTransactionAmount').value,
        description: document.getElementById('editTransactionDescription').value,
        transaction_date: document.getElementById('editTransactionDate').value
    };
    if (type === 'INCOME' || type === 'EXPENSE') {
        data.account_id = document.getElementById('editTransactionAccount').value;
    } else if (type === 'TRANSFER') {
        data.from_account_id = document.getElementById('editTransactionFromAccount').value;
        data.to_account_id = document.getElementById('editTransactionToAccount').value;
    }
    fetch(`/ajax/edit-transaction/${id}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        const errorDiv = document.getElementById('editTransactionError');
        if (data.success) {
            errorDiv.style.display = 'none';
            var modal = bootstrap.Modal.getInstance(document.getElementById('editTransactionModal'));
            modal.hide();
            window.location.reload();
        } else {
            errorDiv.textContent = data.message;
            errorDiv.style.display = 'block';
        }
    });
}); 