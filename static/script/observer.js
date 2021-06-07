const target = document.getElementById("loadMore")
const tableInner = document.querySelector(".table-items")
var counter = 9;


const callback = function(e) {
    if(e[0].isIntersecting){     
        loadMore()        
    }
    if (e[0].boundingClientRect.y <34){
        loadMore()
    }
    tableInners = document.getElementsByClassName("table-inner")
}

const loadMore = () => {
    fetch('/web/api/'+list_userid+'?query=watchlist&counter=' + counter,{
        headers: {
            'Accept': 'application/json',
            'Content-Type':'application/json'
        }
    })
    .then(function (res){
        return res.text()
    })
    .then(result=>{
        var data = JSON.parse(result)
        for(let i = 0; i < data.length; i++){
            var inner = `
            <div
            class="table-inner"
            style="
            background: linear-gradient(
                360deg,
                rgba(24, 24, 24, 0.95) 0%,
                rgba(0, 0, 0, 0) 80.77%
                ),
                url('https://www.themoviedb.org/t/p/w780${data[i].backdrop}')
                no-repeat center center / cover;
            background-blend-mode: multiply;
            "
            >
            <div class="table-text">
            <div class="text-top">
                <span class="stick"></span>
                <h4>
                ${data[i].director} (${data[i].created_date})
                </h4>
            </div>
            <h2>${data[i].title || data[i].original_name}</h2>
            </div>
            <a href="/${data[i].product_type_name}/${data[i].product_id}"></a>
            <div class="table-actions">`

            if(session_userid==list_userid){
                inner += `
                <div class="actions-btn">
                <div class="btn-inner remove-watchlist-profile">
                <i 
                data-id="${data[i].product_id}"
                data-type="${data[i].product_type}" 
                class="bx bxs-trash"></i>
                </div>
                <div class="table-dropdown-content">
                <div>İzleme Listenden Kaldır!</div>
                </div>
            </div>     
                `
              }else {
                inner += `
                <div class="actions-btn">
                <div class="btn-inner add-watchlist-profile">
                <i 
                data-id="${data[i].product_id}"
                data-type="${data[i].product_type}" 
                class="bx bxs-bookmark-alt"></i>
                </div>
                <div class="table-dropdown-content">
                <div>İzleme Listene Ekle!</div>
                </div>
            </div>        
                `
              }
            inner += 
            `<div class="actions-btn add-list-profile">
                <div class="btn-inner">
                <i data-id="${data[i].product_id}"
                data-type="${data[i].product_type}"        
                data-user="${session_userid}" style="font-size: 31px !important" class="bx bx-list-plus"></i>
                </div>
                <div class="table-dropdown-content">
                <div>Listene Ekle!</div>
                </div>
            </div>
            </div>
            <div class="table-rate"></div>
            </div>    
            `
            counter +=1
            tableInner.innerHTML += inner
        }
        if(!data.length){
            target.remove()
        }

    }).catch(err=>{
        console.log(err)
        Snackbar.show({text:"Böyle olsun istemezdik ama bir hata oldu sanki!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
        Snackbar.show({text:err, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
    })
}

const option = {
    rootMargin:"120px",
}

const observer = new IntersectionObserver(callback,option)
observer.observe(target)
