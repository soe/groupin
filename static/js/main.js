$(document).ready(function(){
  $('a[rel=tooltip]').tooltip();
  $('a[rel=popover]').popover({'placement': 'right', });
  $('#credits').popover({'placement': 'top', });
});