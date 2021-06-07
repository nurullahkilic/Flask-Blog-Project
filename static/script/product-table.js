function live (eventType, elementQuerySelector, cb) {
    document.addEventListener(eventType, function (event) {
        var qs = document.querySelectorAll(elementQuerySelector);

        if (qs) {
            var el = event.target, index = -1;
            while (el && ((index = Array.prototype.indexOf.call(qs, el)) === -1)) {
                el = el.parentElement;
            }

            if (index > -1) {
                cb.call(el, event);
            }
        }
    });
}

live("click", "div.add-list-profile", function (e) {
    const productId = e.target.getAttribute("data-id")
    const productType = e.target.getAttribute("data-type")
    fetch(`/web/api/${e.target.getAttribute("data-user")}?query=list`)
    .then((data)=>{
        return data.text()
    })
    .then((data)=>{
        var result = JSON.parse(data)
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
                .then(function(res){ 
                    return res.text()
                })
                .then(function(result){
                    var data = JSON.parse(result)
                    const dataMsg = data["message"]
                    Snackbar.show({text:dataMsg, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
                })
                .catch(function(res){ 
                    console.log(res)
                    Snackbar.show({text:res, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
                    Snackbar.show({text:"Böyle olsun istemezdik ama bir hata oldu sanki!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
                }) 
            })
        }
    })
    .catch(function(res){ 
        console.log(res)
        Snackbar.show({text:"Böyle olsun istemezdik ama bir hata oldu sanki!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
    }) 
});

live("click", "div.add-watchlist-profile", function (e) {
    const productId = e.target.getAttribute("data-id")
    const productType = e.target.getAttribute("data-type")
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
});

live("click", "div.remove-watchlist-profile", function (e) {
    const list_item = e.target.parentElement.parentElement.parentElement.parentElement
    const productId = e.target.getAttribute("data-id")
    const productType = e.target.getAttribute("data-type")
    const data = {
        "product_id": productId,
        "product_type": productType
    }
    fetch("/web/api/removelist?query=watchlist",
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
        list_item.remove()
        Snackbar.show({text:dataMsg, pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
    })
    .catch(function(res){ 
        console.log(res)
        Snackbar.show({text:"Böyle olsun istemezdik ama bir hata oldu sanki!", pos: 'top-center', actionText: 'Tamam', actionTextColor: '#90da54'});
    })    

});
