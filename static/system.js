document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    setInterval(fetchStats, 2000);
});

async function fetchStats() {
    try {
        const response = await fetch('/api/system/stats');
        const data = await response.json();

        if (data.error) throw new Error(data.error);

        updateGauge('cpu', data.cpu);
        updateGauge('disk', data.disk);
        
        document.getElementById('ram-val').textContent = Math.round(data.ram.percent) + '%';
        document.getElementById('ram-bar').style.width = data.ram.percent + '%';
        document.getElementById('ram-detail').textContent = `${data.ram.used} / ${data.ram.total} GB`;

        document.getElementById('uptime-val').textContent = data.uptime;
        document.getElementById('os-badge').textContent = data.os;

    } catch (e) {
        console.error("Stats error:", e);
    }
}

function updateGauge(id, value) {
    const valEl = document.getElementById(`${id}-val`);
    const barEl = document.getElementById(`${id}-bar`);
    
    if (valEl) valEl.textContent = Math.round(value) + '%';
    if (barEl) barEl.style.width = value + '%';
}

async function confirmPower(action) {
    const msg = action === 'reboot' 
        ? "Are you sure you want to REBOOT the host system?" 
        : "Are you sure you want to SHUTDOWN the host system?";
        
    if (!confirm(msg)) return;

    try {
        Toast.show(`Initiating ${action}...`, 'info');
        
        const response = await fetch('/api/system/power', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ action })
        });
        
        const data = await response.json();
        
        if (data.success) {
            Toast.show('Command sent successfully. See you on the other side!', 'success');
        } else {
            Toast.show('Error: ' + data.error, 'error');
        }
    } catch (e) {
        Toast.show('Connection failed', 'error');
    }
}