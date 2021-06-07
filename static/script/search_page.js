var dropdowns = document.getElementById("myDropdown-search");
var dropbtns = document.querySelector(".dropbtn-search");


dropbtns.addEventListener("click",function(e){
  if (e.target.parentElement.children[1].classList.contains('show')) { 

      if (dropdowns.classList.contains('show')) {
        dropdowns.classList.remove('show');
      }
    }
    else {
    e.target.parentElement.children[1].classList.toggle("show");
  }
});

dropdowns.addEventListener("click",function(){
  if (dropdowns.classList.contains('show')) {
    dropdowns.classList.remove('show');
  }
})

const articlesInner = document.querySelector(".search-articles")
const usersInner = document.querySelector(".search-users")
const moviesInner = document.querySelector(".search-movies-inner")
const seriesInner = document.querySelector(".search-series-inner")

const searchBar = document.querySelector(".search-page-input")
let oldArticles = articlesInner.innerHTML
let oldUsers = usersInner.innerHTML
let oldMovies = moviesInner.innerHTML
let oldSeries = seriesInner.innerHTML


searchBar.addEventListener("input", function () {
  setTimeout(function() {
    fetch(`/web/api/search?query=${searchBar.value.trim()}`)
    .then(function (response) {
      return response.json();
    })
    .then(function (res) {
      //Article Bar
      if (searchBar.value==""){
        articlesInner.parentElement.style.display="flex"
        articlesInner.innerHTML = oldArticles
      }else if(res.articles.length==0){  
        articlesInner.parentElement.style.display="none"
        const emptyElement = document.createElement("div")
        emptyElement.className = "search-articles-inner"
        emptyElement.style.background = "linear-gradient(270deg,rgba(29,29,29, 0.2) 10%,rgba(29,29,29, 0.62) 60%)"
        emptyElement.innerHTML =`
        <div class="articles-info">
          <a class="href-title"><h1><i>'${searchBar.value}'</i> için hiçbir makale bulunamadı!</h1></a>
        </div>        
        `
        articlesInner.innerHTML =""
        articlesInner.append(emptyElement)
      }else {
        articlesInner.parentElement.style.display="flex"
        articlesInner.innerHTML = " "
        res.articles.forEach(article => {
          const articleElement = `
          <div
          class="search-articles-inner"
          style="
            background: linear-gradient(
                270deg,
                rgba(29,29,29, 0.2) 10%,
                rgba(29,29,29, 0.62) 60%
              ),
              url('${article.thumbnail}');
            background-position: 20%;
            background-size: cover;
            background-blend-mode: multiply;
          "
        >
          <div class="articles-info">
            <h4>
              <a href="/@${article.author_username}" class="user-fullname"
                >${article.author_fullname}</a
              >
              · ${article.created_date}
            </h4>
            <a
              href="/article/${article.slug}"
              class="href-title"
              title="${article.title}"
              ><h1>
              ${article.title}
              </h1></a
            >
          </div>
          <div class="article-actions">
            <div>
              <a href="/article/${article.slug}#comment"
                ><img src="/static/icons/comment.svg" alt=""
              /></a>
              <span>${article.comment}</span>
            </div>
            <div>
              <a href=""><img src="/static/icons/like.svg" alt="" /></a>
              <span>${article.like}</span>
            </div>
          </div>
        </div>
          `
            articlesInner.innerHTML+=articleElement
        });
      }
     
      //Users Bar
      if (searchBar.value==""){
        usersInner.parentElement.style.display="flex"
        usersInner.innerHTML = oldUsers
      }else if(res.users.length==0){  
        usersInner.parentElement.style.display="none"
        // const emptyElement = document.createElement("div")
        // emptyElement.className = "search-users-inner"
        // emptyElement.style.background = "linear-gradient(90deg,rgba(0, 0, 0, 0.2) 10%,rgba(0, 0, 0, 0.8) 60%)"
        // emptyElement.innerHTML =`        
        // <div>
        //   <div class="user-name">
        //     <a href=""><h2>'${searchBar.value}' için hiç kimse bulunamadı!</h2></a>
        //   </div>
        // </div>      
        // `
        // usersInner.innerHTML =""
        // usersInner.append(emptyElement)
      }else {
        usersInner.parentElement.style.display="flex"
        usersInner.innerHTML = " "
        res.users.forEach(user => {
          const userElement = `
          <div
          class="search-users-inner"
          style="
            background: linear-gradient(
                90deg,
                rgba(0, 0, 0, 0.2) 10%,
                rgba(0, 0, 0, 0.8) 60%
              ),
              url('${user.banner_pic}');
            background-position: 20%;
            background-size: cover;
            background-blend-mode: multiply;
          "
        >
          <img src="${user.profile_pic}" alt="" />
          <div>
            <div class="user-name">
              <a href="/@${user.username}"><h2>${user.fullname}</h2></a>
              <h5>@${user.username}</h5>
            </div>
            <a href="" class="btn-success">Takip Et</a>
          </div>
        </div>
          `
            usersInner.innerHTML+=userElement
        });
      }

      //Movies Bar
      if (searchBar.value==""){
        moviesInner.parentElement.style.display="flex"
        moviesInner.innerHTML = oldMovies
      }else if(res.movies.length==0){  
        moviesInner.parentElement.style.display="none"
        const emptyElement = document.createElement("div")
        emptyElement.className = "table-inner"
        emptyElement.style.background = "linear-gradient(360deg,rgba(24, 24, 24, 0.95) 0%,rgba(0, 0, 0, 0) 80.77%)"
        emptyElement.innerHTML =`        
        <div class="table-text">
        <div class="text-top">
          <span class="stick"></span>
          <h4>
          Film
          </h4>
        </div>
        <h2>'${searchBar.value}' için hiçbir film bulunamadı!</h2>
      </div>
      <a href=""></a>    
        `
        moviesInner.innerHTML =""
        moviesInner.append(emptyElement)
      }else {
        moviesInner.parentElement.style.display="flex"
        moviesInner.innerHTML = " "
        res.movies.forEach(movie => {
          const movieElement = `
          <div
          class="table-inner"
          style="
      background: linear-gradient(
          360deg,
          rgba(24, 24, 24, 0.95) 0%,
          rgba(0, 0, 0, 0) 80.77%
        ),
        url('https://www.themoviedb.org/t/p/w780${movie.backdrop}')
          no-repeat center center / cover;
      background-blend-mode: multiply;
    "
        >
          <div class="table-text">
            <div class="text-top">
              <span class="stick"></span>
              <h4>
              ${movie.director==null ? '' : movie.director} (${movie.year})
              </h4>
            </div>
            <h2>${movie.title}</h2>
          </div>
          <a href="/movies/${movie.movie_id}"></a>
        </div>
          `
            moviesInner.innerHTML+=movieElement
        });
      }

      //Series Bar
      if (searchBar.value==""){
        seriesInner.parentElement.style.display="flex"
        seriesInner.innerHTML = oldMovies
      }else if(res.series.length==0){  
        seriesInner.parentElement.style.display="none"
        const emptyElement = document.createElement("div")
        emptyElement.className = "table-inner"
        emptyElement.style.background = "linear-gradient(360deg,rgba(24, 24, 24, 0.95) 0%,rgba(0, 0, 0, 0) 80.77%)"
        emptyElement.innerHTML =`        
        <div class="table-text">
        <div class="text-top">
          <span class="stick"></span>
          <h4>
          Dizi
          </h4>
        </div>
        <h2>'${searchBar.value}' için hiçbir dizi bulunamadı!</h2>
      </div>
      <a href=""></a>    
        `
        seriesInner.innerHTML =""
        seriesInner.append(emptyElement)
      }else {
        seriesInner.parentElement.style.display="flex"
        seriesInner.innerHTML = " "
        res.series.forEach(serie => {
          const movieElement = `
          <div
          class="table-inner"
          style="
      background: linear-gradient(
          360deg,
          rgba(24, 24, 24, 0.95) 0%,
          rgba(0, 0, 0, 0) 80.77%
        ),
        url('https://www.themoviedb.org/t/p/w780${serie.backdrop}')
          no-repeat center center / cover;
      background-blend-mode: multiply;
    "
        >
          <div class="table-text">
            <div class="text-top">
              <span class="stick"></span>
              <h4>
              ${serie.director==null ? '' : serie.director } (${serie.year})
              </h4>
            </div>
            <h2>${serie.title}</h2>
          </div>
          <a href="/series/${serie.movie_id}"></a>
        </div>
          `
          seriesInner.innerHTML+=movieElement
        });
      }
     





      
      
      
      // console.log(res);      
    })
    .catch((err) => {
      console.log(err);
    });




  },370)  
});