function errorMessage(msg) {
    return `<div class="alert alert-danger alert-dismissible fade show" role="alert">${msg}</div>`;
}

$('.commentPoster').on('click', function(event) {
    // Show mini comment poster textbox
    alert("comment poster clicked");
    event.preventDefault();
});

$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
});