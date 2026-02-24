document.addEventListener('DOMContentLoaded', () => {
    const scanForm = document.getElementById('scanForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const errorMessage = document.getElementById('errorMessage');

    if (scanForm) {
        scanForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const urlInput = document.getElementById('targetUrl');
            const url = urlInput.value;

            // Show loading
            loadingOverlay.style.display = 'flex';
            errorMessage.style.display = 'none';

            try {
                const formData = new FormData();
                formData.append('url', url);

                const response = await fetch('/scan', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    // Store results in session storage and redirect
                    sessionStorage.setItem('scanResults', JSON.stringify(data));
                    window.location.href = '/results';
                } else {
                    loadingOverlay.style.display = 'none';
                    errorMessage.textContent = data.detail || data.error || 'An error occurred during scanning.';
                    errorMessage.style.display = 'block';
                }
            } catch (err) {
                loadingOverlay.style.display = 'none';
                errorMessage.textContent = 'Failed to connect to the server.';
                errorMessage.style.display = 'block';
            }
        });
    }
});

function displayResults(data) {
    document.getElementById('scannedUrl').textContent = `Target: ${data.target_url}`;
    document.getElementById('totalVulns').textContent = data.summary.total;
    document.getElementById('highVulns').textContent = data.summary.high;
    document.getElementById('mediumVulns').textContent = data.summary.medium;
    document.getElementById('lowVulns').textContent = data.summary.low;

    const tableBody = document.getElementById('vulnTableBody');
    const noVulns = document.getElementById('noVulnsMessage');

    if (data.vulnerabilities.length === 0) {
        document.querySelector('.vuln-table-container').style.display = 'none';
        noVulns.style.display = 'block';
    } else {
        tableBody.innerHTML = '';
        data.vulnerabilities.forEach(vuln => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td style="font-weight: 600;">${vuln.type}</td>
                <td><span class="severity-badge badge-${vuln.severity.toLowerCase()}">${vuln.severity}</span></td>
                <td style="color: var(--text-secondary); line-height: 1.5;">${vuln.description}</td>
            `;
            tableBody.appendChild(row);
        });
    }
}
