document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('form'); // Select the form element

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent the default form submission

        // Define the age mapping object
        const ageMapping = {
            'under_18': 18,  // Added an entry for 'under_18'
            '18_24': 21,
            '25_34': 30,
            '35_44': 40,
            '45_54': 50,
            '55_64': 60,
            '65_over': 70
        };

        // Create a FormData object from the form
        const formData = new FormData(form);

        // Get the age group selected and map it to the appropriate value
        const selectedAge = formData.get('age');
        const ageValue = ageMapping[selectedAge];

        // Build the JSON object based on the API's expected structure with the correct data types
        const data = {
            cost_t: parseFloat(formData.get('cost')), // float32
            age: parseFloat(ageValue), // float32
            dem_female: parseInt(formData.get('gender') === 'female' ? 1 : 0, 10), // int8
            race: parseInt(formData.get('race') === 'Black' ? 1 : 0, 10), // int8
            biomarkers: parseFloat(formData.get('biomarker')), // float32
            comorbidity: parseInt(formData.get('comorbidity'), 10), // int8
            lasix_dose_count_tm1: parseFloat(formData.get('lasix_dose_count_tm1')), // float32
            cre_tests_tm1: parseFloat(formData.get('cre_tests_tm1')), // float32
            crp_tests_tm1: parseFloat(formData.get('crp_tests_tm1')), // float32
            esr_tests_tm1: parseFloat(formData.get('esr_tests_tm1')), // float32
            ghba1c_tests_tm1: parseFloat(formData.get('ghba1c_tests_tm1')), // float32
            hct_tests_tm1: parseFloat(formData.get('hct_tests_tm1')), // float32
            ldl_tests_tm1: parseFloat(formData.get('ldl_tests_tm1')), // float32
            nt_bnp_tests_tm1: parseFloat(formData.get('nt_bnp_tests_tm1')), // float32
            sodium_tests_tm1: parseFloat(formData.get('sodium_tests_tm1')), // float32
            trig_tests_tm1: parseFloat(formData.get('trig_tests_tm1')) // float32
        };

        // Log the data to the console for testing
        console.log(JSON.stringify(data));
        // Send the data to the API via fetch
        fetch('https://riskscore-predicition-d7a9cyfvfnf3fvc7.southindia-01.azurewebsites.net/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data) // Send the JSON object
        })
            .then(response => response.json())
            .then(result => {
                // Store form data and updated result in localStorage
                localStorage.setItem('formData', JSON.stringify(Object.fromEntries(formData)));
                localStorage.setItem('predictedRiskScore', result.predicted_risk_score.toFixed(2));

                // Redirect to the result page
                window.location.href = '/result';

            })
            .catch(error => console.error('Error:', error));


    });
});
