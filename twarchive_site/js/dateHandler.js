document.addEventListener('DOMContentLoaded',function() {
    document.getElementById("datepicker").onchange=changeEventHandler;
},false);

async function changeEventHandler(event) {
    // You can use “this” to refer to the selected element.
    if(!event.target.value) document.getElementById('dateLink').href = "#"
    else {
        var d = loadDate();
        document.getElementById("dateLink").href = "#" + d;
        // Load in our data here. based on d (date)
        var dailyData = await loadJSON(function(response) {
            var actual_JSON = JSON.parse(response);
            console.log(actual_JSON);
            var items = Object.keys(actual_JSON).map(function(key) {
                return [key, actual_JSON[key]];
            });
            console.log(items);
            items.sort(function(val1, val2) {
                console.log(val1[1]["appearances"]);
                console.log(val2[1]["appearances"]);
                return (val1[1]["rank"] / (1.0 * val1[1]["appearances"]) - (val2[1]["rank"] / (1.0 * val2[1]["appearances"])))
            });
            console.log("ITEMS AFTER SORT");
            console.log(items);
            //replace this later?
            document.getElementById("todayHead").innerText = d.replace(/_/g,  "/");
            var innerData = "";
            for (var i = 0; i < 10; i++) {
                innerData+= "<p><a href=" + items[i][1]["url"] + ">" + (i+1) + ". " + items[i][0] + "</a></p>";
            }
            document.getElementById("data").innerHTML = innerData;
        }, d);

    };
}

function loadDate() {
    dateAsString = document.getElementById("datepicker").value;
    var newStr = dateAsString.replace(/-/g, '_');
    return newStr;
}

function getData(d) {
    loadJSON(function(response) {
        var actual_JSON = JSON.parse(response);
        console.log(actual_JSON);
        return actual_JSON;
    }, d);
}

function loadJSON(callback, date) {

   var xobj = new XMLHttpRequest();
   xobj.overrideMimeType("application/json");
   xobj.open('GET', 'database/' + date + '.json', true); // Replace 'my_data' with the path to your file
   xobj.onreadystatechange = function () {
         if (xobj.readyState == 4 && xobj.status == "200") {
           // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
           callback(xobj.responseText);
         }
   };
   xobj.send(null);
}
