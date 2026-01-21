document.addEventListener('DOMContentLoaded', loadSettings);

async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const config = await response.json();

        if (config.ip) document.getElementById('ip').value = config.ip;
        if (config.ftp_port) document.getElementById('ftp_port').value = config.ftp_port;
        
        if (config.global_delay) {
            document.getElementById('global_delay').value = config.global_delay;
        } else {
            document.getElementById('global_delay').value = "5";
        }
        
        const ajbCheckbox = document.getElementById('ajb');
        ajbCheckbox.checked = config.ajb === 'true';

        const animCheckbox = document.getElementById('ui_animations');
        const animationsEnabled = config.ui_animations === 'true';
        animCheckbox.checked = animationsEnabled;
        
        localStorage.setItem('animations', animationsEnabled);

    } catch (error) {
        console.error('Error loading settings:', error);
        Toast.show('Failed to load settings', 'error');
    }
}

async function saveAllSettings() {
    const ip = document.getElementById('ip').value;
    const ftpPort = document.getElementById('ftp_port').value;
    const globalDelay = document.getElementById('global_delay').value;
    const ajb = document.getElementById('ajb').checked ? "true" : "false";
    const uiAnimations = document.getElementById('ui_animations').checked ? "true" : "false";

    const payload = {
        ip: ip,
        ftp_port: ftpPort,
        global_delay: globalDelay,
        ajb: ajb,
        ui_animations: uiAnimations
    };

    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.success) {
            localStorage.setItem('animations', uiAnimations);
            Toast.show('Settings saved successfully!', 'success');
        } else {
            Toast.show('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        Toast.show('Connection error while saving', 'error');
    }
}