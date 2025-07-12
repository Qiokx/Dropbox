// JavaScript for file manager UI
let selectedItem = null;
let longPressTimer = null;
let touchStartTime = 0;

document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupDragAndDrop();
});

function setupEventListeners() {
    const items = document.querySelectorAll('.item');
    items.forEach(item => {
        item.addEventListener('click', function(e) {
            if (selectedItem) {
                clearSelection();
                return;
            }
            if (item.dataset.type === 'folder') {
                window.location.href = '/browse/' + item.dataset.path;
            } else {
                openFile(item.dataset.path);
            }
        });
        item.addEventListener('touchstart', function(e) {
            touchStartTime = Date.now();
            longPressTimer = setTimeout(() => {
                selectItem(item);
            }, 500);
        });
        item.addEventListener('touchend', function(e) {
            clearTimeout(longPressTimer);
            if (Date.now() - touchStartTime < 500) {
                if (selectedItem) {
                    clearSelection();
                }
            }
        });
        item.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            selectItem(item);
        });
    });
}

function setupDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    dropZone.addEventListener('drop', handleDrop, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}
function highlight() {
    document.getElementById('dropZone').classList.add('drag-over');
}
function unhighlight() {
    document.getElementById('dropZone').classList.remove('drag-over');
}
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}
function handleFiles(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    uploadFiles(formData);
}
function uploadFiles(formData) {
    const progressBar = document.getElementById('progressBar');
    const progressFill = document.getElementById('progressFill');
    progressBar.style.display = 'block';
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        progressBar.style.display = 'none';
        if (data.success) {
            location.reload();
        } else {
            alert('Upload failed: ' + data.message);
        }
    })
    .catch(error => {
        progressBar.style.display = 'none';
        alert('Upload failed: ' + error);
    });
}
function selectItem(item) {
    selectedItem = item;
    item.classList.add('selected');
    document.getElementById('bottomActions').classList.add('show');
}
function clearSelection() {
    if (selectedItem) {
        selectedItem.classList.remove('selected');
        selectedItem = null;
    }
    document.getElementById('bottomActions').classList.remove('show');
}
function openFile(path) {
    window.open('/files/' + path, '_blank');
}
function shareItem() {
    if (!selectedItem) return;
    const path = selectedItem.dataset.path;
    const url = window.location.origin + '/files/' + path;
    if (navigator.share) {
        navigator.share({
            title: selectedItem.dataset.name,
            url: url
        });
    } else {
        navigator.clipboard.writeText(url).then(() => {
            alert('Link copied to clipboard');
        });
    }
    clearSelection();
}
function renameItem() {
    if (!selectedItem) return;
    const currentName = selectedItem.dataset.name;
    const newName = prompt('Enter new name:', currentName);
    if (newName && newName !== currentName) {
        fetch('/api/rename', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                oldPath: selectedItem.dataset.path,
                newName: newName
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Rename failed: ' + data.message);
            }
        });
    }
    clearSelection();
}
function moveItem() {
    alert('Move functionality coming soon');
    clearSelection();
}
function copyItem() {
    alert('Copy functionality coming soon');
    clearSelection();
}
function deleteItem() {
    if (!selectedItem) return;
    if (confirm('Are you sure you want to delete this item?')) {
        fetch('/api/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                path: selectedItem.dataset.path
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Delete failed: ' + data.message);
            }
        });
    }
    clearSelection();
}
function closeModal() {
    document.getElementById('modal').classList.remove('show');
}
document.addEventListener('click', function(e) {
    if (!e.target.closest('.item') && !e.target.closest('.bottom-actions')) {
        clearSelection();
    }
});
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        clearSelection();
        closeModal();
    }
});
