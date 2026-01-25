/**
 * The Whole Thingymabob
 * it does the thingy, will document later, have to because uhm, we havent documented anything yet
 * + handles the drag and drop for payloads *ay im getting there with documentation*
 */
document.addEventListener('DOMContentLoaded', () => {
    loadsettings();
    loadTheme();
    fetch("/api/network_info")
        .then(r => r.json())
        .then(info => {
            const serverIpEl = document.getElementById("server-ip");
            const clientIpEl = document.getElementById("client-ip");
            if (serverIpEl) serverIpEl.textContent = info.server_ip || "Unknown";
            if (clientIpEl) clientIpEl.textContent = info.client_ip || "Unknown";
        })
        .catch(() => {
            const serverIpEl = document.getElementById("server-ip");
            const clientIpEl = document.getElementById("client-ip");
            if (serverIpEl) serverIpEl.textContent = "Unknown";
            if (clientIpEl) clientIpEl.textContent = "Unknown";
        });

    const dropZone = document.body;
    const fileInput = document.getElementById('fileInput');
    let dragLeaveTimer;

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    dropZone.addEventListener('dragenter', (e) => {
        dropZone.classList.add('drag-highlight');
        clearTimeout(dragLeaveTimer);
    }, false);

    dropZone.addEventListener('dragover', (e) => {
        dropZone.classList.add('drag-highlight');
        clearTimeout(dragLeaveTimer);
    }, false);

    dropZone.addEventListener('dragleave', (e) => {
        dragLeaveTimer = setTimeout(() => {
            dropZone.classList.remove('drag-highlight');
        }, 100);
    }, false);

    dropZone.addEventListener('drop', (e) => {
        clearTimeout(dragLeaveTimer);
        dropZone.classList.remove('drag-highlight');

        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) uploadPayload(files[0]);
    });

    if (fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) uploadPayload(fileInput.files[0]);
        });
    }
});

async function readJSON(filename) {
    try {
        const response = await fetch(filename);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching JSON:', error);
        throw error;
    }
}

async function getJSONValue(filename, property) {
    try {
        const data = await readJSON(filename);
        return data[property];
    } catch (error) {
        console.error('Error getting JSON value:', error);
        return null;
    }
}

async function uploadPayload(droppedFile = null) {
    const fileInput = document.getElementById('fileInput');
    const upBtn = document.getElementById('UPB');

    const file = (droppedFile instanceof File) ? droppedFile : fileInput.files[0];

    if (!file) {
        Toast.show('Please select a file first', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const originalText = upBtn.innerHTML;
    upBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Uploading...';
    upBtn.disabled = true;

    try {
        const response = await fetch('/upload_payload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(`Status ${response.status}`);

        Toast.show(`Successfully uploaded ${file.name}`, 'success');
        
        if (!droppedFile) fileInput.value = "";
        
        await loadpayloads();

    } catch (error) {
        console.error('Upload error:', error);
        Toast.show('Upload failed: ' + error.message, 'error');
    } finally {
        upBtn.innerHTML = originalText;
        upBtn.disabled = false;
    }
}

async function saveIP() {
    const ipInput = document.getElementById("IP");
    const ipValue = ipInput.value;
    if (ipValue.trim() !== "") {
        setip(ipValue);
    }
}

async function loadIP() {
    try {
        const savedIP = await getJSONValue('static/config/settings.json', 'ip');
        if (savedIP) {
            document.getElementById('IP').value = savedIP;
        } else {
            document.getElementById('IP').value = '';
        }

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('IP').innerHTML = 'Error loading IP';
    }
}

async function saveAJB() {
    const checkbox = document.getElementById("AJB-B");
    const isChecked = checkbox.checked;
    localStorage.setItem("savedAJB", isChecked);
    setajb(isChecked.toString());
}

async function loadAJB() {
    try {
        const savedAJB = await getJSONValue('static/config/settings.json', 'ajb');
        const checkbox = document.getElementById("AJB-B");
        const isTrue = (savedAJB === "true");
        checkbox.checked = isTrue;
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('IP').innerHTML = 'Error loading IP';
    }
}

async function setajb(str) {
    await fetch('/edit_ajb', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({content: str})
    });
}

async function setip(str) {
    await fetch('/edit_ip', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({content: str})
    });
}

async function saveFTPPort() {
    const portInput = document.getElementById("FTP_PORT");
    const portValue = portInput.value;
    if (portValue.trim() !== "") {
        await fetch('/edit_ftp_port', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({content: portValue})
        });
    }
}

