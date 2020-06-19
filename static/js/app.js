function errorMessage(msg) {
    return `<div class="alert alert-danger alert-dismissible fade show" role="alert">${msg}</div>`;
}

$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
});