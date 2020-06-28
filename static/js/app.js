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

function votePost(postID, voteType) {
    var token = Cookies.get('csrftoken');
    alert(token);
    $.ajax({
        data: form.serialize(),
        type: form.attr('method'),
        url:  form.attr('action'),
        success: function(response) {
            if (response.success) {
                
            } else {
                $('#loginError').html(errorMessage(response.message));
            }

            // Update post vote count with +1. Even though someone else could
            // have also upvoted in the same time, if we fetch the latest count
            // from the DB it may not "seem" like our vote was successfully
            // applied
        }
    });
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

$('#sortByVotes').on('click', function(event) {
    alert("sort by votes clicked");
    event.preventDefault();
});

$('#sortByNew').on('click', function(event) {
    alert("sort by new clicked");
    event.preventDefault();
});

$('#sortByOld').on('click', function(event) {
    alert("sort by old clicked");
    event.preventDefault();
});

$('.upVote').on('click', function(event) {
    var postID = $(this).data('post');
    votePost(postID, 1);
    event.preventDefault();
});

$('.downVote').on('click', function(event) {
    var postID = $(this).data('post');
    votePost(postID, 2);
    event.preventDefault();
});

$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
});