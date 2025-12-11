document.addEventListener('DOMContentLoaded', function() {
    loadAllSnippets();
});

async function loadAllSnippets() {
    try {
        const response = await fetch('/snippets');
        const data = await response.json();

        const container = document.getElementById('snippets-list');

        if (data.snippets.length === 0) {
            container.innerHTML = '<p>No snippets found. Be the first to create one!</p>';
            return;
        }

        let html = '';
        data.snippets.forEach(snippet => {
            html += `
                <div class="snippet-card">
                    <h3>${snippet.title}</h3>
                    <pre>${escapeHtml(snippet.code)}</pre>
                    ${snippet.description ? `<p>${escapeHtml(snippet.description)}</p>` : ''}

                    <div class="snippet-meta">
                        <span>By: ${snippet.author.nick_name}</span>
                        <span>${new Date(snippet.created_at).toLocaleDateString()}</span>
                    </div>

                    <div class="snippet-meta">
                        <span>❤️ ${snippet.like_count} likes</span>
                        <a href="#" onclick="viewSnippet(${snippet.id})">View details</a>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading snippets:', error);
        document.getElementById('snippets-list').innerHTML =
            '<p class="error">Error loading snippets</p>';
    }
}

function viewSnippet(id) {
    window.location.href = `/snippet-detail.html?id=${id}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}