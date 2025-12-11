document.addEventListener('DOMContentLoaded', function() {
    checkAuthAndLoadUser();
});

async function checkAuthAndLoadUser() {
    const token = localStorage.getItem('auth_token');

    if (!token) {
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch('/user', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            displayUserInfo(user);
        } else {
            localStorage.removeItem('auth_token');
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error');
    }
}

function displayUserInfo(user) {
    const userInfoDiv = document.getElementById('user-info');
    userInfoDiv.innerHTML = `
        <div class="user-card">
            <h3>👤 ${user.nick_name || user.email}</h3>
            <p>Email: ${user.email}</p>
            <p>Name: ${user.first_name || ''} ${user.last_name || ''}</p>
            <p>Member since: ${new Date(user.created_at).toLocaleDateString()}</p>
        </div>
    `;
}

function logout() {
    const token = localStorage.getItem('auth_token');

    if (token) {
        fetch('/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }).catch(console.error);
    }

    localStorage.removeItem('auth_token');
    window.location.href = '/login';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.className = 'error';
    errorDiv.style.display = 'block';
}