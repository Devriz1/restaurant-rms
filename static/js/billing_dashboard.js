const search = document.getElementById("searchGuest");

if(search){

    search.addEventListener("keyup", function(){

        const value = this.value.toLowerCase();

        document.querySelectorAll(".billing-card").forEach(card=>{

            card.style.display =
                card.innerText.toLowerCase().includes(value)
                ? ""
                : "none";

        });

    });

}