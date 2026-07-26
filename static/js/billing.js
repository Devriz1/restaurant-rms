/* ==========================================================
   RESTAURANT RMS
   POS BILLING JAVASCRIPT
========================================================== */


document.addEventListener(
    "DOMContentLoaded",
    function(){



        const discountType =
            document.querySelector(
                "#id_discount_type"
            );


        const discount =
            document.querySelector(
                "#id_discount"
            );


        const serviceCharge =
            document.querySelector(
                "#id_service_charge"
            );


        const tax =
            document.querySelector(
                "#id_tax"
            );


        const amountReceived =
            document.querySelector(
                "input[name='amount']"
            );



        const subtotalElement =
            document.querySelector(
                ".summary-line strong"
            );


        const totalElement =
            document.querySelector(
                ".total-box h1"
            );



        const balanceBox =
            document.createElement(
                "div"
            );


        balanceBox.className =
            "balance-box";


        document
        .querySelector(
            ".payment-section"
        )
        .appendChild(
            balanceBox
        );




        function money(value){

            return "₹ " +
            Number(value)
            .toFixed(2);

        }





        function calculate(){


            let subtotal =
                parseFloat(
                    subtotalElement
                    .innerText
                    .replace("₹","")
                )
                ||0;



            let discountValue =
                parseFloat(
                    discount.value
                )
                ||0;



            let discountAmount=0;



            if(
                discountType.value
                ==="percent"
            ){

                discountAmount =
                subtotal *
                discountValue /
                100;

            }

            else{

                discountAmount =
                discountValue;

            }




            if(
                discountAmount >
                subtotal
            ){

                discountAmount =
                subtotal;

            }




            let service =
                parseFloat(
                    serviceCharge.value
                )
                ||0;



            let taxAmount =
                parseFloat(
                    tax.value
                )
                ||0;




            let total =
                subtotal
                -
                discountAmount
                +
                service
                +
                taxAmount;



            if(total < 0){

                total=0;

            }




            totalElement.innerText =
                money(total);




            if(amountReceived){


                let received =
                parseFloat(
                    amountReceived.value
                )
                ||0;



                let balance =
                received-total;



                balanceBox.innerHTML =

                `
                <strong>
                Balance:
                </strong>

                ${
                    money(balance)
                }

                `;


            }



        }





        [
            discountType,
            discount,
            serviceCharge,
            tax,
            amountReceived

        ]
        .forEach(
            element=>{


                if(element){

                    element.addEventListener(
                        "input",
                        calculate
                    );


                    element.addEventListener(
                        "change",
                        calculate
                    );

                }


            }
        );



        calculate();



    }
);