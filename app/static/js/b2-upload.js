/**
 * Backblaze B2 Direct Browser Upload Helper
 * Handles direct streaming of media/document files from admin browser to Backblaze B2,
 * bypassing the Render server to prevent memory, timeout, and bandwidth issues.
 */

document.addEventListener('DOMContentLoaded', () => {
    initB2DirectUploads();
});

function initB2DirectUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"][data-b2-upload="true"]');
    fileInputs.forEach(input => {
        setupB2Input(input);
    });
}

function setupB2Input(input) {
    if (input.dataset.b2Initialized) return;
    input.dataset.b2Initialized = "true";

    const parentForm = input.closest('form');
    const folder = input.dataset.folder || 'materials';

    // Create UI container for upload progress
    let progressContainer = input.parentElement.querySelector('.b2-upload-progress');
    if (!progressContainer) {
        progressContainer = document.createElement('div');
        progressContainer.className = 'b2-upload-progress mt-2 d-none';
        progressContainer.innerHTML = `
            <div class="d-flex align-items-center justify-content-between mb-1">
                <small class="b2-upload-status text-info fw-semibold">Preparing Direct B2 Cloud Upload...</small>
                <small class="b2-upload-percent text-muted">0%</small>
            </div>
            <div class="progress" style="height: 8px; border-radius: 4px; background: rgba(255,255,255,0.1);">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-success" role="progressbar" style="width: 0%;"></div>
            </div>
        `;
        input.parentElement.appendChild(progressContainer);
    }

    const statusText = progressContainer.querySelector('.b2-upload-status');
    const percentText = progressContainer.querySelector('.b2-upload-percent');
    const progressBar = progressContainer.querySelector('.progress-bar');

    input.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Reset progress UI
        progressContainer.classList.remove('d-none');
        progressBar.style.width = '0%';
        progressBar.classList.add('progress-bar-animated', 'progress-bar-striped', 'bg-success');
        progressBar.classList.remove('bg-danger');
        statusText.textContent = 'Requesting presigned upload URL from B2...';
        statusText.className = 'b2-upload-status text-info fw-semibold';
        percentText.textContent = '0%';

        // Disable form submit button during upload
        let submitBtn = parentForm ? parentForm.querySelector('button[type="submit"], input[type="submit"]') : null;
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.dataset.origText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Uploading to B2 Cloud...';
        }

        let targetFolder = input.dataset.folder || 'materials';
        const cwTypeSelect = parentForm ? parentForm.querySelector('[name="courseware_type"]') : null;
        if (file.name.toLowerCase().endsWith('.zip') || (cwTypeSelect && cwTypeSelect.value === 'SCORM')) {
            targetFolder = 'scorm';
        }

        try {
            const fileContentType = file.type || 'application/octet-stream';

            // Step 1: Request Presigned Upload URL from backend
            const res = await fetch('/api/b2/presigned-upload-url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filename: file.name,
                    folder: targetFolder,
                    content_type: fileContentType
                })
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.error || 'Failed to generate B2 upload URL');
            }

            const data = await res.json();
            const uploadUrl = data.upload_url;
            const uniqueFilename = data.filename;
            const key = data.key;

            // Step 2: Perform direct XHR PUT upload to Backblaze B2
            statusText.textContent = `Streaming '${file.name}' directly to B2 Cloud...`;
            await new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('PUT', uploadUrl, true);
                xhr.setRequestHeader('Content-Type', fileContentType);

                xhr.upload.onprogress = (evt) => {
                    if (evt.lengthComputable) {
                        const percentComplete = Math.round((evt.loaded / evt.total) * 100);
                        progressBar.style.width = percentComplete + '%';
                        percentText.textContent = percentComplete + '%';
                    }
                };

                xhr.onload = () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve();
                    } else {
                        reject(new Error(`B2 Upload HTTP status ${xhr.status}`));
                    }
                };

                xhr.onerror = () => reject(new Error('Network or CORS error during B2 direct upload'));
                xhr.ontimeout = () => reject(new Error('B2 upload request timed out'));
                xhr.send(file);
            });

            // Step 3: Success! Update UI & inject hidden form inputs
            progressBar.style.width = '100%';
            progressBar.classList.remove('progress-bar-animated', 'progress-bar-striped');
            statusText.textContent = 'Upload complete! Direct B2 Cloud reference created.';
            statusText.className = 'b2-upload-status text-success fw-bold';
            percentText.textContent = '100%';

            // Helper to format file size
            let sizeStr = 'N/A';
            if (file.size < 1024 * 1024) {
                sizeStr = (file.size / 1024).toFixed(1) + ' KB';
            } else {
                sizeStr = (file.size / (1024 * 1024)).toFixed(1) + ' MB';
            }

            // Create or update hidden form inputs
            setHiddenInput(parentForm, 'b2_uploaded_filename', uniqueFilename);
            setHiddenInput(parentForm, 'b2_uploaded_key', key);
            setHiddenInput(parentForm, 'b2_file_size_str', sizeStr);
            setHiddenInput(parentForm, 'b2_file_size_bytes', file.size.toString());

            // For SCORM packages, check if launch file can be auto-detected or defaults to index.html
            if (targetFolder === 'scorm' || file.name.endsWith('.zip')) {
                setHiddenInput(parentForm, 'b2_scorm_launch_href', 'index.html');
            }

            // Temporarily rename/clear the original file input so form submission won't send binary bytes to Render
            input.dataset.originalName = input.name || input.dataset.originalName || 'file';
            input.removeAttribute('name');

            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.dataset.origText || 'Save / Submit';
            }

        } catch (err) {
            console.error('B2 Direct Upload Error:', err);
            progressBar.classList.add('bg-warning');
            progressBar.classList.remove('progress-bar-animated', 'bg-success');
            statusText.textContent = `Direct B2 upload notice: ${err.message}. Standard server fallback active.`;
            statusText.className = 'b2-upload-status text-warning fw-bold';

            // Ensure file input name is restored for standard server form submit fallback
            if (input.dataset.originalName) {
                input.name = input.dataset.originalName;
            }

            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.dataset.origText || 'Save / Submit';
            }
        }
    });
}

function setHiddenInput(form, name, value) {
    if (!form) return;
    let hidden = form.querySelector(`input[type="hidden"][name="${name}"]`);
    if (!hidden) {
        hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = name;
        form.appendChild(hidden);
    }
    hidden.value = value;
}
