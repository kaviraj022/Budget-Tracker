document.addEventListener('DOMContentLoaded', function() {
    // Open rename modal
    document.querySelectorAll('.rename-account-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const accountId = btn.getAttribute('data-account-id');
            const currentName = document.getElementById('accountName-' + accountId).textContent.trim();
            document.getElementById('renameAccountId').value = accountId;
            document.getElementById('renameAccountName').value = currentName;
            document.getElementById('renameAccountError').style.display = 'none';
            var modal = new bootstrap.Modal(document.getElementById('renameAccountModal'));
            modal.show();
        });
    });

    // Submit rename form
    document.getElementById('renameAccountForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const accountId = document.getElementById('renameAccountId').value;
        const newName = document.getElementById('renameAccountName').value.trim();
        const errorDiv = document.getElementById('renameAccountError');
        if (!newName) {
            errorDiv.textContent = 'Account name is required.';
            errorDiv.style.display = 'block';
            return;
        }
        fetch(`/ajax/rename-account/${accountId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ account_name: newName })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                errorDiv.style.display = 'none';
                document.getElementById('accountName-' + accountId).textContent = newName;
                var modal = bootstrap.Modal.getInstance(document.getElementById('renameAccountModal'));
                modal.hide();
            } else {
                errorDiv.textContent = data.message;
                errorDiv.style.display = 'block';
            }
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