document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('register-form');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');

    if (registerForm) {
        registerForm.onsubmit = async function(e) {
            e.preventDefault();

            const formData = {
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                first_name: document.getElementById('first_name').value || null,
                last_name: document.getElementById('last_name').value || null,
                nick_name: document.getElementById('nick_name').value || null
            };

            console.log('Sending registration data:', formData);

            try {
                // ВАЖНО: Используем /register вместо /user
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                console.log('Response status:', response.status);

                if (response.ok) {
                    const data = await response.json();
                    console.log('Registration successful:', data);

                    errorMessage.style.display = 'none';
                    successMessage.style.display = 'block';
                    successMessage.textContent = data.message + ' User ID: ' + data.user_id;
                    registerForm.reset();

                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                } else {
                    const errorData = await response.json();
                    console.log('Registration error:', errorData);

                    successMessage.style.display = 'none';
                    errorMessage.style.display = 'block';
                    errorMessage.textContent = errorData.detail || 'Registration failed';
                }
            } catch (error) {
                console.error('Network error:', error);
                errorMessage.style.display = 'block';
                errorMessage.textContent = 'Network error: ' + error.message;
            }
        };
    }
});