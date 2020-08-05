function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

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
    $.post({
        data: {
            pid: postID,
            type: voteType
        },
        url:  '/questions/vote/',
        success: function(response) {
            // Update post vote count with +1. Even though someone else could
            // have also upvoted in the same time, if we fetch the latest count
            // from the DB it may not "seem" like our vote was successfully
            // applied
            if (response.success) {
                var votes = parseInt($(`#postVotes${postID}`).html());
                $(`#postVotes${postID}`).html((votes + response.type).toString());
            } else {
                alert('error');
            }
        }
    });
}

function acceptAnswer(questionID, postID) {
    $.post({
        data: {
            pid: postID,
            qid: questionID
        },
        url:  '/questions/accept/',
        success: function(response) {
            // Update post vote count with +1. Even though someone else could
            // have also upvoted in the same time, if we fetch the latest count
            // from the DB it may not "seem" like our vote was successfully
            // applied
            if (response.success) {
                window.location.reload();
            } else {
                alert('error');
            }
        }
    });
}

function fetchPosts(questionID, order) {
    $.post({
        data: {
            pid: postID,
            qid: questionID
        },
        url:  '/questions/posts/',
        success: function(response) {
            // Update post vote count with +1. Even though someone else could
            // have also upvoted in the same time, if we fetch the latest count
            // from the DB it may not "seem" like our vote was successfully
            // applied
            if (response.success) {
                window.location.reload();
            } else {
                alert('error');
            }
        }
    });
}

$('.commentPoster').on('click', function(event) {
    // Show mini comment poster textbox
    var target = $(this).data('target');
    var postid = $(this).data('postid');
    var poster = `<div class="text-right"><input type="hidden" name="pid" value="${postid}"><textarea class="form-control" name="comment" placeholder="Enter Comment" rows="3"></textarea><input type="submit" value="Post Comment" class="btn-sm btn btn-primary mt-2"></div>`;

    $(`#${target}`).html(poster);
    event.preventDefault();
});

$('.load-more').on('click', function(event) {
    alert("load more clicked");
    event.preventDefault();
});

const POST_ORDER = {
    OLD: 1,
    NEW: 2,
    VOTES: 3
};

$('#sortByVotes').on('click', function(event) {
    fetchPosts($(this).data('qid'), POST_ORDER.VOTES);
    event.preventDefault();
});

$('#sortByNew').on('click', function(event) {
    fetchPosts($(this).data('qid'), POST_ORDER.NEW);
    event.preventDefault();
});

$('#sortByOld').on('click', function(event) {
    fetchPosts($(this).data('qid'), POST_ORDER.OLD);
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

$('.accept').on('click', function(event) {
    var postID = $(this).data('post');
    var questionID = $(this).data('question');
    acceptAnswer(questionID, postID);
    event.preventDefault();
});

$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
    var csrftoken = Cookies.get('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});