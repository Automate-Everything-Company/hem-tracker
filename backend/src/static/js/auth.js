function getToken() {
    return localStorage.getItem('token');
}

function attachTokenToHeaders(headers = {}) {
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

function fetchWithToken(url, options = {}) {
    options.headers = attachTokenToHeaders(options.headers || {});
    return fetch(url, options);
}

function logout() {
    localStorage.removeItem('token');
    updateHeader().then(() => {
        window.location.href = '/login';
    });
}

function isTokenExpired(token) {
    const payloadBase64 = token.split('.')[1];
    const decodedJson = atob(payloadBase64);
    const decoded = JSON.parse(decodedJson);
    const exp = decoded.exp;
    const now = Math.floor(Date.now() / 1000);
    return now >= exp;
}

function checkTokenExpiration() {
    const token = localStorage.getItem('token');
    if (token && isTokenExpired(token)) {
        logout();
    }
}

async function validateToken(token) {
    try {
        const response = await fetch('/validate-token', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        return response.ok;
    } catch (error) {
        console.error('Error validating token:', error);
        return false;
    }
}

setInterval(checkTokenExpiration, 60000);