async function loadFTPPort() {
    try {
        const savedPort = await getJSONValue('static/config/settings.json', 'ftp_port');
        if (savedPort) {
            document.getElementById('FTP_PORT').value = savedPort;
        } else {
            document.getElementById('FTP_PORT').value = '1337';
        }
    } catch (error) {
        console.error('Error loading FTP Port:', error);
    }
}

async function installDownload0() {
    const btn = document.getElementById('btn-update-dl0');
    const originalText = btn.innerHTML;

    if (!confirm("Install local download0.dat to PS5? Ensure you updated it in Repos first.")) return;

    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Installing...';
    btn.disabled = true;

    try {
        const response = await fetch('/tools/update_download0', {method: 'POST'});
        const data = await response.json();

        if (data.success) {
            Toast.show(data.message, 'success');
        } else {
            Toast.show('Error: ' + data.message, 'error');
        }
    } catch (error) {
        Toast.show('Connection Error: ' + error, 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function blockUpdates() {
    const btn = document.getElementById('btn-block-upd');
    const originalText = btn.innerHTML;

    if (!confirm("This will patch system files to block updates. Proceed?")) return;

    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Patching...';
    btn.disabled = true;

    try {
        const response = await fetch('/tools/block_updates', {method: 'POST'});
        const data = await response.json();

        if (data.success) {
            Toast.show(data.message, 'success');
        } else {
            Toast.show('Error: ' + data.message, 'error');
        }
    } catch (error) {
        Toast.show('Connection Error: ' + error, 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function SendPayload(str = "") {
    const btn = document.getElementById('SJB');

    try {
        if (!str) {
            btn.disabled = true;
            btn.classList.add('opacity-80', 'cursor-wait');
            btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-3xl"></i><span>Running...</span>';
        } else {
            Toast.show('Sending payload...', 'info');
        }

        const response = await fetch('/send_payload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                payload: str,
                IP: document.getElementById('IP').value
            })
        });

        const data = await response.json();

        if (response.ok) {
            if (!str) Toast.show('Jailbreak command sent!', 'success');
            else Toast.show('Payload sent successfully', 'success');
        } else {
            Toast.show(data.error || 'Failed to send payload', 'error');
        }

    } catch (error) {
        Toast.show('Connection Error: ' + error, 'error');
    } finally {
        if (!str) {
            btn.disabled = false;
            btn.classList.remove('opacity-80', 'cursor-wait');
            btn.innerHTML = '<i class="fa-solid fa-bolt text-3xl"></i><span>Jailbreak</span>';
        }
    }
}

async function DeletePayload(str) {
    if (!confirm(`Delete ${str}?`)) return;

    try {
        const response = await fetch('/delete_payload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({payload: str})
        });

        if (response.ok) {
            Toast.show(`${str} deleted`, 'success');
            await loadpayloads();
        } else {
            Toast.show('Failed to delete file', 'error');
        }
    } catch (error) {
        Toast.show(error.message, 'error');
    }
}

async function loadsettings() {
    await loadIP();
    await loadFTPPort();
    await loadAJB();
    await loadpayloads();
}

async function togglePayloadIndex(filename, checkbox) {
    const enabled = checkbox.checked;
    const configKey = filename.split('/').pop();

    const card = checkbox.closest('.draggable-item');
    const nameSpan = card?.querySelector('.payload-name');
    const chip = card?.querySelector('.fa-microchip');

    if (nameSpan) {
        if (enabled) {
            nameSpan.classList.add('text-brand-light', 'font-bold');
            nameSpan.classList.remove('opacity-90');
            chip?.classList.add('text-brand-light', 'opacity-100');
            chip?.classList.remove('opacity-40');
        } else {
            nameSpan.classList.remove('text-brand-light', 'font-bold');
            nameSpan.classList.add('opacity-90');
            chip?.classList.remove('text-brand-light', 'opacity-100');
            chip?.classList.add('opacity-40');
        }
    }

    try {
        const response = await fetch('/api/payload_config/toggle', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filename: configKey, enabled})
        });

        if (!response.ok) throw new Error("API Error");

        Toast.show(`${configKey} ${enabled ? 'enabled' : 'disabled'} for autoload`, 'info');

    } catch (e) {
        console.error(e);
        Toast.show('Failed to update setting', 'error');
        checkbox.checked = !enabled;
    }
}

