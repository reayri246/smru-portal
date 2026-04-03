(function($) {
    $(document).ready(function() {
        // Function to reload the form
        function reloadForm() {
            // Submit the form to reload with new data
            $('#subject_form').submit();
        }

        // When college changes, reload form
        $('#id_college').change(function() {
            // Clear dependent fields
            $('#id_branch').val('');
            $('#id_year').val('');
            reloadForm();
        });

        // When branch changes, reload form
        $('#id_branch').change(function() {
            // Clear dependent fields
            $('#id_year').val('');
            reloadForm();
        });
    });
})(django.jQuery);