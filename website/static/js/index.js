window.setTimeout(function () {
  $(".alert").remove()
}, 4000);

$('#profile_image').change(function () {
  var file_data = $('#profile_image').prop('files')[0];
  var form_data = new FormData();
  form_data.append('file', file_data);
  $.ajax({
    url: '/upload_image',
    type: "POST",
    data: form_data,
    contentType: false,
    cache: false,
    processData: false,
    success: function (response) {
      if (response.success) {
        $("#display_profile_image").attr('src', response.url);
        $("#header_user_image").attr('src', response.url);
      }
    }
  });
});

function selectProfileImage() {
  $('#profile_image').click();
}