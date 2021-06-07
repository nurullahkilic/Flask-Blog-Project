let editor;
BalloonEditor
			.create( document.querySelector( '#editor' ), {
				mediaEmbed: {previewsInData: true},
				toolbar: {
					items: [
						'heading',
						'bold',
						'underline',
						'italic',
						'blockQuote',
						'|',
						'numberedList',
						'bulletedList',
						'link',
						'mediaEmbed',
						'insertTable',
						'imageInsert',
						'codeBlock',
						'undo',
						'redo',
						'indent',
						'outdent'
					],
					shouldNotGroupWhenFull: true
				},
				language: 'tr',
				image: {
					toolbar: [
						'imageTextAlternative',
						'imageStyle:full',
						'imageStyle:side'
					]
				},
				table: {
					contentToolbar: [
						'tableColumn',
						'tableRow',
						'mergeTableCells'
					]
				},
				licenseKey: '',
				
				
			} )
.then( newEditor => {
    editor = newEditor;
} )
.catch( error => {
    console.error( error );
} );


const articleId = document.querySelector('#articleId')
const title = document.querySelector('#header')
const link = document.querySelector('#linkImg')
const articleImg = document.querySelector('.article-image');

const colorPick = document.createElement("img");
const colorThief = new ColorThief();
let RGB;

link.addEventListener('input',function (e) {
	if (e.target.value !== ""){
		articleImg.style.background = `url('${e.target.value}') no-repeat center center / cover, #181818 `		
		colorPick.crossOrigin = 'Anonymous'
		colorPick.src = e.target.value
		colorPick.addEventListener('load', function() {
			RGB = `${colorThief.getColor(colorPick)[0]},${colorThief.getColor(colorPick)[1]},${colorThief.getColor(colorPick)[2]}`;
		});
	} else {
		articleImg.style.background = "#181818"
	}
	
})

