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

function openModal(editName = null) {
    const modal = document.getElementById('repoModal');
    const title = document.getElementById('modalTitle');
    const oldNameRef = document.getElementById('old-name-ref');

    document.getElementById('repo-name').value = '';
    document.getElementById('repo-url').value = '';
    document.getElementById('repo-github').value = '';
    document.getElementById('repo-pattern').value = '';
    document.getElementById('repo-type').value = 'direct';

    if (editName && currentRepos[editName]) {
        const data = currentRepos[editName];
        title.textContent = "Modify Repository";
        oldNameRef.value = editName;
        document.getElementById('repo-name').value = editName;
        document.getElementById('repo-type').value = data.type;

        if (data.type === 'direct') {
            document.getElementById('repo-url').value = data.url;
        } else {
            document.getElementById('repo-github').value = data.repo;
            document.getElementById('repo-pattern').value = data.asset_pattern;
        }
    } else {
        title.textContent = "Add Repository";
        oldNameRef.value = "";
    }

    toggleFields();
    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('repoModal').classList.add('hidden');
}

async function loadRepos() {
    const res = await fetch('/api/repos/list');
    currentRepos = await res.json();
    
    const tbody = document.getElementById('repoTable');
    if (document.getElementById('loading')) {
        document.getElementById('loading').classList.add('hidden');
    }
    tbody.innerHTML = '';

    for (const [name, config] of Object.entries(currentRepos)) {
        const isDirect = config.type === 'direct';
        const source = isDirect ? 
            `<div class="truncate w-64" title="${config.url}">${config.url}</div>` : 
            `<div><i class="fa-brands fa-github mr-1"></i> ${config.repo} <span class="opacity-50 text-xs ml-1 font-mono">(${config.asset_pattern})</span></div>`;
        
        const tr = document.createElement('tr');
        tr.className = "hover:bg-white/5 transition-colors group";
        tr.innerHTML = `
            <td class="p-4 font-mono text-brand-light font-bold">${name}</td>
            <td class="p-4">
                <span class="px-2 py-1 rounded text-[10px] uppercase font-bold tracking-wide ${isDirect ? 'bg-green-900/30 text-green-400 border border-green-900' : 'bg-purple-900/30 text-purple-400 border border-purple-900'}">
                    ${config.type}
                </span>
            </td>
            <td class="p-4 text-xs opacity-80">${source}</td>
            <td class="p-4 text-right">
                <button onclick="updateSingleRepo('${name}', this)" class="p-2 text-gray-400 hover:text-brand-light transition-colors" title="Update now">
                    <i class="fa-solid fa-arrows-rotate"></i>
                </button>
                <button onclick="openModal('${name}')" class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs font-bold mx-2 transition-colors">
                    <i class="fa-solid fa-pen"></i> Edit
                </button>
                <button onclick="deleteRepo('${name}')" class="p-2 text-gray-500 hover:text-red-500 transition-colors">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    }
}

async function updateSingleRepo(name, btn) {
    const icon = btn.querySelector('i');
    icon.classList.add('fa-spin');
    btn.disabled = true;

    try {
        const res = await fetch('/update_repos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ targets: [name] })
        });
        const data = await res.json();
        
        if (data.success && data.updated.length > 0) {
            alert(`Successfully updated ${name}`);
        } else if (data.errors && data.errors.length > 0) {
            alert(`Error updating ${name}: ${data.errors[0]}`);
        } else {
            alert(`${name} is already up to date.`);
        }
    } catch (e) {
        alert("Update failed: " + e.message);
    } finally {
        icon.classList.remove('fa-spin');
        btn.disabled = false;
    }
}

async function saveRepo() {
    const name = document.getElementById('repo-name').value.trim();
    const type = document.getElementById('repo-type').value;
    const oldName = document.getElementById('old-name-ref').value;

    if(!name) return alert("Filename is required");

    let payload = { 
        name: name, 
        old_name: oldName,
        type: type, 
        save_path: `payloads/${name}` 
    };

    if (type === 'direct') {
        payload.url = document.getElementById('repo-url').value.trim();
        if(!payload.url) return alert("URL is required");
    } else {
        payload.repo = document.getElementById('repo-github').value.trim();
        payload.asset_pattern = document.getElementById('repo-pattern').value.trim();
        if(!payload.repo || !payload.asset_pattern) return alert("Repo and Pattern are required");
    }

    try {
        const res = await fetch('/api/repos/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if(data.error) throw new Error(data.error);

        closeModal();
        loadRepos();
    } catch(e) {
        alert("Error saving: " + e.message);
    }
}

async function deleteRepo(name) {
    if(!confirm(`Delete configuration for ${name}?`)) return;
    await fetch('/api/repos/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
    });
    loadRepos();
}

document.addEventListener('DOMContentLoaded', loadRepos);
