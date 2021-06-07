//popup açma
const openPopup = function(id){
    const popupCont = document.querySelector("#"+ id);
    const popupInner = popupCont.children[0].children[0]
    const popupBack = popupCont.children[0]
    popupBack.style.visibility = "visible"
    popupBack.style.opacity = "1"
    popupInner.style.top = "calc(50% - 20px)"

    // //Body scrollunu kaldırma
    // const scrollY = window.scrollY;
    // const body = document.body;
    // body.style.position = 'fixed';
    // body.style.top = `-${scrollY}px`;
    
    //popup kapatma
    window.addEventListener('keydown',(e)=>{
      if (e.key === "Escape") { 
          popupBack.style.visibility = "hidden"
          popupBack.style.opacity = ".8"
          popupInner.style.top = "calc(-41%)"

          //Body scrollunu aktif etme
          // body.style.position = '';
          // body.scrollY= scrollY;
      }
    })
    popupCont.addEventListener('click',(e)=>{
        if (e.target.className=="popup" || e.target.className=="bx bx-x" ){
            popupBack.style.visibility = "hidden"
            popupBack.style.opacity = "0"
            popupInner.style.top = "calc(-41%)"
            //Body scrollunu aktif etme
            // body.style.position = '';
            // body.scrollY= scrollY;
        }
    })
    
  }

//Liste üç noktası açma kapama
  var options = document.getElementsByClassName("bx-dots-vertical-rounded");
  for (var i = 0; i < options.length; i++) {
    options[i].addEventListener("click", function (e) {      
      if (e.target.parentElement.children[2].classList.contains("hidden")) {
        e.target.parentElement.children[2].classList.remove("hidden");
      } else {
        e.target.parentElement.children[2].classList.add("hidden");
      }
    });
  }
  
  window.addEventListener('click',function(event) {
    var wrappers = document.getElementsByClassName("list-drop");
    var i;
    for (i = 0; i < wrappers.length; i++) {
      var openWrapper = wrappers[i];
      if (!openWrapper.classList.contains("hidden") && !openWrapper.parentElement.children[1].isSameNode(event.target)) {
          openWrapper.classList.add("hidden");
      }
    }

} )
