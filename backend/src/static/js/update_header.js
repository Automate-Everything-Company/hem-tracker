async function updateHeader() {
    const token = localStorage.getItem('token');
    const nav = document.querySelector('nav ul');
    if (token) {
        try {
            const response = await fetch('/validate-token', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                if (data.valid && data.username) {
                    nav.innerHTML = `
                        <li><a href="/">Home</a></li>
                        <li><a href="/about">About</a></li>
                        <li><a href="#" id="myDataLink">My Data</a></li>
                        <li><a href="/disclaimer">Disclaimer</a></li>
                        <li><a href="/contact">Contact</a></li>
                        <li><a href="#" onclick="logout()">Logout</a></li>
                    `;
                    setupMyDataLink(data.username);
                    return;
                }
            }
        } catch (error) {
            console.error('Error validating token:', error);
        }
    }
    setDefaultHeader();
}

function setupMyDataLink(username) {
    const myDataLink = document.getElementById('myDataLink');
    if (myDataLink) {
        myDataLink.addEventListener('click', (event) => {
            event.preventDefault();
            if (typeof redirectToUserPage === 'function') {
                redirectToUserPage(username);
            } else {
                console.error('redirectToUserPage function not found');
            }
        });
    }
}

function setDefaultHeader() {
    const nav = document.querySelector('nav ul');
    nav.innerHTML = `
        <li><a href="/">Home</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/login">Login</a></li>
        <li><a href="/signup">Sign up</a></li>
        <li><a href="/disclaimer">Disclaimer</a></li>
        <li><a href="/contact">Contact</a></li>
    `;
}

function logout() {
    localStorage.removeItem('token');
    updateHeader();
    window.location.href = '/login';
}

document.addEventListener('DOMContentLoaded', updateHeader);

window.updateHeader = updateHeader;