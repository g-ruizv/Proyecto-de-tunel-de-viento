function addController(id, controllerName) {
    const postData = {
        name: controllerName
    };

    fetch(`/api/v1/fanWall/controllers/${id}`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function updateController() {
    const controllerSelect = document.getElementById('controllerSelect');
    const controllerValue = document.getElementById('controllerValue').value;
    const selectedControllerId = controllerSelect.value;

    fetch(`/api/v1/fanWall/controllers/${selectedControllerId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: controllerValue }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        console.log('Success:', data);
        $('#controllerModal').modal('hide');
        document.getElementById('updateForm').reset();
    })
    .catch(error => {
        console.error('There was a problem with the PUT operation:', error);
    });
}
function getControllers() {
    fetch('/api/v1/fanWall/controllers')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error){
                showAlert(data.error, "warning");
                return;
            }
            const controllerSelect = document.getElementById('controllerSelect');
            controllerSelect.innerHTML = ''; // Clear previous options
            data.controllers.forEach(controller => {
                const option = document.createElement('option');
                option.value = controller.id;
                option.textContent = controller.name;
                controllerSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

async function getController(id) {
    let controllerData;
    try {
        const response = await fetch(`/api/v1/fanWall/controllers/${id}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        if (data.error) {
            showAlert(data.error, "warning");
            return;
        }
        console.log('Controller:', data);
        controllerData = data;
        console.log(controllerData);
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
    console.log(controllerData);
    return controllerData;
}


function addMultipleControllers() {
    controllerList = getControllerNamesAndIds();
    console.log(controllerList);
    const postData = { "controllers": [] }
    controllerList.forEach(element => {
        let newController = {"name": element.name, "id": element.id};
        postData.controllers.push(newController);
    });
    fetch(`/api/v1/fanWall/addMultipleControllers`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // PRIMERO CONVIERTE A JSON
    })
    .then(data => {
        // AHORA SÍ PUEDES USAR 'data'
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        console.log("Controladores añadidos:", data);
    })
    .catch(error => {
        console.error("Error en addMultipleControllers:", error);
    });
}

function getConfigurations() {
    fetch('/api/v1/fanWall/configurations')
        .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
        })
        .then(data => {
            if (data.error){
                showAlert(data.error, "warning");
                return;
            }
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

function getPresets() {
    fetch('/api/v1/fanWall/presets')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, "warning");
            return;
        }
        const dropdown = document.getElementById('presetDropdown');
        dropdown.innerHTML = '';
        data.presets.forEach(preset => {
            const option = document.createElement('a');
            option.classList.add('dropdown-item');
            option.href = '#';
            option.id = `${preset.id}`;
            option.textContent = `Preset ${preset.name}`;
            // 👇 AÑADE ESTE MANEJADOR
            option.addEventListener('click', (e) => {
                e.preventDefault();
                importPreset(preset.id);
            });
            dropdown.appendChild(option);
        });
    })
    .catch(error => console.error('Error getPresets:', error));
}

