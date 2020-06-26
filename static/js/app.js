function errorMessage(msg) {
    return `<div class="alert alert-danger alert-dismissible fade show" role="alert">${msg}</div>`;
}

$('.commentPoster').on('click', function(event) {
    // Show mini comment poster textbox
    var target = $(this).data('target');
    var postid = $(this).data('postid');
    var poster = `<input type="hidden" name="pid" value="${postid}"><input type="text" class="form-control" name="comment" placeholder="Comment">`;

    $(`#${target}`).html(poster);
    event.preventDefault();
});

$('.load-more').on('click', function(event) {
    alert("load more clicked");
    event.preventDefault();
});

$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
});