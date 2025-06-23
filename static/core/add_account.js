document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('addAccountForm');
    const errorDiv = document.getElementById('addAccountError');
    if (!form) return;
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';

        const account_name = document.getElementById('account_name').value;
        const amount_type = document.getElementById('amount_type').value;
        if (!account_name.trim()) {
            errorDiv.textContent = 'Account name is required.';
            errorDiv.style.display = 'block';
            return;
        }

        fetch('/ajax/add-account/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ account_name, amount_type })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                errorDiv.classList.remove('text-danger');
                errorDiv.classList.add('text-success');
                errorDiv.textContent = data.message;
                errorDiv.style.display = 'block';
                setTimeout(() => {
                    var modal = bootstrap.Modal.getInstance(document.getElementById('addAccountModal'));
                    modal.hide();
                    form.reset();
                    errorDiv.classList.remove('text-success');
                    window.location.reload();
                }, 1000);
            } else {
                errorDiv.classList.remove('text-success');
                errorDiv.classList.add('text-danger');
                errorDiv.textContent = data.message;
                errorDiv.style.display = 'block';
            }
        })
        .catch(() => {
            errorDiv.textContent = 'An error occurred. Please try again.';
            errorDiv.style.display = 'block';
        });
    });
});

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