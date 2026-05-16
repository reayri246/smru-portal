document.addEventListener('DOMContentLoaded', function () {
    var collegeSelect = document.getElementById('id_college');
    var yearSelect = document.getElementById('id_year');
    if (!collegeSelect || !yearSelect) {
        return;
    }

    function filterYearOptions() {
        var selectedCollege = collegeSelect.value;
        var options = Array.prototype.slice.call(yearSelect.options);
        var currentValue = yearSelect.value;
        var visibleCount = 0;

        options.forEach(function (option) {
            if (!option.value) {
                option.hidden = false;
                return;
            }
            var optionCollegeId = option.dataset.collegeId;
            if (!selectedCollege || optionCollegeId === selectedCollege) {
                option.hidden = false;
                visibleCount += 1;
            } else {
                option.hidden = true;
            }
        });

        if (selectedCollege && yearSelect.selectedOptions.length > 0) {
            var selectedOption = yearSelect.selectedOptions[0];
            if (selectedOption.hidden) {
                yearSelect.value = '';
            }
        }

        if (visibleCount === 0 && selectedCollege) {
            yearSelect.value = '';
        } else if (!selectedCollege) {
            yearSelect.value = currentValue;
        }
    }

    collegeSelect.addEventListener('change', filterYearOptions);
    filterYearOptions();
});