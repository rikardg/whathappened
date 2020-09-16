console.log("Cthulhu fhtagn!");

type Datamap = {
    field: string,
    subfield?: string | undefined,
    type?: "skillcheck" | "binary" | "area" | "table" | undefined
}

type Elementdata = any;


type Tabledata = any[];


type SaveFunction = (datamap: Datamap | DOMStringMap, data: Elementdata | Tabledata) => void
   

function init_skillchecks() {
    console.log("Init skillchecks");
    const checkboxes: HTMLInputElement[] = Array.from(document.getElementsByTagName('input'));
    checkboxes.forEach(element => {
        if(element.type === "checkbox" && element.getAttribute('data-type') === 'skillcheck') {
            element.onchange = () => {
                //console.log(element.getAttribute('data-field'), element.checked);
                saveCheck(element);
            }
        }
    });
}

function saveCheck(editfield: HTMLInputElement) {
    const value = editfield.checked;
    const datafields: DOMStringMap = editfield.dataset;
    const data = Object.assign({}, datafields);
    //console.log(data, value);
    send_update(data, value);
}

function init_editable_binaries() {
    console.log("Init editable binaries");
    const checkboxes: HTMLInputElement[] = Array.from(document.getElementsByTagName('input'));
    checkboxes.forEach(element => {
        if(element.type === "checkbox" && element.getAttribute('data-type') === 'binary') {
            element.onchange = () => {
                //console.log(element.getAttribute('data-field'), element.checked);
                saveCheck(element);
            }
        }
    });
}

function get_meta_tag(tagname: string): string|undefined {
    const metas = document.getElementsByTagName('meta');
    for(const meta of metas) {
        if(meta.name === tagname)
            return meta.content;
    }
    return undefined;
}

function send_update(datamap: Datamap|DOMStringMap, value: any) {
    const xhr = new XMLHttpRequest()
    const url = document.location.href + 'update';
    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("X-CSRFToken", get_meta_tag('_token'));
    xhr.setRequestHeader('x-csrf-token', get_meta_tag('_token'));
    xhr.onload = () => {
        console.log("Post done");
        console.log(url);
        console.log(xhr.status);
        console.log(xhr.statusText);
    }
    datamap['value'] = value;

    console.log(JSON.stringify(datamap));
    xhr.send(JSON.stringify([datamap, ]));
}




function saveElement(editfield: HTMLInputElement, element: HTMLElement, save: SaveFunction, editable_handler: (e: Event) => void) {
    const value = editfield.value;
    const datafields: DOMStringMap = element.dataset;
    const data = Object.assign({}, datafields);
    
    const field = element.getAttribute('data-field');
    console.log(`Save changes to ${field}, new value ${value}`);
    element.innerHTML = value;
    element.addEventListener("click", editable_handler);
    save(data, value);
}


function editElement(element: HTMLElement, type: "area" | "input", save: SaveFunction, editable_handler: (e: Event) => void) {
    console.log("Edit element");
    const value = element.innerHTML;
    let editfield = null;

    if(type === "input") {
        editfield = document.createElement("input");
    }
    else if(type == "area") {
        editfield = document.createElement('textarea');
    }

    editfield.value = value;

    element.innerHTML = "";
    element.append(editfield);
    editfield.focus();

    editfield.addEventListener("focusout", (e) => {
        saveElement(editfield, element, save, editable_handler);
    })

    editfield.addEventListener("keypress", (e) => {
        if(e.keyCode === 13 && e.ctrlKey === false) {
            saveElement(editfield, element, save, editable_handler);
        }
    })
    
    element.removeEventListener("click", editable_handler);
}


const make_editable_handler = (element: HTMLElement, save: SaveFunction, type: "input" | "area" = "input") => {
    const f = (e: Event) => {
        e.preventDefault();
        editElement(element, type, save, f);
    }

    return f;
}

function make_element_editable(element: HTMLElement, save: SaveFunction, type: "input" | "area"  = "input") {
    const editable_handler = make_editable_handler(element, save, type);
    element.addEventListener("click", editable_handler);
}



function table_to_obj(table: HTMLTableElement): Tabledata {
    let data_rows = [];

    const tableName = table.getAttribute('data-field');
    const fields = Array.from(table.tHead.rows[0].cells).map((element, index) => {
        return {'property': element.getAttribute('data-property'), 'index': index};
    }).filter((element, index) => {
        if(element['property']) return true;
        return false;
    });

    const rows = Array.from(table.tBodies[0].rows);
    for(const row of rows) {
        const row_data = {}
        fields.forEach(field => {
            row_data[field['property']] = row.cells.item(field['index']).innerHTML;
        });

        data_rows.push(row_data);
    }

    return data_rows
}


const editable_table = (table: HTMLTableElement, save: (data: Tabledata) => void) => {
    const make_cell_editable = (cell: HTMLTableCellElement) => {
        make_element_editable(cell, (data: any) => {
            save(table_to_obj(table));
        });
    }
    const make_row_editable = (row: HTMLTableRowElement, fields: any[]) => {
        const cells = Array.from(row.cells);
        //console.log(fields);
        cells.forEach((cell, index) => {
            if(fields.find(field => (field['index'] === index))) {
                make_cell_editable(cell);
            }
        })
    }

    const cells = Array.from(table.tHead.rows[0].cells);
    const fields = cells.map((element, index) => {
        return {'property': element.getAttribute('data-property'), 'index': index};
    }).filter((element, index) => {
        if(element['property']) return true;
        return false;
    });

    const rows =  Array.from(table.tBodies[0].rows);
    for(const row of rows) {
        make_row_editable(row, fields);
    }
    const parent = table.parentElement;
    const button = document.createElement('button');
    button.innerHTML = "Add row";

    button.onclick = () => {
        const new_row = table.insertRow(-1);
        new_row.innerHTML = "<td>-</td>".repeat(cells.length);
        make_row_editable(new_row, fields);
    }

    parent.appendChild(button);
}

const editable_area_handler = function(e: Event) {
    e.preventDefault();
    //editElement(this, "area", (d) => {});
}

function init_editable() {
    console.log("Init editable values");
    const editables: HTMLElement[] = <HTMLElement[]>Array.from(document.getElementsByClassName('editable'));
    
    const save = (datamap: Datamap | DOMStringMap, data: Elementdata|Tabledata) => {
        console.log("Save data");
        console.log(data);
        send_update(datamap, data);
    }

    editables.forEach(element => {
        if(element.getAttribute('data-type') == 'area') {
            make_element_editable(element, save, "area");
        } else {
            make_element_editable(element, save);
        }
    })
}


function init_editable_tables() {
    console.log("Init editable tables");
    const tables: HTMLTableElement[] = <HTMLTableElement[]>Array.from(document.getElementsByClassName('editableTable'));

    tables.forEach(table => {
        editable_table(table, (data: Tabledata) => {
            const field = table.getAttribute('data-field');
            console.log("Saving table.\n"); console.log(data)
            send_update({field: field}, data)
        } );
    });

}


document.addEventListener('DOMContentLoaded', function(event) {
    //the event occurred
    
    init_skillchecks();
    init_editable();
    init_editable_binaries();
    init_editable_tables();
  })
