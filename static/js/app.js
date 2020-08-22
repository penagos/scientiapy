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

    return false;
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

    return false;
}

function fetchPosts(questionID, order) {
    $.post({
        url: `/questions/posts/${questionID}/${order}/`,
        data: {},
        success: function(response) {
            if (response.success) {
                $('#answersContainer').html(response.posts);
            } else {
                alert(response.mesage);
            }
        }
    });

    return false;
}

function commentEdit(postID, id) {
    commentEditor(id, postID);
    return false;
}

function commentDelete(id) {
    if (confirm('Are you sure you want to delete this comment?')) {
        $.post({
            url:  `/questions/deletecomment/${id}/`,
            success: function(response) {
                if (response.success) {
                    window.location.reload();
                } else {
                    alert('error');
                }
            }
        });
    }

    return false;
}

function commentCancel(restore, target) {
    if (restore != '') {
        $(restore).show();
    }

    $(target).hide();
    return false;
}

// Create HTML form on the fly for editing/posting comments
function commentEditor(id, postID) {
    if (id) {
        // Edit comment
        comment = $(`#commentBody${id}`).text().trim();
        commentID = `<input type="hidden" name="cid" value="${id}">`;
        target = `#commentPosterTarget${id}`;

        // Hide original comment
        $(`#commentBody${id}`).hide();
        restore = `#commentBody${id}`;
    } else {
        // New comment
        comment = '';
        commentID = '';
        target = `#commentPoster${postID}`;
        restore = '';
    }

    var posterName = `poster${postID}${id}`;
    var poster = `<div class="text-right"><input type="hidden" name="pid" value="${postID}">${commentID}<textarea id="${posterName}" class="form-control" name="comment" placeholder="Enter Comment" rows="8" autofocus required>${comment}</textarea><a href="#" class="btn btn-sm btn-secondary mt-2 mr-2" tabindex="1" onclick="return commentCancel('${restore}', '${target}');">Cancel</a><input type="submit" value="Post Comment" tabindex="0" class="btn-sm btn btn-primary mt-2"></div>`;
    $(target).html(poster);
    $(target).show();
    $(`#${posterName}`).focus();
}

function postComment(postid) {
    commentEditor(0, postid);
    return false;
}

$('.load-more').on('click', function(event) {
    alert("load more clicked");
    event.preventDefault();
});

const POST_ORDER = {
    OLD: 'old',
    NEW: 'new',
    VOTES: 'votes'
};

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

    $(".nav .nav-link").on("click", function(){
        $(".nav").find(".active").removeClass("active");
        $(this).addClass("active");
     });
});