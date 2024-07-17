document.addEventListener('DOMContentLoaded', function() {
    const resetPasswordForm = document.getElementById('resetPasswordForm');
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const resetToken = document.getElementById('resetToken').value;

            if (newPassword !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }

            fetch('/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: resetToken, new_password: newPassword }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.detail) {
                    alert(data.detail);
                    window.location.href = '/login';
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