const articleFollowBtn = document.querySelector('#articleFollowBtn')
const articleLikeBtn = document.querySelector('#articleLikeBtn')


const articleFollowFunc = function(e) {
	const data = {"user_id": e.currentTarget.getAttribute("data-id")}
	const elem = e.currentTarget
	fetch("/web/follow",
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
	  if (elem.classList.contains('article-primary')){
		elem.textContent = "Takip Et"
		elem.classList.remove("article-primary") 
	  }else{
		elem.textContent = "Takiptesin"
		elem.classList.add("article-primary") 
	  }
	  const dataMsg = data["message"]
	  Snackbar.show({text:dataMsg, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
	})
	.catch(function(res){ console.log(res) }) 
  }

  if (typeof(articleFollowBtn) != 'undefined' && articleFollowBtn != null)
{
	articleFollowBtn.addEventListener("click",articleFollowFunc)
}

const deleteArticle = function(slug) {
	Swal.fire({
		title: 'Makaleyi silmek istediğine emin misin?',
		text: "Bu hamleden sonra makaleyi geri getiremezsin!",
		icon: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#3085d6',
		cancelButtonColor: '#d33',
		confirmButtonText: 'Evet, eminim!',
		cancelButtonText: 'İptal!'
	  }).then((result) => {
		if (result.isConfirmed) {
		  Swal.fire(
			'Deleted!',
			'Your file has been deleted.',
			'success'
		  )
		  window.location = "/delete/" + slug
		}
	  })
}

articleLikeBtn.addEventListener("click",function(e) {
	const data = {"activity_id": e.currentTarget.getAttribute("data-id")}
	const elem = e.currentTarget
	fetch("/web/api/like?type=article",
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
	  if (elem.classList.contains('liked')){
		// elem.textContent = "Değer Ver"
		elem.classList.remove("liked") 
		elem.querySelector(".btn-text").textContent = "DEĞER VER"
	  }else{
		elem.querySelector(".btn-text").textContent  = "DEĞER VERDİN"
		elem.classList.add("liked") 
	  }
	  const dataMsg = data["message"]
	  Snackbar.show({text:dataMsg, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
	})
	.catch(function(res){ console.log(res) 
		Snackbar.show({text:dataMsg, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
	}) 
})