async function togglePayloadDelay(filename, btn) {
    const isEnabled = btn.classList.contains('text-brand-light');
    const newState = !isEnabled;

    const card = btn.closest('.draggable-item');
    const delayBadge = card.querySelector('.delay-indicator');

    if (newState) {
        btn.classList.add('text-brand-light', 'font-bold');
        btn.classList.remove('opacity-70');
        btn.classList.add('bg-brand-blue/20', 'border-brand-blue/50');
        if (delayBadge) delayBadge.classList.remove('hidden');
    } else {
        btn.classList.remove('text-brand-light', 'font-bold');
        btn.classList.add('opacity-70');
        btn.classList.remove('bg-brand-blue/20', 'border-brand-blue/50');
        if (delayBadge) delayBadge.classList.add('hidden');
    }

    try {
        const response = await fetch('/api/payload_delays/toggle', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filename, enabled: newState})
        });

        if (response.ok) {
            Toast.show(`Delay ${newState ? 'enabled' : 'disabled'} for ${filename}`, 'info');
        } else {
            throw new Error("API Error");
        }
    } catch (e) {
        console.error(e);
        Toast.show('Failed to toggle delay', 'error');
        if (!newState) {
            btn.classList.add('text-brand-light', 'font-bold');
            btn.classList.remove('opacity-70');
        } else {
            btn.classList.remove('text-brand-light', 'font-bold');
            btn.classList.add('opacity-70');
        }
    }
}

