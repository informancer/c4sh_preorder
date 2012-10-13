$(document).ready(function() {
  var choiceCreditCard = $('button#choice-credit-card');
  var choiceBankTransfer = $('button#choice-bank-transfer');

  var infoCreditCard = $('div#info-credit-card');
  var infoBankTransfer = $('div#info-bank-transfer');

  $('div#payment-choice').button();

  choiceCreditCard.click(function() {
    infoCreditCard.show();
    infoBankTransfer.hide();
  });

  choiceBankTransfer.click(function() {
    infoCreditCard.hide();
    infoBankTransfer.show();
  });

  $("#payment-form").submit(function(event) {

    $('.submit-button').attr("disabled", "disabled");

    paymill.createToken({
        number: $('.card-number').val(), //benötigt
        exp_month: $('.card-expiry-month').val(), //benötigt
        exp_year: $('.card-expiry-year').val(), //benötigt
        cvc: $('.card-cvc').val(), //optional
        cardholder: $('.card-holdername').val() //optional

    }, paymillResponseHandler);

    return false;
  });
});

function paymillResponseHandler(error,result) {
   if (error) {
        // zeigt Fehler im Formular an
        $(".payment-errors").text(error.apierror);

        $('.submit-button').attr("disabled", false);
   } else {
       var form = $("#payment-form");

       // Token wird ausgegeben
       var token = result.token;

       // Token wird deinem Formular hinzugefügt und wird an Server übergeben
       form.append("<input type='hidden' name='paymillToken' value='" + token + "'/>");

       // Formular absenden
       form.get(0).submit();
   }
}