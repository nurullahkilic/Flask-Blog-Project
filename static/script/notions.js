//Spoiler Blur
const spoilers = document.getElementsByClassName("spoiler");
for (var i=0; spoilers.length > i; i++){
  spoilers[i].children[0].addEventListener('click',function (e) {
    var parag = this.parentElement.children[1]
    this.classList.toggle("opacity")
    parag.classList.toggle("noblur")
  })
}
 
 
 //ÜÇ NOKTA DROPDOWN FONSKİYONU 
 
 var options = document.getElementsByClassName("bx bx-dots-horizontal-rounded");
  for (var i = 0; i < options.length; i++) {
    options[i].addEventListener("click", function (e) {
      if (e.target.parentElement.children[4].classList.contains("hidden")) {
        e.target.parentElement.children[4].classList.remove("hidden");
      } else {
        e.target.parentElement.children[4].classList.add("hidden");
      }
    });
  }
  
  window.addEventListener('click',function(event) {
    var wrappers = document.getElementsByClassName("list-drop-notion");
    var i;
    for (i = 0; i < wrappers.length; i++) {
      var openWrapper = wrappers[i];
      if (!openWrapper.classList.contains("hidden") && !openWrapper.parentElement.children[3].isSameNode(event.target)) {
          openWrapper.classList.add("hidden");
      }
    }

} )



//Notion Send Bar Actionları
function escapeHtml(text) {
  var map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };

  return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// const linkBar = document.getElementById("linkBar")
const spoilerBar = document.getElementById("spoilerBar")
const notionTextarea = document.getElementById("notionTextarea")
const notionRightSide = document.querySelector(".cont-right-side")
const notionForm = document.getElementById("notionForm")

spoilerBar.addEventListener("click",function() {
  if(this.getAttribute("disabled")=="disabled"){
    alert("Zaten Spoiler Eklediniz")
  }else{
    Swal.fire({
      title: 'Spoiler Girin',
      input: 'textarea',
      inputAttributes: {
        autocapitalize: 'off'
      },
      showCancelButton: true,
      confirmButtonText: 'Ekle',
      cancelButtonText: 'İptal',
      showLoaderOnConfirm: true,
      preConfirm: (spoiler) => {
        notionTextarea.value += 
        `
[--spoiler--]      
${spoiler}
[--spoiler--]`
      spoilerBar.setAttribute('disabled','disabled')
      },
      allowOutsideClick: () => !Swal.isLoading()
    })
  }
  }
 
)

notionForm.addEventListener("submit",function(e) {
  e.preventDefault()
  let escapedValue = escapeHtml(notionTextarea.value)
  var firstIndexSpo = escapedValue.indexOf("[--spoiler--]");
  var lastIndexSpo = escapedValue.lastIndexOf("[--spoiler--]");
  var spoilerText = escapedValue.substring(firstIndexSpo + 14,lastIndexSpo).trim()
  if (firstIndexSpo=="-1" && lastIndexSpo=="-1"){   
    var htmlOut = escapedValue
  }else{
    var spoilerHTML = `<div class="spoiler"><div class="alert-button"><i class='bx bxs-error-circle' ></i></div><p>${spoilerText}</p></div>`;
    var htmlOut = escapedValue.replace(escapedValue.substring(firstIndexSpo ,lastIndexSpo + 14), spoilerHTML);
  }
  var textOut = escapedValue 

  const data = {
    "text_out": textOut,
    "html_out": htmlOut,
    "product_id": productId,
    "product_type": productType
  }

  fetch("/web/api/notions?query=add",
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
      Snackbar.show({text:dataMsg, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
      notionTextarea.value = ""
  })

  // var firstIndexLink = notionTextarea.value.indexOf("[--link--]");
  // var lastIndexLink = notionTextarea.value.lastIndexOf("[--link--]");
  // var linkText = notionTextarea.value.substring(firstIndexLink + 10,lastIndexLink).trim()
  // var firstIndexLink = res.indexOf("[--link--]");
  // var lastIndexLink = res.lastIndexOf("[--link--]");
  // res2 = res.replace(notionTextarea.value.substring(firstIndexLink ,lastIndexLink + 11), linkText);
})

// linkBar.addEventListener("click",function(params) {
//   Swal.fire({
//     title: 'Linki Girin',
//     input: 'text',
//     inputAttributes: {
//       autocapitalize: 'off'
//     },
//     showCancelButton: true,
//     confirmButtonText: 'Ekle',
//     cancelButtonText: 'İptal',
//     showLoaderOnConfirm: true,
//     preConfirm: (link) => {
//       notionTextarea.value += "[--link--]" + link + "[--link--]"
//     },
//     allowOutsideClick: () => !Swal.isLoading()
//   })
// }
// )

//Left Side Fixed 
const leftSide = document.querySelector('.cont-left-side')
const rightSide = document.querySelector('.cont-right-side')
const leftFixed = document.querySelector('.left-side-fixed')
let windowHeight = (document.documentElement.clientHeight || document.body.clientHeight);
window.onresize= function() {  
  windowHeight = (document.documentElement.clientHeight || document.body.clientHeight)
}
if (leftSide.clientHeight<rightSide.clientHeight){
  window.onscroll = function () {
    let padd = (leftFixed.clientHeight - windowHeight) + 720
    const windowTop = document.documentElement.scrollTop || document.body.scrollTop;
    if (windowTop>padd){
      leftFixed.classList.remove("relative")
    } else {
      leftFixed.classList.add("relative")
    }
  }
}

//RESPONSİVE BACDROP FONKSİYONU
function backdropSize(x) {
    if (x.matches) { // If media query matches
      setInterval(() => {
        backdropImage.style.height = backdropInner.clientHeight + 120 + "px"
        hackdrop.style.height = backdropInner.clientHeight + 150 + "px"
      }, 200);
    } else {
        backdropImage.style.height = 662 + "px"
    }
  }
  
  const x = window.matchMedia("(max-width: 800px)")
  const backdropInner = document.querySelector(".backdrop-inner")
  const backdropImage = document.querySelector(".backdrop-image")
  const hackdrop = document.querySelector(".hackdrop")
  backdropSize(x) // Call listener function at run time
  x.addEventListener('change', backdropSize) // Attach listener function on state changes
  