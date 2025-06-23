document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('changePasswordForm');
    const errorDiv = document.getElementById('changePasswordError');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';

        const current_password = document.getElementById('current_password').value;
        const new_password = document.getElementById('new_password').value;
        const confirm_password = document.getElementById('confirm_password').value;

        if (new_password !== confirm_password) {
            errorDiv.textContent = 'New passwords do not match.';
            errorDiv.style.display = 'block';
            return;
        }

        fetch('/ajax/change-password/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                current_password,
                new_password,
                confirm_password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                errorDiv.classList.remove('text-danger');
                errorDiv.classList.add('text-success');
                errorDiv.textContent = data.message;
                errorDiv.style.display = 'block';
                setTimeout(() => {
                    var modal = bootstrap.Modal.getInstance(document.getElementById('changePasswordModal'));
                    modal.hide();
                    form.reset();
                    errorDiv.classList.remove('text-success');
                }, 1500);
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