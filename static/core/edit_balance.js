document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.editable-balance').forEach(function(input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                input.blur();
            }
        });
        input.addEventListener('blur', function() {
            const accountId = input.getAttribute('data-account-id');
            const newBalance = input.value;
            fetch('/ajax/update-balance/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ account_id: accountId, balance: newBalance })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                } else {
                    input.classList.remove('is-valid');
                    input.classList.add('is-invalid');
                }
                setTimeout(() => {
                    input.classList.remove('is-valid', 'is-invalid');
                }, 1500);
            })
            .catch(() => {
                input.classList.remove('is-valid');
                input.classList.add('is-invalid');
                setTimeout(() => {
                    input.classList.remove('is-invalid');
                }, 1500);
            });
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