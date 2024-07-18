function exportGridAsMatrix() {
    var gridMatrix = {};
    var items = grid.engine.nodes;

    items.forEach(function(item) {
        var x = item.x;
        var y = item.y;
        var id = item.id;
        var cell = {x: x, y: y};
        gridMatrix[id] = cell;
    });

    console.log('Grid Matrix:', gridMatrix);
    return gridMatrix;
};

function importGridFromJSON(configuration) {
    grid.removeAll();
    controllerIds = [];
    console.log('Importing grid from JSON:', configuration);
    for (var key in configuration) {
        var cell = configuration[key];
        var itemHtml = `
        <div class="unavailable grid-stack-item-content">
            <button class="delete-button" onclick="deleteWidget('${key}')">&times;</button>
            <br><br>
            <label class="slider-label" for="${key}">${cell.name}</label>
            <input type="range" min="0" max="100" value="50" class="slider" id="${key}">
        </div>`;
        grid.addWidget(itemHtml, {w: 2, h: 2, x: cell.x,y: cell.y,id:key ,noResize: true});
        controllerIds.push(key);
    }
    
}

function areGridItemsRectangular(){
    var gridSize = getGridSize();
    if(getGridCount()==gridSize[0]*gridSize[1]){
        return true;
    }
    return false;
}

function getGridCorners() {
    var items = grid.engine.nodes;
    var minX = Infinity;
    var minY = Infinity;
    var maxX = -Infinity;
    var maxY = -Infinity;
    
    items.forEach(function(item) {
        if (item.x < minX) {
            minX = item.x;
        }
        if (item.y < minY) {
            minY = item.y;
        }
        if (item.x > maxX) {
            maxX = item.x;
        }
        if (item.y > maxY) {
            maxY = item.y;
        }
    });
    
    return [minX, minY, maxX, maxY];
}

function getGridCount(){
    var items = grid.engine.nodes;
    return items.length;
}

function getGridSize() {
    var corners = getGridCorners();
    console.log(corners);
    var minX = corners[0];
    var minY = corners[1];
    var maxX = corners[2];
    var maxY = corners[3];
    var width = (maxX - minX)/2 + 1;
    var height = (maxY - minY)/2 + 1;
    console.log("Width: " + width + " Height: " + height);
    return [width, height];
}

function getControllerNamesAndIds(){
    var controllerList=[];
    var items = grid.engine.nodes;
    items.forEach(function(item){
        controllerList.push({"name":item.id, "id": item.id});
    });
    console.log(controllerList);
    return controllerList;
}

let currentConfiguration = {
    id: null,
    name: null
};

let currentPreset = {
    id: null,
    name: null
};

function showAlert(message, type) {
    var alertHtml = `<div class="alert alert-${type} alert-dismissible fade show warning-custom-alert" role="alert">
                                ${message}
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                             </div>`;
            $('#alert-placeholder').html(alertHtml);
}