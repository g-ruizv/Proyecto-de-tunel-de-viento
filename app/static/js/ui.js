var options = {
    cellHeight: 80,
    verticalMargin: 10,
    width: 12,
    minHeight: 4,
    float: true,
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
var controllerIds = ["id1","id2","id3"];
getConfigurations();
updateSliders();

function getValue(id) {
    console.log(id);
    var slider = document.getElementById(id);
    var value = slider.value;
    console.log('Slider value: ' + value);
    //setSpeed(value,id);
    setControllerSpeed(value,id);
}

// Include other UI interaction functions here

$(document).on('mouseup', '.slider', function() {
    var id = $(this).attr('id');
    getValue(id);
});

$(document).on('click', '#configDropdown .dropdown-item', function() {
    // Handle configuration selection
    var id = $(this).attr('id');
    console.log('Configuration selected:', id);
    importConfiguration(id);
});



function getConfigurations() {
    fetch('/api/v1/fanWall/configurations')
        .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
        })
        .then(data => {
            const dropdown = document.getElementById('configDropdown');
            dropdown.innerHTML = ''; // Clear existing options
            console.log(data);
            data.configurations.forEach(configuration => {
                const option = document.createElement('a');
                option.classList.add('dropdown-item');
                option.href = '#'; // Add link behavior if needed
                console.log(configuration);
                option.id = `${configuration.id}`;
                option.textContent = `Configuration ${configuration.name}`;
                dropdown.appendChild(option);
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function updateSliders(){
    controllerIds.forEach(function(id){
        addSlider(id);
    });
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
    var itemHtml = '<div class="square-wrapper"><br><br><label class="slider-label" for="' + id + '">' + id + '</label><input type="range" min="0" max="100" value="50" class="slider" id="' + id + '"></div>';
    grid.addWidget(itemHtml, {w: 2, h: 2, id:id ,noResize: true});
}

$(document).on('mouseup', '.slider', function() {
    var id = $(this).attr('id');
    getValue(id);

});
