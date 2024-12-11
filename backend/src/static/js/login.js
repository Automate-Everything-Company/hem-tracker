document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const username = formData.get('username');
    const password = formData.get('password');

    fetch('/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({username, password})
    })
    .then(response => response.json())
    .then(data => {
        if (data.access_token) {
            localStorage.setItem('token', data.access_token);
            if (typeof updateHeader === 'function') {
                updateHeader().then(() => redirectToUserPage(username));
            } else {
                redirectToUserPage(username);
            }
        } else {
            alert('Login failed: ' + (data.detail || 'Unknown error'));
        }
    })
    .catch(error => console.error('Error logging in:', error));
});

// Expose the redirectToUserPage function globally
window.redirectToUserPage = redirectToUserPage;