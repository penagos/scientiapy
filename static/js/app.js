function errorMessage(msg) {
    return `<div class="alert alert-danger alert-dismissible fade show" role="alert">${msg}</div>`;
}

// Called on question view if a new post/comment was made (or edited)
function handlePostFlash() {
    if(window.location.hash) {
        var hash = window.location.hash.substring(1);
        var identifier = new RegExp('^[pc]+[0-9]+$');
        if (identifier.test(hash)) {
            console.log("flashing");
            $(`#${hash}`).toggleClass("postFlash");
            setTimeout(function() {
                console.log("out");
                $(`#${hash}`).toggleClass("postFlash");
                $(`#${hash}`).toggleClass("postFlashHide");
            }, 1500);
        }
    }
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