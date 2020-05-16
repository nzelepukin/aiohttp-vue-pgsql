var app = new Vue({
	el: "#switchbase",
	data: {
		search: "",
		importState: "",
		url: "/data/",
		selectMode: "multi",
		headVariant: "dark",
		currentPage: 1,
		totalRows: 1,
		perPage: 20,
		all_fields: [
			{key: 'index',label: '#', type: 'service', count: 1},
			{key: 'protocol',label: 'Протокол',type: 'select',default_value: '',sortable: true, count: 2},
			{key: 'ip',label: 'IP адрес', type: 'select',default_value: '',sortable: true, count: 3},
            {key: 'hostname',label: 'Имя', type: 'select',default_value: '', count: 4},
            {key: 'serial',label: 'Серийный номер', type: 'select',default_value: '', count: 5},
			{key: 'model',label: 'Модель', type: 'select', default_value: '', sortable: true, count: 6},
			{key: 'dev_ios',label: 'Версия ПО', type: 'select',default_value: '', sortable: true, count: 7},
			{key: 'description',label: 'Описание', type: 'select',default_value: '', count: 8},			
			{key: 'project',label: 'Проект', type: 'select', default_value: '',sortable: true, count: 9},	
			{key: 'in_date',label: 'Дата ввода', type: 'date', default_value: '01.01.1900',sortable: true, count: 10},
			{key: 'power',label: 'Мощность', type: 'service', count: 11},
			{key: 'power_type',label: 'Эл. питание',type: 'select', default_value: '', sortable: true, count: 12},
			{key: 'type',label: 'Тип', type: 'select',default_value: '', count: 13},			
			{key: 'place',label: 'Объект', type: 'select',default_value: '',sortable: true, count: 14},
            {key: 'building',label: 'Здание', type: 'select',default_value: '', count: 15},
			{key: 'room',label: 'Комната', type: 'select',default_value: '', count: 16},	
			{key: 'selected',label: '', type: 'service', count: 100}		        
	],
		switches_fields: [ ],
		selected: [],
		switches: [],
		editParameters: [],
		file: ""
	},
	created: 
		function() {
			this.switches_fields=[
				{key: 'index',label: '#', type: 'service', count: 1},
				{key: 'ip',label: 'IP адрес', type: 'select',default_value: '',sortable: true, count: 3},
				{key: 'hostname',label: 'Имя', type: 'select',default_value: '', count: 4},
				{key: 'serial',label: 'Серийный номер', type: 'select',default_value: '', count: 5},
				{key: 'model',label: 'Модель', type: 'select', default_value: '', sortable: true, count: 6},
				{key: 'dev_ios',label: 'Версия ПО', type: 'select',default_value: '', sortable: true, count: 7},
				{key: 'place',label: 'Объект', type: 'select',default_value: '',sortable: true, count: 14},
				{key: 'selected',label: '', type: 'service', count: 100}	        
		];
			fetch(this.url+'switch/', {
				mode : "no-cors", 
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
				this.switches = data;
				this.totalRows = this.switches.length
			 });					
	},

	methods: {
		snmpinfo() {
			console.log(JSON.stringify(this.selected));
			fetch(this.url+"snmpinfo/", {
				mode : "no-cors", 
				method : "POST",
				headers : {"Content-Type" : "application/json; charset=utf-8"},
				body : JSON.stringify(this.selected)
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				fetch(this.url+'switch/', {
					mode : "no-cors", 
					method : "GET"
				}
				).then(response => response.json()).then(data => { this.switches = data })
			})

		},	
		handleFileUpload(){
			this.file = this.$refs.file.files[0];
			console.log(this.file);
			this.importState="Загрузка файла ..."
			let formData = new FormData();
			formData.append('file', this.file);
			fetch(this.url+"xlstobase/", {
				mode : "no-cors", 
				method : "POST",
				body: formData
			}
			).then(response => response.json()).then(data => {
				console.log(data);
				this.importState="Файл загружен, необходимо обновить страницу";
				fetch(this.url+"switch/", {
					mode : "no-cors", 
					method : "GET"
				}).then(response => response.json()).then(data => { this.switches = data;})
			});
		},
		onRowSelected(switches) {
			this.selected = switches;
		  },
		selectAllRows() {
			this.$refs.selectableTable.selectAllRows()
		  },
		clearSelected() {
			this.$refs.selectableTable.clearSelected()
		  },
		AddDevice() {
			var new_device = {};
			this.all_fields.forEach(element => {
				if (element.type==='service') {}
				else { 
				new_device[element.key]=document.getElementById('new-'+element.key).value;
				}
			})
			fetch(this.url+"switch/", {
				mode : "no-cors", 
				method : "POST",
				headers : {"Content-Type" : "application/json; charset=utf-8"},
				body : JSON.stringify(new_device)
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				fetch(this.url+'switch/', {
					mode : "no-cors", 
					method : "GET"
				}
				).then(response => response.json()).then(data => { this.switches = data })
			})
		},
		devOptions(param) {
			var output=[];
			var options =[];
			this.switches.forEach(element => {
				output.push(element[param])
			}
			);
			output = new Set(output);
			output.forEach(element => { 
				options.push( element)
			})
			return options
		},
		DeleteDevice() {
			var del_array = [];
			this.selected.forEach(element => {
				del_array.push(element.id)
			});
			fetch(this.url+"switch/"+del_array.join("+"), {
				method : "DELETE"
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				fetch(this.url+'switch/', {
					mode : "no-cors", 
					method : "GET"
				}
				).then(response => response.json()).then(data => { this.switches = data })
			})
		},
		GetSelectedDevice(){
			var tmp=Object.assign({},this.selected[0]);
			if (this.selected.length>0) {
				this.all_fields.forEach( element =>
					{
						if (element.type!=='service') {
							element.default_value=tmp[element.key];
						}
					}
				)
			};
		},
		EditDevice(){
			var output = []
			var tmp = {}
			if (this.selected.length>0) {
				this.selected.forEach( element => output.push({id: element.id}));
				this.editParameters.forEach(element=>(
					tmp[element]=document.getElementById('edit-'+element).value )); 
				output.forEach(element=>{
					for (var prop in tmp) {
						element[prop]=tmp[prop]
					}
				})   
				fetch(this.url+"edit-switch/", {
					mode : "no-cors", 
					method : "POST",
					headers : {"Content-Type" : "application/json; charset=utf-8"},
					body : JSON.stringify(output)
				}
				).then(response => response.json()).then(data => { 
					console.log(data); 
					fetch(this.url+'switch/', {
						mode : "no-cors", 
						method : "GET"
					}
					).then(response => response.json()).then(data => { this.switches = data })
				})
			}
		},
		onFiltered(filteredItems) {
			// Trigger pagination to update the number of buttons/pages due to filtering
			this.totalRows = filteredItems.length
			this.currentPage = 1
		  },
		compare: function(a, b) {
			if (a.count > b.count) {
			  return 1;
			}
			if (a.count < b.count) {
			  return -1;
			}
			// a должно быть равным b
			return 0;
		  }
	},
	computed: {

	  }
})
