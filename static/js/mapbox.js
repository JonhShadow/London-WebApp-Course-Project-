var geocodingClient = mapboxSdk({
    accessToken:
        "pk.eyJ1Ijoibmlja25hbWUyMSIsImEiOiJja2xmNGwxbGUwa3o5Mm9wMGs4cXlqMXNkIn0.Kw8taLGhoDnjr8qXaDz2KA",
});

function autocompleteSuggestionMapBoxAPI(inputParams, callback) {
    geocodingClient.geocoding
        .forwardGeocode({
            query: inputParams,
            countries: ["us"],
            bbox: [
                -124.862197896945,
                45.5435400017256,
                -116.916070668425,
                49.0121490866648,
            ],
            types: ['address'],
            autocomplete: true,
            limit: 5,
        })
        .send()
        .then((response) => {
            const match = response.body;
            console.log(match)
            callback(match);
        });
}

function autocompleteInputBox(inp) {
    var currentFocus;
    inp.addEventListener("input", function (e) {
        var a, b, i, val = this.value;
        closeAllLists();
        if (!val) {
            return false;
        }
        currentFocus = -1;
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(a);

        // suggestion list MapBox api called with callback
        autocompleteSuggestionMapBoxAPI(
            $("#myInput").val(),
            function (results) {
                results.features.forEach(function (key) {
                    b = document.createElement("DIV");
                    b.innerHTML =
                        "<strong>" +
                        key.place_name.substr(0, val.length) +
                        "</strong>";
                    b.innerHTML += key.place_name.substr(val.length);
                    b.innerHTML +=
                        "<input type='hidden' data-lat='" +
                        key.geometry.coordinates[1] +
                        "' data-lng='" +
                        key.geometry.coordinates[0] +
                        "'  value='" +
                        key.place_name +
                        "'>";
                    b.addEventListener("click", function (e) {
                        let lat = $(this).find("input").attr("data-lat");
                        let long = $(this).find("input").attr("data-lng");

                        document.getElementById('lat').value = lat
                        document.getElementById('long').value = long
                        for (const x in key.context) {
                            if (key.context[x].id.includes("postcode")) {
                                document.getElementById('inputzip').value = key.context[x].text;
                                break;
                            }
                        }
                        /*
                        var frame = document.getElementById("frame-map");
                        var map_id = frame.contentWindow.document.getElementsByClassName("folium-map")[0].id;
                        console.log(map_id);
                        var map = window[map_id];
                        var frame_map = frame.contentWindow.document.getElementById(map_id).contentWindow.m;
                        L.marker([lat, long], {opacity: .4}).addTo(frame_map);
                        */

                        /*
                        var a = document.createElement('a');
                        a.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(key)));
                        a.setAttribute('download', 'filename.json');
                        a.click()
                        */

                        inp.value = $(this).find("input").val();
                        $(inp).attr("data-lat", lat);
                        $(inp).attr("data-lng", long);
                        closeAllLists();
                    });
                    a.appendChild(b);
                });
            }
        );
    });

    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function (e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
                  increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) {
            //up
            /*If the arrow UP key is pressed,
                  decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });

    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = x.length - 1;
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }

    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
            except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }

    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
        console.log(document.getElementById("myInput"))
    });
}

autocompleteInputBox(document.getElementById("myInput"));