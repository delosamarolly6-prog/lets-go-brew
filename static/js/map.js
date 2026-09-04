async function initMap() {

    // Temporary location
    // We will replace this with the actual
    // Let's Go Brew Café coordinates later.

    const position = {
        lat: 14.5995,
        lng: 120.9842
    };


    const { Map } =
        await google.maps.importLibrary("maps");

    const { AdvancedMarkerElement } =
        await google.maps.importLibrary("marker");


    const map = new Map(
        document.getElementById("map"),
        {
            center: position,
            zoom: 15,
            mapId: "AIzaSyAMLgtZZdNAyK9t73sD8MXgsn5bZZJSuBg"
        }
    );


    const marker =
        new AdvancedMarkerElement({
            map: map,
            position: position,
            title: "Let's Go Brew Café"
        });

}


function loadGoogleMaps() {

    const script =
        document.createElement("script");

    script.src =
        "https://maps.googleapis.com/maps/api/js" +
        "?key=" +
        window.GOOGLE_MAPS_API_KEY +
        "&v=weekly";

    script.async = true;

    script.defer = true;

    script.onload = initMap;

    document.head.appendChild(script);
}


loadGoogleMaps();