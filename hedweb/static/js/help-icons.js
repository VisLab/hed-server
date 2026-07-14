/**
 * help-icons.js
 *
 * Fetches ui_help.json and injects Bootstrap popover help icons next to form
 * labels. The JSON URL is provided by layout.html via window.hedHelpJsonUrl.
 *
 * JSON structure (v1.1): { "sections": { "actions": {…}, "inputs": {…},
 *   "schema": {…}, "options": {…} } }
 * Each entry may have "html": true to allow HTML markup in "text".
 * The "process_actions" entry may have "action_details": { actionValue: text }
 * for context-sensitive help that updates as the Action dropdown changes.
 *
 * Depends on Bootstrap 5 being loaded globally (bootstrap.Popover).
 */
(function () {
    'use strict';

    const helpJsonUrl = window.hedHelpJsonUrl;
    if (!helpJsonUrl) return;

    async function init() {
        let helpData;
        try {
            const resp = await fetch(helpJsonUrl);
            if (!resp.ok) return;
            helpData = await resp.json();
        } catch (e) {
            return; // fail silently — forms work normally without help icons
        }

        // Flatten all sections into a single map of id -> info
        const sections = helpData.sections || {};
        const elements = {};
        for (const sectionEntries of Object.values(sections)) {
            Object.assign(elements, sectionEntries);
        }

        for (const [id, info] of Object.entries(elements)) {
            const label = document.querySelector(`label[for="${id}"]`);
            if (!label) continue;

            const btn = buildHelpButton(id, info);

            // For labels that wrap radio buttons, stop the click from activating
            // the radio button when the user clicks the ? button.
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
            });

            label.appendChild(btn);

            const useHtml = !!(info.action_details || info.html);

            // For the action dropdown, seed the popover with the currently-selected
            // action's detail text so "validate" (the default) is shown immediately.
            const actionSelect = id === 'process_actions'
                ? document.getElementById('process_actions')
                : null;
            const initialDetail = actionSelect
                ? (info.action_details || {})[actionSelect.value]
                : null;

            const popover = new bootstrap.Popover(btn, {
                title: info.title || '',
                content: buildContent(info, initialDetail),
                trigger: 'click focus',
                placement: info.placement || 'auto',
                html: useHtml,
            });

            if (id === 'process_actions' && info.action_details && actionSelect) {
                // Refresh content each time the popover opens so it always reflects
                // the current action selection (handles the default "validate" case
                // as well as subsequent changes without needing a separate listener).
                btn.addEventListener('show.bs.popover', function () {
                    const detail = info.action_details[actionSelect.value];
                    popover.setContent({
                        '.popover-header': info.title || '',
                        '.popover-body': buildContent(info, detail),
                    });
                });

                // Also update while popover is already open (live change).
                actionSelect.addEventListener('change', function () {
                    const instance = bootstrap.Popover.getInstance(btn);
                    if (instance && document.querySelector(`[data-bs-popper]`) !== null) {
                        const detail = info.action_details[this.value];
                        instance.setContent({
                            '.popover-header': info.title || '',
                            '.popover-body': buildContent(info, detail),
                        });
                    }
                });
            }
        }

        // Close open popovers when clicking outside any help button.
        document.addEventListener('click', function (e) {
            if (!e.target.classList.contains('btn-help')) {
                document.querySelectorAll('.btn-help').forEach(function (b) {
                    const pop = bootstrap.Popover.getInstance(b);
                    if (pop) pop.hide();
                });
            }
        });
    }

    function buildHelpButton(id, info) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn-help';
        btn.setAttribute('aria-label', 'Help for ' + (info.title || id));
        btn.textContent = '?';
        return btn;
    }

    /**
     * Build popover body content for an element.
     * - If the entry has action_details, wrap in HTML with an optional action section.
     * - If the entry has html:true, pass text through as-is.
     * - Otherwise return plain text (Bootstrap will display it safely).
     */
    function buildContent(info, actionDetail) {
        if (info.action_details) {
            let html = '<p>' + (info.html ? info.text : escapeHtml(info.text || '')) + '</p>';
            if (actionDetail) {
                html += '<hr class="my-1"><p class="mb-0">'
                    + (info.html ? actionDetail : escapeHtml(actionDetail)) + '</p>';
            }
            return html;
        }
        // For html:true entries, text is already HTML markup.
        return info.text || '';
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());

