/**
 * upload.js
 * Handles image selection (click + drag-and-drop),
 * preview rendering, and API submission.
 */

'use strict';

// ── DOM refs ──────────────────────────────────────────────────────────────────
const dropZone     = document.getElementById('dropZone');
const fileInput    = document.getElementById('fileInput');
const browseLink   = document.getElementById('browseLink');
const previewBox   = document.getElementById('previewBox');
const previewImg   = document.getElementById('previewImg');
const previewMeta  = document.getElementById('previewMeta');
const predictBtn   = document.getElementById('predictBtn');
const changeBtn    = document.getElementById('changeBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const errorAlert   = document.getElementById('errorAlert');
const errorMsg     = document.getElementById('errorMsg');

const API_BASE     = '';          // same origin; FastAPI serves the page
const MAX_SIZE_MB  = 10;

let selectedFile   = null;

// ── Utilities ─────────────────────────────────────────────────────────────────

function showError(msg) {
  errorMsg.textContent = msg;
  errorAlert.style.display = 'flex';
  errorAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
  errorAlert.style.display = 'none';
}

function formatBytes(bytes) {
  if (bytes < 1024)       return bytes + ' B';
  if (bytes < 1024 ** 2)  return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1024 ** 2).toFixed(1) + ' MB';
}

function setLoading(state) {
  loadingOverlay.classList.toggle('show', state);
  predictBtn.disabled = state;
}

// ── File Selection ────────────────────────────────────────────────────────────

function handleFile(file) {
  hideError();

  // Validate type
  const allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
  if (!allowed.includes(file.type)) {
    showError(`Unsupported file type: ${file.type}. Please upload JPEG or PNG.`);
    return;
  }

  // Validate size
  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    showError(`File too large (${formatBytes(file.size)}). Maximum allowed: ${MAX_SIZE_MB} MB.`);
    return;
  }

  selectedFile = file;

  // Show preview
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    sessionStorage.setItem('skinImageData', e.target.result);
    previewMeta.textContent = `${file.name}  ·  ${formatBytes(file.size)}`;
    previewBox.classList.add('show');
    dropZone.style.display = 'none';
  };
  reader.readAsDataURL(file);
}

// ── Event Listeners ──────────────────────────────────────────────────────────

// Click on drop zone or browse link
dropZone.addEventListener('click', () => fileInput.click());
browseLink.addEventListener('click', (e) => { e.stopPropagation(); fileInput.click(); });
dropZone.addEventListener('keypress', (e) => { if (e.key === 'Enter' || e.key === ' ') fileInput.click(); });

// Native file input
fileInput.addEventListener('change', () => {
  if (fileInput.files.length) handleFile(fileInput.files[0]);
});

// Drag & Drop
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});

// Change / reset
changeBtn.addEventListener('click', () => {
  selectedFile = null;
  fileInput.value = '';
  previewBox.classList.remove('show');
  dropZone.style.display = '';
  hideError();
});

// ── Predict ───────────────────────────────────────────────────────────────────

predictBtn.addEventListener('click', async () => {
  if (!selectedFile) {
    showError('Please select an image first.');
    return;
  }

  hideError();
  setLoading(true);

  try {
    const formData = new FormData();
    formData.append('file', selectedFile);

    const response = await fetch(`${API_BASE}/predict`, {
      method:  'POST',
      body:    formData,
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${response.status})`);
    }

    const result = await response.json();

    // Persist result for result.html
    sessionStorage.setItem('skinResult', JSON.stringify(result));

    // Navigate to results page
    window.location.href = '/result';

  } catch (err) {
    showError(`Analysis failed: ${err.message}`);
  } finally {
    setLoading(false);
  }
});
