// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable({
    "lengthMenu": [[16, 25, 50, -1], [16, 25, 50, "All"]]
  });
});

$(document).ready(function() {
  $('#dataTable2').DataTable({
    "lengthMenu": [[16, 25, 50, -1], [16, 25, 50, "All"]]
  });
});
