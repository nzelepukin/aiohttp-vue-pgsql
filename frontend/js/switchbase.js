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
			{key: 'index',label: '#', type: 'service'},
			{key: 'protocol',label: 'Протокол',type: 'select',default_value: '',sortable: true},
			{key: 'ip',label: 'IP адрес', type: 'select',default_value: '',sortable: true},
            {key: 'hostname',label: 'Имя', type: 'select',default_value: ''},
            {key: 'serial',label: 'Серийный номер', type: 'select',default_value: ''},
			{key: 'model',label: 'Модель', type: 'select', default_value: '', sortable: true},
			{key: 'dev_ios',label: 'Версия ПО', type: 'select',default_value: '', sortable: true},
			{key: 'description',label: 'Описание', type: 'select',default_value: ''},			
			{key: 'project',label: 'Проект', type: 'select', default_value: '',sortable: true},	
			{key: 'in_date',label: 'Дата ввода', type: 'date', default_value: '01.01.1900',sortable: true},
			{key: 'power',label: 'Мощность', type: 'service'},
			{key: 'power_type',label: 'Эл. питание',type: 'select', default_value: '', sortable: true},
			{key: 'type',label: 'Тип', type: 'select',default_value: ''},			
			{key: 'place',label: 'Объект', type: 'select',default_value: '',sortable: true},
            {key: 'building',label: 'Здание', type: 'select',default_value: ''},
			{key: 'room',label: 'Комната', type: 'select',default_value: ''},	
			{key: 'selected',label: '', type: 'service'}		        
	],
		switches_fields: [],
		selected: [],
		switches: [],
		editParameters: [],
		file: ""
	},
	created: 
		function() {
			this.switches_fields=[
				{key: 'index',label: '#'},
				{key: 'ip',label: 'IP адрес',sortable: true},
				{key: 'hostname',label: 'Имя'},
				{key: 'serial',label: 'Серийный номер'},
				{key: 'model',label: 'Модель',sortable: true},
				{key: 'dev_ios',label: 'Версия ПО',sortable: true},
				{key: 'place',label: 'Объект',sortable: true},
				{key: 'selected',label: ''}		        
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
		snmpinfo: function() {
			var ip_array = [];
			this.selected.forEach(element => {
				ip_array.push({id: element.id, ip: element.ip})
			})
			console.log(JSON.stringify(ip_array));
			fetch(this.url+"snmpinfo/", {
				mode : "no-cors", 
				method : "POST",
				headers : {"Content-Type" : "application/json; charset=utf-8"},
				body : JSON.stringify(ip_array)
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
		handleFileUpload:function(){
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
	},
	computed: {

	  }
})
