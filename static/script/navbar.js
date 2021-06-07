const toggleDropdown = function(id){
    const dropdownCont = document.querySelector(`.wrapper > .${id}-dropdown`);
    const wrapper = dropdownCont.parentElement
    const arrow = dropdownCont.parentElement.parentElement.children[0].children[dropdownCont.parentElement.parentElement.children[0].children.length-1]
    wrapper.classList.toggle("hidden");
    arrow.classList.toggle("bx-rotate-180")  
    //DropDown kapatma
    window.addEventListener('keydown',(e)=>{
      if (e.key === "Escape") { 
        wrapper.classList.add("hidden");
        arrow.classList.remove("bx-rotate-180")   
      }
    })   
}

//Bottom Bar'a Active Class'ı Ekleme
const navbarItems = document.getElementsByClassName("bottom-nav-item")
for (let i=0; navbarItems.length>i;i++){
  if(window.location.pathname==navbarItems[i].children[0].getAttribute("href")){
    navbarItems[i].classList.toggle("active")
  }
}