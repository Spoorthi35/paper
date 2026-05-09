/**
 * SmartQGen – Main JavaScript
 * Client-side form validation, sidebar toggle, AJAX helpers
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Sidebar Toggle (Mobile) ──
    const sidebar = document.getElementById('sidebar');
    const sidebarOpen = document.getElementById('sidebarOpen');
    const sidebarClose = document.getElementById('sidebarClose');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    if (sidebarOpen) {
        sidebarOpen.addEventListener('click', () => {
            sidebar.classList.add('open');
            sidebarOverlay.classList.add('active');
        });
    }

    [sidebarClose, sidebarOverlay].forEach(el => {
        if (el) {
            el.addEventListener('click', () => {
                sidebar.classList.remove('open');
                sidebarOverlay.classList.remove('active');
            });
        }
    });

    // ── Password Toggle ──
    const togglePassword = document.getElementById('togglePassword');
    const passwordField = document.getElementById('password');
    if (togglePassword && passwordField) {
        togglePassword.addEventListener('click', () => {
            const type = passwordField.type === 'password' ? 'text' : 'password';
            passwordField.type = type;
            togglePassword.querySelector('i').classList.toggle('bi-eye');
            togglePassword.querySelector('i').classList.toggle('bi-eye-slash');
        });
    }

    // ── Form Validation (Bootstrap style) ──
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // ── Delete Confirmation ──
    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!confirm('Are you sure you want to delete this question? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // ── Paper Generation: Subject → Module AJAX ──
    const subjectSelect = document.getElementById('subject_id');
    const moduleSelector = document.getElementById('moduleSelector');
    const moduleHint = document.getElementById('moduleHint');

    if (subjectSelect && moduleSelector) {
        subjectSelect.addEventListener('change', function () {
            const subjectId = this.value;

            // Hide all module options first
            for (let i = 1; i <= 6; i++) {
                const opt = document.getElementById('moduleOption' + i);
                if (opt) {
                    opt.style.display = 'none';
                    opt.querySelector('input').checked = false;
                }
            }

            if (!subjectId) {
                if (moduleHint) moduleHint.style.display = 'block';
                return;
            }

            // Fetch available modules via AJAX
            fetch('/papers/api/subject-modules/' + subjectId)
                .then(r => r.json())
                .then(modules => {
                    if (moduleHint) moduleHint.style.display = modules.length ? 'none' : 'block';

                    modules.forEach(m => {
                        const opt = document.getElementById('moduleOption' + m);
                        if (opt) {
                            opt.style.display = '';
                            opt.querySelector('input').checked = true;
                        }
                    });
                })
                .catch(() => {
                    if (moduleHint) {
                        moduleHint.textContent = 'Error loading modules. Please try again.';
                        moduleHint.style.display = 'block';
                    }
                });
        });

        // Trigger on page load if subject is pre-selected
        if (subjectSelect.value) {
            subjectSelect.dispatchEvent(new Event('change'));
        }
    }

    // ── Difficulty Distribution Live Total ──
    const easyPct = document.getElementById('easy_pct');
    const mediumPct = document.getElementById('medium_pct');
    const hardPct = document.getElementById('hard_pct');
    const totalPctEl = document.getElementById('totalPct');
    const pctStatus = document.getElementById('pctStatus');

    function updatePctTotal() {
        if (!easyPct || !mediumPct || !hardPct || !totalPctEl) return;
        const total = (parseInt(easyPct.value) || 0) + (parseInt(mediumPct.value) || 0) + (parseInt(hardPct.value) || 0);
        totalPctEl.textContent = total;
        if (pctStatus) {
            if (total === 100) {
                pctStatus.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
            } else {
                pctStatus.innerHTML = '<i class="bi bi-exclamation-triangle-fill text-danger"></i> Must equal 100%';
            }
        }
    }

    [easyPct, mediumPct, hardPct].forEach(el => {
        if (el) el.addEventListener('input', updatePctTotal);
    });
    updatePctTotal();

    // ── Auto-dismiss flash messages after 5s ──
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            const btn = alert.querySelector('.btn-close');
            if (btn) btn.click();
        }, 5000);
    });
});
