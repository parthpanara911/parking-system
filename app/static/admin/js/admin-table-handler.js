$(document).ready(function () {
    const $table = $('#dataTable');
    const deleteUrlBase = $table.data('url');
    const searchInput = $($table.data('search'));
    const successMessage = $table.data('success-message');

    let deleteId = null;
    let targetRow = null;
    const dataTable = $table.DataTable();

    // Search
    searchInput.on('keyup', function () {
        dataTable.search(this.value).draw();
    });

    // Delete modal open
    $table.on('click', '.delete-btn', function () {
        deleteId = $(this).data('id');
        targetRow = $(this).closest('tr');
        $('#confirmDeleteModal').modal('show');
    });

    // Confirm delete
    $('#confirmDeleteBtn').on('click', function () {
        if (!deleteId) return;

        $.ajax({
            url: deleteUrlBase + deleteId,
            type: 'DELETE',
            headers: {
                'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
            },
            success: function () {
                $('#confirmDeleteModal').modal('hide');
                dataTable.row(targetRow).remove().draw(false);
                showMessage(successMessage, 'success');
            },
            error: function (xhr) {
                $('#confirmDeleteModal').modal('hide');
                showMessage('Error: ' + (xhr.responseJSON?.message || 'Unexpected error'), 'danger');
            }
        });
    });

    // Alert helper
    function showMessage(message, type) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show mt-3" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`;
        $('#alertArea').html(alertHtml);

        setTimeout(() => {
            $('.alert').alert('close');
        }, 3000);
    }
});

// collapse sidebar state logic
document.addEventListener('DOMContentLoaded', function () {
    function handleSidebarCollapse(toggleSelector) {
        const toggleLinks = document.querySelectorAll(toggleSelector);

        toggleLinks.forEach(link => {
            const targetId = link.getAttribute('href')?.replace('#', '');
            if (!targetId) return;

            const collapseEl = document.getElementById(targetId);
            const storageKey = 'sidebar-collapse-' + targetId;

            // Restore collapse state only if current URL matches any submenu item
            const submenuLinks = collapseEl?.querySelectorAll('a.nav-link') || [];
            const currentPath = window.location.pathname;

            submenuLinks.forEach(sublink => {
                if (sublink.getAttribute('href') === currentPath) {
                    const bsCollapse = new bootstrap.Collapse(collapseEl, { toggle: false });
                    bsCollapse.show();
                }
            });

            link.addEventListener('click', function () {
                const isExpanded = collapseEl.classList.contains('show');
                localStorage.setItem(storageKey, isExpanded ? 'collapsed' : 'expanded');
            });
        });
    }

    handleSidebarCollapse('.nav-link[data-bs-toggle="collapse"]');
});

