document.addEventListener('DOMContentLoaded', function() {
    const forgotPasswordLink = document.getElementById('forgotPasswordLink');
    const resetPasswordRequestForm = document.getElementById('resetPasswordRequestForm');
    const passwordResetRequestForm = document.getElementById('passwordResetRequestForm');

    if (forgotPasswordLink && resetPasswordRequestForm) {
        forgotPasswordLink.addEventListener('click', function(e) {
            e.preventDefault();
            resetPasswordRequestForm.classList.toggle('hidden');
        });
    }

    if (passwordResetRequestForm) {
        passwordResetRequestForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const resetIdentifier = document.getElementById('resetIdentifier').value;

            fetch('/request-password-reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ identifier: resetIdentifier }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.detail) {
                    alert(data.detail);
                } else {
                    alert('An error occurred. Please try again.');
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    }
});