//yeni liste oluşturma barı
const newList = document.getElementById("new-list-bar");
const noList = document.getElementById("noList");


const showDwight = function(){
    noList.style.background =
      "linear-gradient(90deg,rgba(24, 24, 24, 0.8) 5.46%,rgba(24, 24, 24, 0.1) 100%),url(/static/images/dwight.png), url(/static/images/wall.jpg)";
    noList.style.backgroundPosition = "20%";
    noList.style.backgroundSize = "cover";    
}

const hideDwight = function(){
    noList.style.background =
      "linear-gradient(90deg,rgba(24, 24, 24, 0.8) 5.46%,rgba(24, 24, 24, 0.1) 100%), url(/static/images/wall.jpg)";
    noList.style.backgroundPosition = "20%";
    noList.style.backgroundSize = "cover";
}

if (noList != null) {        
  newList.addEventListener("mousemove", showDwight);
  newList.addEventListener("mouseleave", hideDwight);
}


//Postlardaki küçük resmin konumunu ayarlar
window.onload = function () {
  const titles = document.getElementsByClassName("href-title");
  setInterval(() => {
    for (title of titles) {
      const imagePost =
        title.parentElement.parentElement.parentElement.children[0]
          .children[0];
      const stick =
        title.parentElement.parentElement.parentElement.children[0]
          .children[1];
      imagePost.style.bottom = title.clientHeight + 42 + "px";
      stick.style.height = title.clientHeight + 18 + "px";
    }
  }, 100);
};

//postlardaki açılır dropdown menu 
var dropdowns = document.getElementById("myDropdown");
var dropbtns = document.getElementsByClassName("dropbtn");
for (var i = 0; i < dropbtns.length; i++) {
  dropbtns[i].addEventListener("click", function (e) {
    if (e.target.parentElement.children[1].classList.contains("show")) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains("show")) {
          openDropdown.classList.remove("show");
        }
      }
    } else {
      e.target.parentElement.children[1].classList.toggle("show");
    }
  });
}

window.onclick = function (event) {
  if (!event.target.matches(".dropbtn")) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains("show")) {
        openDropdown.classList.remove("show");
      }
    }
  }
};



//Yan Bar Sabitleme
const leftSide = document.querySelector('.bottom-left-side')
const leftFixed = document.querySelector('.left-side-fixed')
const rightSide = document.querySelector('.bottom-right-side')

//Fixed iken genişlik ayarlama
setInterval(() => {
  leftFixed.style.minWidth = leftSide.clientWidth + 'px';
}, 100);

let windowHeight = (document.documentElement.clientHeight || document.body.clientHeight);
window.onresize= function() {  
  windowHeight = (document.documentElement.clientHeight || document.body.clientHeight)
}
if (leftFixed.clientHeight<rightSide.clientHeight){
  window.onscroll = function () {
    let padd = (leftFixed.clientHeight - windowHeight) + 400
    const windowTop = document.documentElement.scrollTop || document.body.scrollTop;
    if (windowTop>padd){
      leftFixed.classList.remove("relative")
    } else {
      leftFixed.classList.add("relative")
    }
  }  
}



//Follow Fonksiyonu
const follow = function(e) {
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
    if (elem.classList.contains('btn-success')){
      elem.innerHTML = `<i class='bx bxs-user-minus' ></i> Takibi Bırak`
      elem.className = "btn-danger"
    }else{
      elem.innerHTML = `<i class='bx bxs-user-plus' ></i> Takip Et`
      elem.className = "btn-success"
    }
    const dataMsg = data["message"]
    Snackbar.show({text:dataMsg, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
  })
  .catch(function(res){ console.log(res) }) 
}


//FOLLOW BUTONU
const followBtn = document.getElementById("followBtn")
const follower = document.getElementById("follower")
const followContainer = document.querySelector(".follow-container")

if (followBtn != null) {
  followBtn.addEventListener('click', follow)
}

//FOLLOW POPUP REQUESTİ
const followPopups = document.getElementsByClassName("followPopups")
for (var i=0; followPopups.length > i; i++){
  followPopups[i].addEventListener('click',function (e) {
      const user_id = e.target.getAttribute("data-id")
      const query = e.target.getAttribute("data-query")

      fetch(`/web/api/${user_id}?query=${query}`)
      .then(data=>data.json())
      .then(result=>{
        openPopup("popup-container-follow")
        followContainer.innerHTML = `<div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>`
        var dataHTML = ""
        result.forEach(user => {
          dataHTML += `
          <div class="follow-content">
            <div class="follow-left-side">
              <a href="/@${user.username}">
                <img src="${user.profile_pic}" alt="" />
              </a>
              <div class="follow-user">
                <a href="/@${user.username}"><h3>${user.fullname}</h3> <h5>@${user.username}</h5></a>                
              </div>
            </div> 
          `
          if(session_username==user.username){
            dataHTML += `
            <div class="follow-right-side">          
            </div>
            </div>          
            `
          }else {
            if (user.is_following_viewer){
              dataHTML += `
                <div class="follow-right-side">
                  <a href="javascript:;" data-id="${user.id}" class="btn-danger btn-follow"><i class='bx bxs-user-minus' ></i> Takibi Bırak</a>
                </div>
              </div>          
              `
            } else {
              dataHTML += `
              <div class="follow-right-side">
                <a href="javascript:;" data-id="${user.id}" class="btn-success btn-follow"><i class='bx bxs-user-plus' ></i> Takip Et</a>
              </div>
              </div>          
             `
            }
          }
    
        });
        followContainer.innerHTML = dataHTML
        //Popup içindeki butonları dinleyerek fonksiyon verme
        const btnFollows = followContainer.getElementsByClassName("btn-follow")
        for (var i=0; btnFollows.length > i; i++){
          btnFollows[i].addEventListener('click',follow)
        }
      })
      .catch(err=>{
        console.log(err)
      })    
  })
}