document.getElementsByTagName("form")[0].addEventListener('submit',(e)=>{
	console.log(e.target.getAttribute("data-type"))
	let data;
    e.preventDefault()
	if (title.textContent=="" || title.textContent==null){
		Snackbar.show({text:"Başlık makalenin bel kemiğidir. Lütfen başlık giriniz!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
	}
	else if (link.value=="" || link.value==null){
		Snackbar.show({text:"Görsel linki giriniz!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
	}
	else if (editor.getData()=="" || editor.getData()==null){
		Snackbar.show({text:"Makale alanı boş gözüküyor. Lütfen boşlukları dolduralım!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
	}else {
		if (e.target.getAttribute("data-type")=="add"){
			data = {
				title: title.textContent,
				link: link.value,
				color: RGB || null,
				content: editor.getData()
			} 
		} else if (e.target.getAttribute("data-type")=="update"){
			data = {
				"id": articleId.value,
				"title": title.textContent,
				"link": link.value,
				"color": RGB || null,
				"content": editor.getData()
			} 
		}
			let booleanDeny= true;
			let confirmText ="Yayınla"	
			let alertTitle = 'Makaleyi yayınlamak istiyor musun?' 		
			if(e.target.getAttribute("data-publish")=="false"){
				booleanDeny = false
				confirmText ="Kaydet!"
				alertTitle = "Makaledeki değişiklikleri kaydetmek istiyor musun?"
			}
			if(e.target.getAttribute("data-type")=="update"){
				booleanDeny = false
			}
			Swal.fire({
				title: alertTitle,
				showDenyButton: booleanDeny,
				showCancelButton: true,
				confirmButtonText: confirmText,
				denyButtonText: `Taslak olarak kaydet`,
				cancelButtonText: `İptal`,
			  }).then((result) => {
				if (result.isConfirmed) {
				  fetch("/addarticle?query="+ e.target.getAttribute("data-type"),
				  {
					  headers: {
					  'Accept': 'application/json',
					  'Content-Type': 'application/json',
					  "X-CSRFToken": csrf_token
					  },
					  method: "POST",
					  body: JSON.stringify(data)
				  })
				  .then(function(res){ 
					  return res.json()
				  })
				  .then(function(res){ 
					  console.log(res)
					  Swal.fire({
						position: 'top-end',
						icon: 'success',
						title: res["message"],
						showConfirmButton: false,
						timer: 1500
					  }).then(function() {
						window.location = res["location"];
					});
				  })
				  .catch(function(res){
					   console.log(res) 
					   Swal.fire({
						position: 'top-end',
						icon: 'error',
						title: "Böyle olsun istemezdik ama sunucu tarafında bir hatalar oldu sanki!",
						showConfirmButton: false,
						timer: 2000
					  })
					  })    
				} else if (result.isDenied) {
					fetch("/addarticle?query="+ e.target.getAttribute("data-type")+"&type=draft",
					{
						headers: {
						'Accept': 'application/json',
						'Content-Type': 'application/json',
						"X-CSRFToken": csrf_token
						},
						method: "POST",
						body: JSON.stringify(data)
					})
					.then(function(res){ 
						return res.json()
					})
					.then(function(res){ 
						console.log(res)
						Swal.fire({
						  position: 'top-end',
						  icon: 'success',
						  title: res["message"],
						  showConfirmButton: false,
						  timer: 1500
						}).then(function() {
						  window.location = res["location"];
					  });
					})
					.catch(function(res){
						 console.log(res) 
						 Swal.fire({
						  position: 'top-end',
						  icon: 'error',
						  title: "Böyle olsun istemezdik ama sunucu tarafında bir hatalar oldu sanki!",
						  showConfirmButton: false,
						  timer: 2000
						})
						})    
				}
			  })
	}
})

const publishDraft = document.getElementById("publishDraft")
const textForm = document.getElementsByTagName("form")[0]
publishDraft.addEventListener('click',function() {
	let data;
	if (title.textContent=="" || title.textContent==null){
		Snackbar.show({text:"Başlık makalenin bel kemiğidir. Lütfen başlık giriniz!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
	}
	else if (link.value=="" || link.value==null){
		Snackbar.show({text:"Görsel linki giriniz!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
	}
	else if (editor.getData()=="" || editor.getData()==null){
		Snackbar.show({text:"Makale alanı boş gözüküyor. Lütfen boşlukları dolduralım!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
	}else {
			data = {
				"id": articleId.value,
				"title": title.textContent,
				"link": link.value,
				"color": RGB || null,
				"content": editor.getData()
			} 
			let booleanDeny= false;
			let confirmText ="Yayınla"	
			let alertTitle = 'Makaleyi yayınlamak istiyor musun?' 		
			Swal.fire({
				title: alertTitle,
				showDenyButton: booleanDeny,
				showCancelButton: true,
				confirmButtonText: confirmText,
				denyButtonText: `Taslak olarak kaydet`,
				cancelButtonText: `İptal`,
			  }).then((result) => {
				if (result.isConfirmed) {
				  fetch("/addarticle?query="+ textForm.getAttribute("data-type")+"&type=publish",
				  {
					  headers: {
					  'Accept': 'application/json',
					  'Content-Type': 'application/json',
					  "X-CSRFToken": csrf_token
					  },
					  method: "POST",
					  body: JSON.stringify(data)
				  })
				  .then(function(res){ 
					  return res.json()
				  })
				  .then(function(res){ 
					  console.log(res)
					  Swal.fire({
						position: 'top-end',
						icon: 'success',
						title: res["message"],
						showConfirmButton: false,
						timer: 1500
					  }).then(function() {
						window.location = res["location"];
					});
				  })
				  .catch(function(res){
					   console.log(res) 
					   Swal.fire({
						position: 'top-end',
						icon: 'error',
						title: "Böyle olsun istemezdik ama sunucu tarafında bir hatalar oldu sanki!",
						showConfirmButton: false,
						timer: 2000
					  })
					  })    
				}
			  })
	}
})