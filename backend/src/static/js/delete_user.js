function deleteUser() {
    const username = document.getElementById('username').value;

    if (confirm(`Are you sure you want to delete the user ${username}? This action cannot be undone.`)) {
        fetchWithToken(`/api/users/${username}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(error => {
                    alert(`Error deleting user: ${error.detail}`);
                });
            }
            return response.json();
        })
        .then(data => {
            alert('User deleted successfully.');
            window.location.href = '/'; // Redirect to the homepage after deletion
        })
        .catch(error => console.error('Error deleting user:', error));
    }
}