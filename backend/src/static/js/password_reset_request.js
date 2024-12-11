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

            fetch('/api/password/request-reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ identifier: resetIdentifier }),
            })
                .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => {
                        throw new Error(errData.message || 'An error occurred. Please try again.');
                    });
                }
                return response.json();
            })
                .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    alert('Password reset instructions have been sent to your email.');
                }
            })
                .catch((error) => {
                console.error('Error:', error);
                alert(error.message || 'An error occurred. Please try again.');
            });
        });
    }
});