html="""
<!DOCTYPE html>
<html>
  <head>
    <title>Itinéraire sécurisé</title>
    <style>
      body { font-family: Arial; padding: 20px; }
      input, button, select { margin: 10px 0; padding: 10px; width: 100%; max-width: 500px; }
      #map { height: 70vh; width: 100%; margin-top: 20px; }
    </style>
  </head>
  <body>
    <h2>Planifier un itinéraire sécurisé</h2>
    <input id="origin" type="text" placeholder="Origine (ex: Paris)" />
    <input id="destination" type="text" placeholder="Destination (ex: Lyon)" />
    <button onclick="initMap()">Afficher les itinéraires</button>
    <select id="routeSelector" onchange="changeRoute()" style="display:none;"></select>
    <div id="map"></div>

    <!-- Firebase SDK -->
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore.js"></script>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCa5eES736vT1iDDLFLd_wlMNRiSqz9aks&libraries=places,geometry"></script>

    <script>
      // 🔐 Firebase config (remplace par tes vraies infos)
      const firebaseConfig = {
          apiKey: "AIzaSyCVrtMdl4OXsi3DelUAfBDnrLmqA6uNGk0",
          authDomain: "safe-b04bc.firebaseapp.com",
          projectId: "safe-b04bc",
          storageBucket: "safe-b04bc.firebasestorage.app",
          messagingSenderId: "571704741536",
          appId: "1:571704741536:web:ca2e3deaf87f93a5a543c5"
          };

      firebase.initializeApp(firebaseConfig);
      const db = firebase.firestore();

      let directionsRenderer, directionsService, allRoutes, riskZones = [];
      let map;

      async function fetchRiskZones() {
        const snapshot = await db.collection("riskareas").get();
        riskZones = snapshot.docs.map(doc => {
          const data = doc.data();
          if (data.Pos && data.Pos.length === 2) {
            return { lat: data.Pos[0], lng: data.Pos[1] };
          }
          return null;
        }).filter(Boolean);
      }

      function drawRiskMarkers() {
        riskZones.forEach(zone => {
          new google.maps.Circle({
            strokeColor: "#FF0000",
            strokeOpacity: 0.8,
            strokeWeight: 1,
            fillColor: "#FF0000",
            fillOpacity: 0.35,
            map,
            center: zone,
            radius: 100
          });
        });
      }

      async function initMap() {
        const origin = document.getElementById("origin").value;
        const destination = document.getElementById("destination").value;
        if (!origin || !destination) {
          alert("Saisir origine et destination.");
          return;
        }

        await fetchRiskZones();

        if (!directionsRenderer) {
          map = new google.maps.Map(document.getElementById("map"), {
            zoom: 7,
            center: { lat: 48.8566, lng: 2.3522 }
          });
          directionsService = new google.maps.DirectionsService();
          directionsRenderer = new google.maps.DirectionsRenderer({ map });
        }

        const request = {
          origin: origin,
          destination: destination,
          travelMode: 'DRIVING',
          provideRouteAlternatives: true
        };

        directionsService.route(request, (result, status) => {
          if (status === 'OK') {
            const routesWithScore = result.routes.map((route, index) => {
              const path = google.maps.geometry.encoding.decodePath(route.overview_polyline.points);
              let riskCount = 0;
              path.forEach(point => {
                riskZones.forEach(zone => {
                  const d = google.maps.geometry.spherical.computeDistanceBetween(point, new google.maps.LatLng(zone.lat, zone.lng));
                  if (d < 100) riskCount++;
                });
              });
              return { route, index, riskCount };
            }).sort((a, b) => a.riskCount - b.riskCount);

            allRoutes = routesWithScore.map(r => r.route);
            directionsRenderer.setDirections({ routes: allRoutes });
            directionsRenderer.setRouteIndex(routesWithScore[0].index);
            populateSelector(routesWithScore);
            drawRiskMarkers();
            alert(`Itinéraire le plus sûr sélectionné automatiquement : ${routesWithScore[0].riskCount} zones à risque.`);
          } else {
            alert("Erreur Google Maps : " + status);
          }
        });
      }

      function populateSelector(routes) {
        const selector = document.getElementById("routeSelector");
        selector.style.display = "block";
        selector.innerHTML = "";
        routes.forEach((r, i) => {
          const opt = document.createElement("option");
          opt.value = r.index;
          opt.text = `Itinéraire ${i + 1} - ${r.route.legs[0].distance.text}, ${r.route.legs[0].duration.text} - Zones : ${r.riskCount}`;
          selector.appendChild(opt);
        });
      }

      function changeRoute() {
        const idx = parseInt(document.getElementById("routeSelector").value);
        directionsRenderer.setRouteIndex(idx);
      }
    </script>
  </body>
</html>
"""

with open("itineraire_form.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ HTML interactif créé.")