document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('create-form');
    const messageDiv = document.getElementById('message');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const token = localStorage.getItem('auth_token');
        if (!token) {
            showMessage('Please login first', 'error');
            window.location.href = '/login';
            return;
        }

        const title = document.getElementById('title').value;
        const code = document.getElementById('code').value;
        const description = document.getElementById('description').value;

        if (!title || !code) {
            showMessage('Title and code are required', 'error');
            return;
        }

        try {
            const response = await fetch('/snippets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    title: title,
                    code: code,
                    description: description || null
                })
            });

            if (response.ok) {
                showMessage('Snippet created successfully!', 'success');
                form.reset();

                // Redirect to my snippets after 2 seconds
                setTimeout(() => {
                    window.location.href = '/my-snippets';
                }, 2000);
            } else {
                const error = await response.json();
                showMessage(`Error: ${error.detail || 'Failed to create snippet'}`, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('Network error', 'error');
        }
    });
});

function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.style.display = 'block';

    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}