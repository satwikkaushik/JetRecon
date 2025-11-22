// script.js - Frontend logic for JetRecon

const API_BASE = 'http://localhost:8000';

// DOM elements
const createTaskSection = document.getElementById('create-task-section');
const createTaskForm = document.getElementById('create-task-form');
const taskDetailsSection = document.getElementById('task-details-section');
const executionPlanSection = document.getElementById('execution-plan-section');
const statusMessage = document.getElementById('status-message');
const createTaskBtn = document.getElementById('create-task-btn');
const prepareBtn = document.getElementById('prepare-btn');
const performReconBtn = document.getElementById('perform-recon-btn');

let currentTaskId = null;

// Default dark theme (no toggle)
function setDefaultTheme() {
    document.documentElement.setAttribute('data-theme', 'dark');
}

// Utility functions
function showElement(element) {
    element.classList.remove('hidden');
}

function hideElement(element) {
    element.classList.add('hidden');
}

// Background pulse animation trigger (used to emphasize big actions)
function triggerBgPulse() {
    const el = document.body;
    if (el.classList.contains('bg-animate')) return;
    el.classList.add('bg-animate');
    function cleanup() {
        el.classList.remove('bg-animate');
        el.removeEventListener('animationend', cleanup);
    }
    el.addEventListener('animationend', cleanup);
}

function setStatusMessage(message, type = 'error') {
    statusMessage.textContent = message;
    statusMessage.className = type;
    setTimeout(() => {
        statusMessage.textContent = '';
        statusMessage.className = '';
    }, 5000);
}

function enableButton(button) {
    button.disabled = false;
    button.innerHTML = button.innerHTML.replace('<div class="loading"></div>', '');
}

function disableButton(button) {
    button.disabled = true;
    button.innerHTML = '<div class="loading"></div>' + button.innerHTML;
}

// Display task details
function displayTaskDetails(task) {
    const taskInfo = document.getElementById('task-info');
    taskInfo.innerHTML = `
        <p><strong><i class="fas fa-id-badge"></i> Task ID:</strong> ${task.job_id}</p>
        <p><strong><i class="fas fa-file"></i> File 1:</strong> ${task.file1}</p>
        <p><strong><i class="fas fa-file"></i> File 2:</strong> ${task.file2}</p>
        <p><strong><i class="fas fa-puzzle-piece"></i> Chunks File 1:</strong> ${task.chunks_file1}</p>
        <p><strong><i class="fas fa-puzzle-piece"></i> Chunks File 2:</strong> ${task.chunks_file2}</p>
        <p><strong><i class="fas fa-weight"></i> Size File 1:</strong> ${task.size_file1} bytes</p>
        <p><strong><i class="fas fa-weight"></i> Size File 2:</strong> ${task.size_file2} bytes</p>
        <p><strong><i class="fas fa-tasks"></i> Status:</strong> <span class="status-${task.status}">${task.status.replace(/_/g, ' ')}</span></p>
    `;
    currentTaskId = task.job_id;
    // collapse header to increase visible space and hide the create panel
    collapseHeader();
    hideElement(createTaskSection);
    showElement(taskDetailsSection);
    showElement(prepareBtn);
}

// Collapse header: hide subheading and reduce header size
function collapseHeader() {
    const header = document.querySelector('header');
    if (!header.classList.contains('collapsed')) {
        header.classList.add('collapsed');
    }
}

// Display execution plan
function displayExecutionPlan(plan) {
    const executionPlanInfo = document.getElementById('execution-plan-info');
    executionPlanInfo.innerHTML = `
        <p><strong><i class="fas fa-id-badge"></i> Task ID:</strong> ${plan.job_id}</p>
        <p><strong><i class="fas fa-boxes"></i> Bucket Count:</strong> ${plan.bucket_count}</p>
        <p><strong><i class="fas fa-expand"></i> Bucket Size:</strong> ${plan.bucket_size}</p>
        <p><strong><i class="fas fa-users-cog"></i> Recon Workers:</strong> ${plan.recon_workers}</p>
        <p><strong><i class="fas fa-users"></i> Read Workers:</strong> ${plan.read_workers}</p>
        <p><strong><i class="fas fa-hashtag"></i> Hash Algorithm:</strong> ${plan.hash_algorithm}</p>
        <h3><i class="fas fa-file"></i> File 1 Plan</h3>
        <p><strong>Path:</strong> ${plan.file1.path}</p>
        <p><strong>Size:</strong> ${plan.file1.size} bytes</p>
        <p><strong>Chunks:</strong> ${plan.file1.chunks.length}</p>
        <h3><i class="fas fa-file"></i> File 2 Plan</h3>
        <p><strong>Path:</strong> ${plan.file2.path}</p>
        <p><strong>Size:</strong> ${plan.file2.size} bytes</p>
        <p><strong>Chunks:</strong> ${plan.file2.chunks.length}</p>
    `;
    hideElement(taskDetailsSection);
    showElement(executionPlanSection);
    showElement(performReconBtn);
}

// API calls
async function createTask(file1, file2) {
    try {
        const response = await fetch(`${API_BASE}/jobs/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ file1, file2 }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create task');
        }

        const task = await response.json();
        displayTaskDetails(task);
        setStatusMessage('Task created successfully!', 'success');
    } catch (error) {
        setStatusMessage(`Error creating task: ${error.message}`);
    } finally {
        enableButton(createTaskBtn);
    }
}

async function prepareTask(taskId) {
    try {
        const response = await fetch(`${API_BASE}/jobs/${taskId}/prepare`, {
            method: 'POST',
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to prepare task');
        }

        const plan = await response.json();
        displayExecutionPlan(plan);
        setStatusMessage('Task prepared successfully!', 'success');
    } catch (error) {
        setStatusMessage(`Error preparing task: ${error.message}`);
    } finally {
        enableButton(prepareBtn);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', setDefaultTheme);

createTaskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file1 = document.getElementById('file1').value.trim();
    const file2 = document.getElementById('file2').value.trim();

    if (!file1 || !file2) {
        setStatusMessage('Please enter both file paths.');
        return;
    }

    disableButton(createTaskBtn);
    triggerBgPulse();
    await createTask(file1, file2);
});

prepareBtn.addEventListener('click', async () => {
    if (!currentTaskId) {
        setStatusMessage('No task selected.');
        return;
    }

    triggerBgPulse();
    disableButton(prepareBtn);
    await prepareTask(currentTaskId);
});

performReconBtn.addEventListener('click', () => {
    // Placeholder for future implementation
    setStatusMessage('Perform Recon functionality not yet implemented.', 'error');
});