
$.getScript( "https://maps.googleapis.com/maps/api/js?key=" + google_api_key + "&libraries=places&callback=initAutoComplete")
.done(function( script, textStatus ) {
    window.addEventListener("load", initAutoComplete)
})

let autocomplete;

function initAutoComplete(){
   autocomplete = new google.maps.places.Autocomplete(
       document.getElementById('id-google-address'),
       {
           types: ['address'],
           componentRestrictions: {'country': [base_country.toLowerCase()]},
       })

   autocomplete.addListener('place_changed', onPlaceChanged);
}


function onPlaceChanged (){

    var place = autocomplete.getPlace();

    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id-google-address').value

    if (!place.geometry){
        document.getElementById('id-google-address').placeholder = "*Begin typing address";
    }
    else{
        var no_city = true
        var no_state = true
        var no_country = true
        var no_postal_code = true
        for (var i = 0; i < place.address_components.length; i++) {
            for (var j = 0; j < place.address_components[i].types.length; j++) {
     
                if (place.address_components[i].types[j] == "sublocality_level_1" || place.address_components[i].types[j] == "locality") {
                    $('#id_city').val(place.address_components[i].long_name)
                    no_city = false
                }              
                if (place.address_components[i].types[j] == "administrative_area_level_1") {
                    $('#id_state').val(place.address_components[i].long_name)
                    no_state = false
                }
                if (place.address_components[i].types[j] == "country") {
                    $('#id_country').val(place.address_components[i].short_name)
                    no_country = false
                }

                if (place.address_components[i].types[j] == "postal_code") {
                    $('#id_zip_code').val(place.address_components[i].long_name)
                    no_postal_code = false
                }
            }
        }
        $('#id_address1').val(place.name)
        if (no_city) {
            $('#id_city').val("")
        }
        if (no_state) {
            $('#id_state').val("")
        }
        if (no_country) {
            $('#id_country').val("")
        }
        if (no_postal_code) {
            $('#id_zip_code').val("")
        }

        //find all hidden inputs & ignore csrf token
        var x = $( "input:hidden" );
        console.log(x)
        for (let i = 0; i < x.length; i++){
            if (x[i].name != "csrfmiddlewaretoken")
            x[i].type = "text";
            // x.eq(x).attr("class", 'hidden-el')
        }

        // //fade in the completed form
        // $('.hidden-el').fadeIn('slow')
        // $('#listing-btn').removeAttr("disabled")
    }
}
