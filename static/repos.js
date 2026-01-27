let currentRepos = {};

function toggleFields() {
    const type = document.getElementById('repo-type').value;
    const urlField = document.getElementById('field-url');
    const ghField = document.getElementById('field-github');

    if(type === 'direct') {
        urlField.classList.remove('hidden');
        ghField.classList.add('hidden');
    } else {
        urlField.classList.add('hidden');
        ghField.classList.remove('hidden');
    }
}

function openModal() {
    const modal = document.getElementById('repoModal');
    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('repoModal').classList.add('hidden');
}

async function loadRepos() {
    const tableBody = document.getElementById('repoTable');
    const loading = document.getElementById('loading');
    
    try {
        const response = await fetch('/api/repos/list');
        const repos = await response.json();
        
        if (loading) loading.classList.add('hidden');
        tableBody.innerHTML = '';
        
        if (Object.keys(repos).length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="p-8 text-center opacity-30">
                        <i class="fa-solid fa-box-open text-4xl mb-2"></i>
                        <p>No repositories configured</p>
                    </td>
                </tr>`;
            return;
        }

        for (const [name, config] of Object.entries(repos)) {
            const row = document.createElement('tr');
            row.className = "border-b border-oled-border last:border-0 hover:bg-white/5 transition-colors group";
            row.innerHTML = `
                <td class="p-4 font-mono text-brand-light" data-label="Filename">
                    <div class="flex items-center gap-3">
                        <i class="fa-regular fa-file-code opacity-50"></i>
                        <span>${name}</span>
                    </div>
                </td>
                <td class="p-4" data-label="Type">
                    <span class="px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${
                        config.type === 'release' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' : 
                        'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                    }">
                        ${config.type}
                    </span>
                </td>
                <td class="p-4 opacity-70 text-xs" data-label="Source">
                    <div class="flex flex-col gap-1">
                        <span class="font-bold">${config.repo || 'Direct URL'}</span>
                        <span class="font-mono opacity-50 text-[10px] truncate max-w-[150px] sm:max-w-xs">
                            ${config.asset_pattern || config.url}
                        </span>
                    </div>
                </td>
                <td class="p-4 text-right" data-label="Actions">
                    <div class="flex items-center justify-end gap-2 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
                        <button onclick="updateSingleRepo('${name}', this)" class="p-2 text-gray-400 hover:text-brand-light transition-colors" title="Update now">
                            <i class="fa-solid fa-arrows-rotate"></i>
                        </button>
                        <button onclick="editRepo('${name}')" class="p-2 hover:text-brand-light transition-colors" title="Edit">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button onclick="deleteRepo('${name}')" class="p-2 hover:text-red-500 transition-colors" title="Delete">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tableBody.appendChild(row);
        }
    } catch (error) {
        console.error(error);
        if (loading) loading.innerText = "Failed to load repositories";
        Toast.show("Failed to load repositories", "error");
    }
}

async function updateSingleRepo(name, btn) {
    const icon = btn.querySelector('i');
    const originalClass = icon.className;
    
    icon.className = 'fa-solid fa-spinner fa-spin';
    btn.disabled = true;
    Toast.show(`Updating ${name}...`, 'info');

    try {
        const res = await fetch('/update_repos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ targets: [name] })
        });
        const data = await res.json();
        
        if (data.success && data.updated.length > 0) {
            Toast.show(`Successfully updated ${name}`, "success");
        } else if (data.errors && data.errors.length > 0) {
            Toast.show(`Error updating ${name}: ${data.errors[0]}`, "error");
        } else {
            Toast.show(`${name} is already up to date`, "info");
        }
    } catch (e) {
        Toast.show("Update failed: " + e.message, "error");
    } finally {
        icon.className = originalClass;
        btn.disabled = false;
    }
}

async function saveRepo() {
    const oldName = document.getElementById('old-name-ref').value;
    const name = document.getElementById('repo-name').value.trim();
    const type = document.getElementById('repo-type').value;

    if (!name) return Toast.show("Filename is required", "warning");
    if (!name.endsWith('.bin') && !name.endsWith('.elf') && !name.endsWith('.js') && !name.endsWith('.dat')) {
        return Toast.show("Filename must end with .bin, .elf, .js, or .dat", "warning");
    }

    let payload = { name, old_name: oldName, type, save_path: `payloads/${name}` };

    if (type === 'direct') {
        payload.url = document.getElementById('repo-url').value.trim();
        if (!payload.url) return Toast.show("URL is required", "warning");
    } else {
        payload.repo = document.getElementById('repo-github').value.trim();
        payload.asset_pattern = document.getElementById('repo-pattern').value.trim();
        if (!payload.repo || !payload.asset_pattern) return Toast.show("GitHub Repo and Pattern are required", "warning");
    }

    const saveBtn = document.querySelector('button[onclick="saveRepo()"]');
    const originalText = saveBtn.innerText;
    saveBtn.innerText = "Saving...";
    saveBtn.disabled = true;

    try {
        const res = await fetch('/api/repos/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);

        Toast.show(oldName ? "Repository updated" : "Repository added", "success");
        closeModal();
        loadRepos();
    } catch(e) {
        Toast.show(e.message, "error");
    } finally {
        saveBtn.innerText = originalText;
        saveBtn.disabled = false;
    }
}

async function deleteRepo(name) {
    if(!confirm(`Delete configuration for ${name}?`)) return;
    try {
        const response = await fetch('/api/repos/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name})
        });
        if (response.ok) {
            Toast.show(`${name} removed`, "success");
            loadRepos();
        } else {
            Toast.show("Failed to delete", "error");
        }
    } catch(e) {
        Toast.show("Connection error", "error");
    }
}

async function editRepo(name) {
    try {
        const response = await fetch('/api/repos/list');
        const repos = await response.json();
        const config = repos[name];
        
        if (config) {
            document.getElementById('old-name-ref').value = name;
            document.getElementById('repo-name').value = name;
            document.getElementById('repo-type').value = config.type;
            toggleFields();
            if (config.type === 'direct') {
                document.getElementById('repo-url').value = config.url || '';
            } else {
                document.getElementById('repo-github').value = config.repo || '';
                document.getElementById('repo-pattern').value = config.asset_pattern || '';
            }
            document.getElementById('modalTitle').innerText = "Edit Repository";
            openModal();
        }
    } catch (e) {
        Toast.show("Error loading repo details", "error");
    }
}

document.addEventListener('DOMContentLoaded', loadRepos);