function getSameSizePresets(){
    gridSize = getGridSize();
    isRectangular = areGridItemsRectangular();
    if (isRectangular == false){
        console.log('Grid items are not rectangular');
        return;
    }
    fetch(`/api/v1/fanWall/presets/same_size/${gridSize[0]}/${gridSize[1]}`)
        .then(response => {
            if (!response.ok) {
            throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error){
                showAlert(data.error, "warning");
                return;
            }
            const dropdown = document.getElementById('presetDropdown');
            dropdown.innerHTML = ''; // Clear existing options
            console.log(data);
            data.presets.forEach(preset => {
                const option = document.createElement('a');
                option.classList.add('dropdown-item');
                option.href = '#'; // Add link behavior if needed
                console.log(preset);
                option.id = `${preset.id}`;
                option.textContent = `Preset ${preset.name}`;
                dropdown.appendChild(option);
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

}

function createConfiguration(id, configurationName){
    const postData = {
        name: configurationName
    };
    fetch(`/api/v1/fanWall/configurations/${id}`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({name: configurationName})
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function saveConfiguration(){
    console.log('Saving configuration...');
    configurationName= document.getElementById('newConfigurationNameInputBox').value;
    id = null;
    const configurationMatrix = exportGridAsMatrix();
    const postData = {
        name: configurationName,
        controllers: configurationMatrix
    };

    fetch(`/api/v1/fanWall/configurations/create_with_controllers`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response from server:', data);
        currentConfiguration.id = data.id;
        currentConfiguration.name = configurationName;
        document.getElementById('currentConfiguration').textContent = data.name;
        getConfigurations();
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function savePreset(){
    console.log('Saving preset...');
    const presetName = document.getElementById('newPresetNameInputBox').value;
    const presetJSON = JSON.parse(document.getElementById('newPresetJsonInputBox').value);
    const postData = {
        name: presetName,
        data: presetJSON
    };

    fetch(`/api/v1/fanWall/presets`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response from server:', data);
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        
        getConfigurations();
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function updateConfiguration(configurationId){
    console.log('Updating configuration...');
    const configurationMatrix = exportGridAsMatrix();
    const postData = {
        controllers: configurationMatrix
    };
    console.log(postData);

    fetch(`/api/v1/fanWall/configurations/${configurationId}/controllers`, {
        method: 'PATCH',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function importConfiguration(configurationId) {
    console.log('Importing configuration:', configurationId);
    fetch(`/api/v1/fanWall/configurations/${configurationId}/controllers`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, "warning");
                return;
            }
            // data.controllers debe ser una matriz (lista de listas) con los IDs de los controladores
            console.log('Configuration matrix:', data.controllers);
            
            // Guardar la configuración completa
            window.currentConfiguration = {
                id: configurationId,
                name: data.name,
                matrix: data.controllers   // Guardamos la matriz aquí
            };
            
            // Mostrar en la interfaz
            const span = document.getElementById('currentConfiguration');
            if (span) span.textContent = data.name;
            
            // Aplicar la matriz al grid visual
            if (typeof importGridFromJSON === 'function') {
                importGridFromJSON(data.controllers);
            }
        })
        .catch(error => console.error('Error importConfiguration:', error));
}

function importPreset(presetId){
    console.log('Importing preset...', presetId);
    fetch(`/api/v1/fanWall/presets/${presetId}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, "warning");
            return;
        }
        // Guardar en variable global
        window.currentPreset = { id: presetId, name: data.name };
        // Mostrar el nombre en algún lugar (opcional)
        let span = document.getElementById('currentPreset');
        if (span) span.textContent = data.name;
        console.log('Preset cargado:', window.currentPreset);
    })
    .catch(error => console.error('Error importPreset:', error));
}

function runPreset(){
    // Verificar que haya un preset cargado
    if (!window.currentPreset || !window.currentPreset.id) {
        console.error("No preset loaded. Please load a preset first.");
        showAlert("No preset loaded", "warning");
        return;
    }
    // Verificar que haya una configuración cargada
    if (!window.currentConfiguration || !window.currentConfiguration.id) {
        console.error("No configuration loaded. Please load a configuration first.");
        showAlert("No configuration loaded", "warning");
        return;
    }
    startProcedure();
    const url = `/api/v1/fanWall/presets/${window.currentPreset.id}/configuration/${window.currentConfiguration.id}`;
    console.log('Running preset with URL:', url);
    fetch(url)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, "warning");
            return;
        }
        console.log('Preset running response:', data);
    })
    .catch(error => console.error('Error runPreset:', error));
}

function stopPreset(){
    console.log('Stopping preset...');
    fetch(`/api/v1/fanWall/presets/${currentPreset.id}/configuration/${currentConfiguration.id}/stop`)
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        console.log('Response from server:', data);
        stopProcedure()
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}