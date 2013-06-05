getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

updateMatches = function(form) {
	var value = $(form).find('select').val();
	if (typeof(value) != 'undefined' && value >= 1) {
		$.ajax({
			type: 'post',
			url: '/admin/api/get-preorder.json',
			dataType: 'json',
			data: 'id='+value,
			beforeSend: function(xhr) {
				xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			},
			success: function(data) {
				if (data.success) {
					var csv_data = $(form).parent().parent().find('td').find('pre').html();
					var entry_date = $(form).parent().parent().prev().find('td.entry_date').html();
					var val = $(form).parent().parent().prev().find('td.value').html();
					html = '<tr>';
					html +='<td><input name="preorder" type="checkbox" value="'+value+'" checked /> <i class="icon-ok"></i></td>';
					html += '<td>'+data.preorder+'</td>';
					html += '<td>'+entry_date+'</td>';
					html += '<td>'+val+'</td>';
					html += '<td><a onclick="$(this).parent().parent().next().remove();$(this).parent().parent().remove()" href="javascript:void(0)"><i class="icon-remove"></i></a></td>';
					html += '</tr><tr>';
					html += '<td colspan="10"><small>This reference has been manually added.</small><pre>'+csv_data+'</pre></td>';
					html += '</tr>';
					$('table#successful_matches').append(html);
					$(form).parent().parent().prev().remove();
					$(form).parent().parent().remove();
				} else {
					alert("API call got unexpected response.");
				}
			}
		}).error(function() {
			alert("API call got unexpected response.");
		});
	}
};

$('input[name=without_billingaddress]').on('change', function() {
	$('div#billingaddress').toggle();  
});