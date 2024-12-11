function redirectToUserPage(username) {
    fetchWithToken(`/api/users/${username}`)
        .then(response => {
            if (response.ok) {
                return response.text();
            } else {
                throw new Error('Failed to load user page');
            }
        })
        .then(htmlContent => {
            const parser = new DOMParser();
            const newDoc = parser.parseFromString(htmlContent, 'text/html');

            document.open();
            document.write(newDoc.documentElement.outerHTML);
            document.close();

            history.pushState(null, '', `/api/users/${username}`);

            initializePage();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load user page. Please try logging in again.');
        });
}

function initializePage() {
    // Re-attach event listeners or run any necessary initialization code here
    // For example:
    if (typeof updateHeader === 'function') {
        updateHeader();
    }
    // Add any other initialization functions you need
}