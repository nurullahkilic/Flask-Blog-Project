const articleComment = document.getElementById("articleComment")
const commentList = document.querySelector(".comment-list")
const commentInput = document.getElementById("commentInput")

articleComment.addEventListener("submit",function(e) {
    e.preventDefault()
    const commentContent = commentInput.value
    const articleId = e.currentTarget.getAttribute("data-article-id")
    const typeId = e.currentTarget.getAttribute("data-type-id")

    const data = {
        "article_id": articleId,
        "type_id": typeId,
        "content": commentContent,
    }
    fetch("/web/api/comment?action=add",
    {
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        "X-CSRFToken": csrf_token
        },
        method: "POST",
        body: JSON.stringify(data)
    })
    .then(function(res){ return res.json()})
    .then(function(data){
        const commentInner = document.createElement("li")
        commentInner.className = "comment-inner"
        commentInner.innerHTML = `
            <img src="${data["user_img"]}" alt="" />
            <div class="comment-data">
                <h4>
                    <a href="/@${data["username"]}" class="user-fullname">${data["fullname"]}</a> · demin
                </h4>
                <div class="comment-msg">
                    ${commentContent}
                </div>
            </div>`
        commentList.insertBefore(commentInner, commentList.children[0])
        commentInput.value = ""
        const dataMsg = data["message"]
        Snackbar.show({text:dataMsg, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
    })
    .catch(function(res){ 
        console.log(res)
        Snackbar.show({text:"Böyle olsun istemezdik ama bir hata oldu sanki!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
        // Snackbar.show({text:res, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
    })    
})

const removeComment = document.getElementsByClassName("bx-trash-alt");
for (var i=0; removeComment.length > i; i++){
    removeComment[i].addEventListener("click",function(e) {
        const deletedComment = e.currentTarget.parentElement
        const commentId = e.currentTarget.getAttribute("data-id")
        const articleId = e.currentTarget.getAttribute("data-article-id")
        const data = {
            "comment_id": commentId,
            "article_id": articleId,
        }
        Swal.fire({
            title: 'Yorumu kaldırmak istediğine emin misin?',
            text: "Bütün sorumluluklar sana ait valla!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Evet, sil gitsin!',
            cancelButtonText: 'Vazgeçtim!'
          }).then((result) => {
            if (result.isConfirmed) {
                fetch("/web/api/comment?action=remove",
                {
                    headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    "X-CSRFToken": csrf_token
                    },
                    method: "POST",
                    body: JSON.stringify(data)
                })
                .then(function(res){ return res.json()})
                .then(function(data){
                    const dataMsg = data["message"]
                    deletedComment.remove()
                    Snackbar.show({text:dataMsg, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
                })
                .catch(function(res){ 
                    console.log(res)
                    Snackbar.show({text:"Böyle olsun istemezdik ama bir hata oldu sanki!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
                })   
            }
        })

 
    })
}