async function loadpayloads() {
    try {
        const [filesRes, configRes, orderRes, delaysRes] = await Promise.all([
            fetch('/list_payloads'),
            fetch('/api/payload_config'),
            fetch('/api/payload_order'),
            fetch('/api/payload_delays')
        ]);

        let files = await filesRes.json();
        const config = await configRes.json();
        const order = await orderRes.json();
        const delays = await delaysRes.json();

        const listElement = document.getElementById('PL');
        const countElement = document.getElementById('payload-count');

        if (countElement) {
            countElement.textContent = files ? files.length : 0;
        }

        listElement.innerHTML = '';

        if (!files || files.length === 0) {
            document.getElementById('empty-state').classList.remove('hidden');
            return;
        }

        document.getElementById('empty-state').classList.add('hidden');

        if (order && order.length > 0) {
            const weights = {};
            order.forEach((name, index) => weights[name] = index);
            files.sort((a, b) => {
                const wa = weights[a.split('/').pop()] ?? 9999;
                const wb = weights[b.split('/').pop()] ?? 9999;
                return wa - wb;
            });
        }

        files.forEach(file => {
            const configKey = file.split('/').pop();
            const isEnabled = config[configKey] !== false && config[file] !== false;
            const delayEnabled = delays[configKey] === true;

            const card = document.createElement('li');
            card.className = "draggable-item relative input-field border rounded-xl p-2 pr-2 flex items-center justify-between group transition-colors hover:border-brand-blue mb-3 bg-black/20";
            card.draggable = true;
            card.dataset.filename = configKey;

            const nameClass = isEnabled 
                ? "text-brand-light font-bold" 
                : "opacity-90";
            
            const chipClass = isEnabled 
                ? "text-brand-light opacity-100" 
                : "opacity-40";

            const delayClass = delayEnabled
                ? "text-brand-light font-bold"
                : "opacity-70";

            card.innerHTML = `
                <div class="flex items-center gap-2 overflow-hidden flex-1">
                    <div class="drag-handle touch-manipulation hidden sm:block p-2 cursor-grab active:cursor-grabbing text-white/20 hover:text-white transition-colors">
                        <i class="fa-solid fa-grip-vertical"></i>
                    </div>
                    
                    <div class="flex flex-col gap-0.5 sm:hidden px-1">
                        <button onclick="movePayload('${configKey}', -1)" class="text-white/30 hover:text-brand-light p-1 -mb-1" title="Move Up">
                            <i class="fa-solid fa-caret-up"></i>
                        </button>
                        <button onclick="movePayload('${configKey}', 1)" class="text-white/30 hover:text-brand-light p-1 -mt-1" title="Move Down">
                            <i class="fa-solid fa-caret-down"></i>
                        </button>
                    </div>

                    <div class="p-3 bg-gray-100 dark:bg-gray-800 rounded-lg shrink-0">
                        <i class="fa-solid fa-microchip text-xl ${chipClass} transition-colors"></i>
                    </div>
                    
                    <div class="flex flex-col overflow-hidden min-w-0 mr-2">
                        <span class="payload-name font-medium text-sm truncate select-none ${nameClass}" title="${file}">${file}</span>
                        <div class="flex items-center gap-1.5">
                            <span class="text-[10px] opacity-50 uppercase tracking-wide">Payload</span>
                            <i class="delay-indicator fa-solid fa-stopwatch text-brand-light text-[10px] ${delayEnabled ? '' : 'hidden'}" title="Delayed"></i>
                        </div>
                    </div>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                    <button onclick="SendPayload('payloads/${file}')" class="px-4 py-2 bg-gray-200 dark:bg-gray-800 hover:bg-brand-blue hover:text-white rounded-lg text-xs font-bold transition-colors shadow-sm whitespace-nowrap">
                        LOAD
                    </button>
                    
                    <div class="relative">
                        <button onclick="toggleDropdown(event, '${configKey}')" class="dropdown-trigger p-2 text-gray-400 hover:text-brand-light transition-colors rounded-lg hover:bg-white/5">
                            <i class="fa-solid fa-ellipsis-vertical text-lg px-1"></i>
                        </button>

                        <div id="dropdown-${configKey}" class="payload-dropdown hidden absolute right-0 top-full mt-2 w-56 bg-white dark:bg-[#1a1a1a] rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50">
                            
                            <label class="w-full flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors cursor-pointer">
                                <div class="flex flex-col">
                                    <span class="text-sm font-medium">Auto Load</span>
                                    <span class="text-[10px] opacity-50">ajb thingy</span>
                                </div>
                                <div class="relative inline-flex items-center pointer-events-none">
                                    <input type="checkbox" class="sr-only peer" onchange="togglePayloadIndex('${file}', this)" ${isEnabled ? 'checked' : ''}>
                                    <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-brand-blue"></div>
                                </div>
                            </label>

                            <button onclick="togglePayloadDelay('${configKey}', this)" 
                                class="w-full flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors text-left group ${delayClass}">
                                <div class="flex flex-col">
                                    <span class="text-sm font-medium">Start Delay</span>
                                    <span class="text-[10px] opacity-50">Wait before loading</span>
                                </div>
                                <i class="fa-solid fa-stopwatch group-hover:scale-110 transition-transform"></i>
                            </button>

                            <button onclick="DeletePayload('${file}')" class="w-full flex items-center justify-between px-4 py-3 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-left">
                                <span class="text-sm font-medium">Delete File</span>
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
            listElement.appendChild(card);
        });

        if (typeof enableDragSort === "function") {
            enableDragSort('PL', () => {
                saveCurrentOrder('PL');
            });
        }

    } catch (e) {
        console.error(e);
        Toast.show('Failed to load payloads', 'error');
    }
}

document.getElementById('SJB').addEventListener('click', function (event) {
    event.preventDefault();
    SendPayload();
});

function toggleMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuIcon = document.getElementById('mobile-menu-icon');

    if (mobileMenu.dataset.hidden === 'true') {
        mobileMenu.className = 'lg:hidden';
        mobileMenu.dataset.hidden = 'false';
        mobileMenuIcon.className = 'fa-solid fa-x';
    } else {
        mobileMenu.className = 'hidden';
        mobileMenu.dataset.hidden = 'true';
        mobileMenuIcon.className = 'fa-solid fa-bars';
    }
}

async function movePayload(filename, direction) {
    const list = document.getElementById('PL');
    const items = Array.from(list.children);
    const index = items.findIndex(item => item.dataset.filename === filename);
    
    if (index === -1) return;
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= items.length) return;
    
    const currentItem = items[index];
    const swapItem = items[newIndex];

    if (direction < 0) {
        list.insertBefore(currentItem, swapItem);
    } else {
        list.insertBefore(swapItem, currentItem);
    }

    await saveCurrentOrder('PL');
}

function toggleDropdown(event, id) {
    event.stopPropagation();
    const dropdown = document.getElementById(`dropdown-${id}`);
    
    document.querySelectorAll('.payload-dropdown').forEach(el => {
        if (el.id !== `dropdown-${id}`) el.classList.add('hidden');
    });

    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-trigger') && !e.target.closest('.payload-dropdown')) {
         document.querySelectorAll('.payload-dropdown').forEach(el => el.classList.add('hidden'));
    }
});