var app = new Vue({
	el: "#switchbase",
	data: {
		userinfo: {username:'',password:'',role:'',firstname:'',lastname:'',email:''},
		search: "",
		importState: "",
		url: "/data/",
		selectMode: "multi",
		headVariant: "dark",
		currentPage: 1,
		totalRows: 1,
		perPage: 100,
		all_fields: [
			{key: 'index',label: '#', type: 'service', count: 1},
			{key: 'protocol',label: 'Протокол',type: 'select',default_value: '',sortable: true, count: 2},
			{key: 'ip',label: 'IP адрес', type: 'select',default_value: '',sortable: true, count: 3},
            {key: 'hostname',label: 'Имя', type: 'select',default_value: '', count: 4},
            {key: 'serial_n',label: 'Серийный номер', type: 'select',default_value: '', count: 5},
			{key: 'model',label: 'Модель', type: 'select', default_value: '', sortable: true, count: 6},
			{key: 'dev_ios',label: 'Версия ПО', type: 'select',default_value: '', sortable: true, count: 7},
			{key: 'description',label: 'Описание', type: 'select',default_value: '', count: 8},			
			{key: 'project',label: 'Проект', type: 'select', default_value: '',sortable: true, count: 9},	
			{key: 'in_date',label: 'Дата ввода', type: 'date', default_value: '01.01.1900',sortable: true, count: 10},
			{key: 'power',label: 'Мощность', type: 'service', count: 11},
			{key: 'power_type',label: 'Эл. питание',type: 'select', default_value: '', sortable: true, count: 12},
			{key: 'switch_type',label: 'Тип', type: 'select',default_value: '', count: 13},			
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
				{key: 'serial_n',label: 'Серийный номер', type: 'select',default_value: '', count: 5},
				{key: 'model',label: 'Модель', type: 'select', default_value: '', sortable: true, count: 6},
				{key: 'dev_ios',label: 'Версия ПО', type: 'select',default_value: '', sortable: true, count: 7},
				{key: 'place',label: 'Объект', type: 'select',default_value: '',sortable: true, count: 14},
				{key: 'selected',label: '', type: 'service', count: 100}	        
		];
			fetch(this.url+'user', {
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
				console.log(data);
				this.userinfo = data;
			 });		
			fetch(this.url+'device', {
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
				this.switches = data;
				this.totalRows = this.switches.length
			 });					
	},

	methods: {
		snmpinfo() {
			fetch(this.url+"snmpinfo", { 
				method : "PATCH",
				headers : {"Content-Type" : "application/json; charset=utf-8"},
				body : JSON.stringify(this.selected)
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				Promise.all(data.map(element=>
					fetch(this.url+"device", {
						method : "PATCH",
						headers : {"Content-Type" : "application/json; charset=utf-8"},
						body : JSON.stringify(element)
					}
					).then(response => response.json())
				)).then(data=> {
					console.log(data);
					fetch(this.url+'device', {
						method : "GET"
					}
				).then(response => response.json()).then(data => { this.switches = data })
				})
			})
		},	
		handleFileUpload(){
			this.file = this.$refs.file.files[0];
			console.log(this.file);
			this.importState="Загрузка файла ..."
			let formData = new FormData();
			formData.append('file', this.file);
			fetch(this.url+"xlstobase", { 
				method : "POST",
				body: formData
			}
			).then(response => response.json()).then(data => {
				Promise.all(data.map(element=>
					fetch(this.url+"device", {
						method : "POST",
						headers : {"Content-Type" : "application/json; charset=utf-8"},
						body : JSON.stringify(element)
					}
					).then(response => response.json())
				)).then(data=> {
					console.log(data);
					fetch(this.url+'device', {
						method : "GET"
					}
				).then(response => response.json()).then(data => { this.switches = data })
				});
				this.importState="Файл загружен,";
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
					if ( document.getElementById('new-'+element.key).value!='') {
				new_device[element.key]=document.getElementById('new-'+element.key).value;}
				}
			});
			console.log(new_device);
			fetch(this.url+"device", {
				method : "POST",
				headers : {"Content-Type" : "application/json; charset=utf-8"},
				body : JSON.stringify(new_device)
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				fetch(this.url+'device', {
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
				del_array.push(element.dev_id)
			});
			fetch(this.url+"device/"+del_array.join("+"), {
				method : "DELETE"
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				fetch(this.url+'device', {
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
				this.selected.forEach( element => output.push({dev_id: element.dev_id}));
				this.editParameters.forEach(element=>(
					tmp[element]=document.getElementById('edit-'+element).value )); 
				output.forEach(element=>{
					for (var prop in tmp) {
						element[prop]=tmp[prop]
					}
				});
				Promise.all(output.map(element=>
					fetch(this.url+"device", {
						method : "PATCH",
						headers : {"Content-Type" : "application/json; charset=utf-8"},
						body : JSON.stringify(element)
					}
					).then(response => response.json())
				)).then(data=> {
					console.log(data);
					fetch(this.url+'device', {
						method : "GET"
					}
				).then(response => response.json()).then(data => { this.switches = data })
				})
			}
		},
		logout() {
			window.location.href = this.url+'logout';
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
