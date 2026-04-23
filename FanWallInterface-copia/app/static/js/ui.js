var options = {
    cellHeight: '70px',
    cellWidth: '70px',
    column: 12,
    verticalMargin: 10,
    minHeight: 4,
    float: true,
};

var smallGridOptions = {
    staticGrid: true,
    cellHeight: '50px',
    float: true,
    column: 12,
    
};

const MessageType = {
    STATUS_UPDATE: 'status_update',
    COMMAND: 'command',
    ACTIVATE: 'activate',
    CONFIG_UPDATE: 'config_update',
    CONTROLLER_INFORMATION: 'controller_information',
    // Add more message types as needed
};

function createMessage(type, data) {
    return {
        type: type,
        data: data
    };
}

var grid = GridStack.init(options);
var smallGrid = GridStack.init(smallGridOptions, '.grid-stack-sm');
var controllerIds = [];
getConfigurations();
//getPresets();
getSameSizePresets();
updateSliders();
var loadPresetButton = document.getElementById('loadPresetButton');
loadPresetButton.classList.add('disabled');
loadPresetButton.setAttribute('aria-disabled', 'true');

grid.on('dragstop', function(event, element) {
    loadPresetButton.classList.add('disabled');
    loadPresetButton.setAttribute('aria-disabled', 'true');
});


function getValue(id) {
    console.log(id);
    var slider = document.getElementById(id);
    var value = slider.value;
    console.log('Slider value: ' + value);
    //setSpeed(value,id);
    setControllerSpeed(value,id);
}

function copyGridData() {
    var mainGridData = grid.save(false);
    smallGrid.removeAll();
    mainGridData.forEach(function(widget) {
        smallGrid.addWidget({
            x: Math.floor(widget.x / 2),
            y: Math.floor(widget.y / 2),
            w: 1,
            h: 1,
            id: widget.id+"-small",
        });
    });
}

function updateSliders(){
    controllerIds.forEach(function(id){
        addSlider(id);
    });
    updateControllerAvailability("id1", true);
}

function addSlider(id){
    var slider = document.createElement("input");
    slider.type = "range";
    slider.min = "0";
    slider.max = "100";
    slider.value = "50";
    slider.id = "slider";
    slider.onmouseup = function() {
        getValue();
    };
    getController(id).then(function(controller){
        var controllerName = controller.name;
        var itemHtml = `
            <div class="unavailable grid-stack-item-content">
                <button class="delete-button" onclick="deleteWidget('${id}')">&times;</button>
                <br><br>
                <label class="slider-label" for="${id}">${controllerName}</label>
                <input type="range" min="0" max="100" value="50" class="slider" id="${id}">
            </div>`;
        grid.addWidget(itemHtml, {w: 2, h: 2, id:id ,noResize: true});
    });
}

function deleteWidget(id) {
    console.log('Deleting widget:', id);
    grid.removeWidget(document.getElementById(id).closest('.grid-stack-item'));
    controllerIds = controllerIds.filter(function(value, index, arr) {
        return value !== id;
    });
    loadPresetButton.classList.add('disabled');
    loadPresetButton.setAttribute('aria-disabled', 'true');
}

function updateControllerAvailability(sliderId, isAvailable) {
    var sliderElement = document.getElementById(sliderId);
    if (sliderElement) {
        var itemElement = sliderElement.closest('.grid-stack-item');
        if (itemElement) {
            if (isAvailable) {
                itemElement.classList.add('available');
                itemElement.classList.remove('unavailable');
            } else {
                itemElement.classList.add('unavailable');
                itemElement.classList.remove('available');
            }
        }
    }
}

$(document).on('mouseup', '.slider', function() {
    var id = $(this).attr('id');
    getValue(id);

});

$('#loadPresetModal').on('show.bs.modal', function () {
    copyGridData();
});

$('#editControllerModal').on('show.bs.modal', getControllers);

$(document).on('click', '#configDropdown .dropdown-item', function() {
    var id = $(this).attr('id');
    console.log('Configuration selected:', id);
    loadPresetButton.classList.remove('disabled');
    loadPresetButton.setAttribute('aria-disabled', 'false');
    importConfiguration(id);
});
$(document).on('click', '#presetDropdown .dropdown-item', function() {
    var id = $(this).attr('id');
    console.log('Configuration selected:', id);
    importPreset(id);
});

function calculateGradientColor(value, colorA, colorB) {
    var rA = parseInt(colorA.slice(1, 3), 16);
    var gA = parseInt(colorA.slice(3, 5), 16);
    var bA = parseInt(colorA.slice(5, 7), 16);

    var rB = parseInt(colorB.slice(1, 3), 16);
    var gB = parseInt(colorB.slice(3, 5), 16);
    var bB = parseInt(colorB.slice(5, 7), 16);

    var r = Math.round(rA + (rB - rA) * (value / 100));
    var g = Math.round(gA + (gB - gA) * (value / 100));
    var b = Math.round(bA + (bB - bA) * (value / 100));

    return `rgb(${r}, ${g}, ${b})`;
}

// Function to update the color of a small grid widget
function updateSmallGridItemColor(widgetId, value, colorA, colorB) {
    var itemElement = document.getElementById(widgetId);
    if (itemElement) {
        var gradientColor = calculateGradientColor(value, colorA, colorB);
        itemElement.style.backgroundColor = gradientColor;
    }
}
