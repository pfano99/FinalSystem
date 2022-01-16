<!DOCTYPE html>
<html>
  <head>
    <title>Add Map</title>

    <style type="text/css">
      #map {
        height: 400px;
        width: 100%;
      }
    </style>
  </head>
  <body>

    <h3>My Google Maps Demo</h3>
    <div id="map"></div>

    <script
      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDV2bOUGX28d0lnalwpl2MVmPHnM8w2jrc&callback=initMap&libraries=&v=weekly"
      async
    ></script>

    <!-- <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false&v=3&libraries=geometry"></script> -->
    <script>
    function initMap(){

      // Map option
  
      var options = {
          center: {lat: -30.5595 , lng:22.9375 },
          zoom: 8
      }
  
      //New Map
      map = new google.maps.Map(document.getElementById("map"),options)
  
      //listen for click on map location
  
      // google.maps.event.addListener(map, "click", (event) => {
      //     //add Marker
      //     addMarker({location:event.latLng});
      // })
  
  
  
      //Marker
  /*
      const marker = new google.maps.Marker({
      position:{lat: 37.9922, lng: -1.1307},
      map:map,
      icon:"https://img.icons8.com/nolan/2x/marker.png"
      });
  
      //InfoWindow
  
      const detailWindow = new google.maps.InfoWindow({
          content: `<h2>Murcia City</h2>`
      });
  
      marker.addListener("mouseover", () =>{
          detailWindow.open(map, marker);
      })
      */
  
  
      let dataArr = [ ]
      addAddressToArr( {{ addresses|safe }} );
  
      // loop through marker
  
      for (let i = 0; i < dataArr.length; i++){
          addMarker(dataArr[i]);
  
      }

      function addAddressToArr(data){
        
        for(let i = 0; i < data.length; i++){
            let f_names = '<h2>' + data[i].f_first_name + ' ' + data[i].f_last_name + '</h2>' ;
            let f_link = '<a href="/farmer/profile/' + data[i].username + '">' + f_names + '</a>';
            let obj = {
                location:{
                  lat: parseFloat(data[i].lat),
                  lng: parseFloat(data[i].lng)
                },
                content: f_link
            }
            dataArr.push(obj);
        }
      }

      // var latLngA = {lat:-26, lng: 28} ;
      // var latLngB = {lat:-33, lng: 18};
      // let distL = google.maps.geometry.spherical.computeDistanceBetween (latLngA, latLngB);
      // console.log(distL)
      // console.log(dataArr)
      

      // Add Marker
      function addMarker(property){
  
          const marker = new google.maps.Marker({
              position:property.location,
              map:map,
              //icon: property.imageIcon
              });
  
              // Check for custom Icon
  
              if(property.imageIcon){
                  // set image icon
                  marker.setIcon(property.imageIcon)
              }
  
              if(property.content){
  
                const detailWindow = new google.maps.InfoWindow({
                content: property.content
                });
      
                marker.addListener("mouseover", () =>{
                    detailWindow.open(map, marker);
                })
            }
  
          
      }
  
  }
  </script>
  </body>
</html>