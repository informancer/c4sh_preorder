$(document).ready(function() {
  var choiceCreditCard = $('a#choice-credit-card');
  var choiceBankTransfer = $('a#choice-bank-transfer');

  var infoCreditCard = $('div#info-credit-card');
  var infoBankTransfer = $('div#info-bank-transfer');

  $('div#payment-choice').button();

  choiceCreditCard.click(function() {
    infoCreditCard.show();
    infoBankTransfer.hide();
    choiceBankTransfer.parent().removeClass('active');
    choiceCreditCard.parent().addClass('active');
  });

  choiceBankTransfer.click(function() {
    infoCreditCard.hide();
    infoBankTransfer.show();
    choiceBankTransfer.parent().addClass('active');
    choiceCreditCard.parent().removeClass('active');
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
        $(".payment-errors").text(error.apierror);

        $('.submit-button').attr("disabled", false);
   } else {
       var form = $("#payment-form");

       var token = result.token;

       form.append("<input type='hidden' name='paymill_token' value='" + token + "'/>");

       form.get(0).submit();
   }
}