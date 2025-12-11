document.addEventListener('DOMContentLoaded', function() {
    loadMySnippets();
});

async function loadMySnippets() {
    const token = localStorage.getItem('auth_token');

    if (!token) {
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch('/snippets/my', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            displayMySnippets(data.snippets);
        } else if (response.status === 401) {
            localStorage.removeItem('auth_token');
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error');
    }
}

function displayMySnippets(snippets) {
    const container = document.getElementById('my-snippets');

    if (!snippets || snippets.length === 0) {
        container.innerHTML = '<p>You haven\'t created any snippets yet.</p>';
        return;
    }

    let html = '';
    snippets.forEach(snippet => {
        html += `
            <div class="snippet-card">
                <h3>${escapeHtml(snippet.title)}</h3>
                <pre>${escapeHtml(snippet.code.substring(0, 200))}${snippet.code.length > 200 ? '...' : ''}</pre>

                <div class="snippet-meta">
                    <span>${new Date(snippet.created_at).toLocaleDateString()}</span>
                    <span>❤️ ${snippet.like_count} likes</span>
                </div>

                <div class="actions-buttons">
                    <button onclick="editSnippet(${snippet.id})" class="btn">Edit</button>
                    <button onclick="deleteSnippet(${snippet.id})" class="btn btn-danger">Delete</button>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function editSnippet(id) {
    window.location.href = `/edit-snippet.html?id=${id}`;
}

async function deleteSnippet(id) {
    if (!confirm('Are you sure you want to delete this snippet?')) {
        return;
    }

    const token = localStorage.getItem('auth_token');

    try {
        const response = await fetch(`/snippets/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('Snippet deleted successfully');
            loadMySnippets(); // Refresh the list
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail || 'Failed to delete'}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    const container = document.getElementById('my-snippets');
    container.innerHTML = `<p class="error">${message}</p>`;
}