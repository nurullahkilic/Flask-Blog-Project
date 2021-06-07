const addList = document.getElementById("addList")
const listContent = document.getElementById("listContent")

addList.addEventListener('click',function(e) {
    const productId = e.currentTarget.getAttribute("data-id")
    const productType = e.currentTarget.getAttribute("data-type")

    fetch(`/web/api/${e.currentTarget.getAttribute("data-user")}?query=list`)
    .then(data=>data.json())
    .then(result=>{
        openPopup("popup-container-user-list")
        listContent.innerHTML = `<div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>`
        var dataHTML = ""
        result.forEach(list => {
            dataHTML += `
            <div class="list-inner" data-id="${list.id}">
                <a href="javascript:;" style="background: linear-gradient(
                90deg,
                rgba(40,40,40, 0.9) 11.86%,
                rgba(40,40,40, 0.4) 77.55%
                ),
                url('${list.picture}')
                no-repeat center center / cover;">
                <h4>${list.name}</h4>
                <h6><span class="fullname">${list.username}</span> · ${list.created_date} </h6>
                </a>            
            </div>
            `
        });
        listContent.innerHTML = dataHTML
        const products = listContent.getElementsByClassName("list-inner")
        for (var i=0; products.length > i; i++){
            products[i].addEventListener('click',function(e) {
                const listId = e.currentTarget.getAttribute("data-id")
                const data = {
                    "list_id": listId,
                    "product_id": productId,
                    "product_type": productType
                }
                fetch("/web/api/addlist",
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
                })
                .catch(function(res){ 
                    console.log(res)
                    Snackbar.show({text:"Böyle olsun istemezdik ama bir hata oldu sanki!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
                }) 
            })
        }
    })
    .catch(function(res){ 
        console.log(res)
        Snackbar.show({text:"Böyle olsun istemezdik ama bir hata oldu sanki!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
    }) 
})


const addWatchList = document.getElementById("addWatchList")
console.log(addWatchList)
addWatchList.addEventListener('click',function (e) {
    const productId = e.currentTarget.getAttribute("data-id")
    const productType = e.currentTarget.getAttribute("data-type")
    const data = {
        "product_id": productId,
        "product_type": productType
    }
    fetch("/web/api/addlist?query=watchlist",
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
    })
    .catch(function(res){ 
        console.log(res)
        Snackbar.show({text:"Böyle olsun istemezdik ama bir hata oldu sanki!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
    })    
})