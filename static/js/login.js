document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');

    if (loginForm) {
        loginForm.onsubmit = async function(e) {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    errorMessage.style.display = 'none';
                    successMessage.style.display = 'block';
                    successMessage.textContent = 'Login successful! Token: ' + data.token;
                    localStorage.setItem('auth_token', data.token);

                    window.location.href = '/dashboard';
                } else {
                    successMessage.style.display = 'none';
                    errorMessage.style.display = 'block';
                    errorMessage.textContent = data.error || 'Login failed';
                }
            } catch (error) {
                errorMessage.style.display = 'block';
                errorMessage.textContent = 'Network error';
            }
        };
    }
});