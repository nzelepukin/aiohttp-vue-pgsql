var app = new Vue({
	el: "#switchbase",
	data: {
		userinfo: {username:'',password:'',role:'',firstname:'',lastname:'',email:'',columns:'',search:''},
		search: "",
		importState: "",
		url: "/data/",
		selectMode: "multi",
		headVariant: "dark",
		currentPage: 1,
		totalRows: 1,
		perPage: 100,
		edit_fields: [
			{key:'label', label: 'Имя поля'},
			{key: 'visible', label: "Отобажается"},
			{key: 'search', label: "Поиск"},
		],
		all_fields: [
			{key: 'index',label: '#', type: 'service', count: 1, display: false},
			{key: 'protocol',label: 'Протокол',type: 'select',default_value: '',sortable: true, count: 2, display: true},
			{key: 'ip',label: 'IP адрес', type: 'select',default_value: '',sortable: true, count: 3, display: true},
            {key: 'hostname',label: 'Имя', type: 'select',default_value: '',sortable: true, count: 4, display: true},
            {key: 'serial_n',label: 'Серийный номер', type: 'select',default_value: '', count: 5, display: true},
			{key: 'model',label: 'Модель', type: 'select', default_value: '', sortable: true, count: 6, display: true},
			{key: 'dev_ios',label: 'Версия ПО', type: 'select',default_value: '', sortable: true, count: 7, display: true},
			{key: 'description',label: 'Описание', type: 'select',default_value: '', count: 8, display: true},			
			{key: 'project',label: 'Проект', type: 'select', default_value: '',sortable: true, count: 9, display: true},	
			{key: 'in_date',label: 'Дата ввода', type: 'date', default_value: '01.01.1900',sortable: true, count: 10, display: true},
			{key: 'power',label: 'Мощность', type: 'service', count: 11, display: true},
			{key: 'power_type',label: 'Эл. питание',type: 'select', default_value: '', sortable: true, count: 12, display: true},
			{key: 'switch_type',label: 'Тип', type: 'select',default_value: '', count: 13, display: true},			
			{key: 'place',label: 'Объект', type: 'select',default_value: '',sortable: true, count: 14, display: true},
            {key: 'building',label: 'Здание', type: 'select',default_value: '', count: 15, display: true},
			{key: 'room',label: 'Комната', type: 'select',default_value: '', count: 16, display: true},	
			{key: 'selected',label: '', type: 'service', count: 100, display: false}		        
	],
		selected: [],
		devices: [],
		device_fields: [],
		editParameters: [],
		file: "",
		// for models and users
		modal_fields: [],
		modal_search: "",
		modal_items: [],
		user_pass1: "",
		user_pass2: "",
		// multiconsole vriables
		mc_username: "",
		mc_password: "",
		mc_ip: "",
		mc_cli: "",
		mc_results:[ {ip:"IP", output:[["Пожалуйста заполните форму и нажмите Выполнить "]] } ]
	},
	created: 
		function() {
			var tmp=Object ;
			fetch(this.url+'user', {
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
				this.userinfo = data;
				this.userinfo.columns.forEach(element=>
					this.device_fields.push(this.all_fields.find(item=>item.key==element))
				);
			 });


			fetch(this.url+'device', {
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
				this.devices = data;
				this.totalRows = this.devices.length
			 });					
	},

	methods: {
		// Start MULTICONSOLE block
		GetMC () {
			// Fills multiconsole inputs with username and IPs
			this.mc_username = this.userinfo.username;
			if (this.selected.length>0) {
				this.mc_ip=this.selected.map(element => element.ip).join("\n");
			};
		},
		multicon() {
			// Multiconsole main func
			fetch("data/multiconsole", {
				method : "POST",
				headers : ({"Content-Type" : "application/json; charset=utf-8"}),
				body : JSON.stringify({
					"command" : this.mc_cli, 
					"username" : this.mc_username, 
					"password" : this.mc_password, 
					"ip" : this.mc_ip })
			}
			).then(response => response.json()).then(data => { this.mc_results = data })			
			}, // End of MULTICONSOLE block
		snmpinfo() {
			// Fill hostname, model, serial, ios with information from device (SNMP) 
			fetch(this.url+"snmpinfo", { 
				method : "PATCH",
				headers : {"Content-Type" : "application/json; charset=utf-8"},
				body : JSON.stringify(this.selected)
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				fetch(this.url+'device', {
					method : "GET"
				}
				).then(response => response.json()).then(data => { this.devices = data })
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
				).then(response => response.json()).then(data => { this.devices = data })
				});
				this.importState="Файл загружен,";
			});
		},

		AddDevice() {
			// Normalize information about new device, send it to BACKEND.
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
				this.devices.push(data)
			})
		},
		DeleteDevice() {
			this.selected.forEach(element => {
				fetch(this.url+"device/"+element.dev_id, {
					method : "DELETE"
				}
				).then(response => response.json()).then(data => {
					console.log(data);
					this.devices.splice(this.devices.indexOf(element),1);
				})
			});

		},
		EditDevice(){
			var output = []
			var tmp = {}
			if (this.selected.length>0) {
				this.selected.forEach( element => output.push(
					{dev_id: element.dev_id}));
				this.editParameters.forEach(element=>(
					tmp[element]=document.getElementById('edit-'+element).value
					)); 
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
					).then(response => response.json().then(data =>{
						this.devices.splice(this.devices.indexOf(element),1,data);
					} ))
				))
			}
		},
		devOptions(param) {
			var output=[];
			var options =[];
			this.devices.forEach(element => {
				output.push(element[param])
			});
			output = new Set(output);
			output.forEach(element => { 
				options.push( element)
			})
			return options
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

		// Start of M-O-D-E-L block
		GetModels() {
			// Get from backend information about existing models
			this.modal_fields = [
				{key: 'index',label: '#', type: 'service'},
				{key: 'model',label: 'Модель',type: 'select',default_value: '',sortable: true},
				{key: 'rec_ios',label: 'Версия ПО', type: 'select',default_value: ''},
				{key: 'power',label: 'Мощность', type: 'select',default_value: ''},	
				{key: 'selected',label: '', type: 'service'}] ;
			fetch(this.url+'model', { 
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
				console.log(data);
				this.modal_items = data;
				this.totalRows = this.modal_items.length
			 })
		},	
		DeleteModel() {
			var del_array = [];
			this.selected.forEach(element => {
				fetch(this.url+"model/"+element.model_id, {
					method : "DELETE"
				}
				).then(response => response.json()).then(data => { 
					console.log(data); 
					this.modal_items.splice(this.modal_items.indexOf(element),1);
			})});
		},
		EditModel(){
			Promise.all(this.selected.map(element=>
				fetch(this.url+"model", {
					method : "PATCH",
					headers : {"Content-Type" : "application/json; charset=utf-8"},
					body : JSON.stringify(element)
				}
				).then(response => response.json()).then(data=>{
					console.log(data);
					this.modal_items.splice(this.modal_items.indexOf(element),1,data);
				})))
		}, 
		CloseModels() {
			fetch(this.url+'device', {
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
				this.devices = data;
				this.totalRows = this.devices.length
			 });
			this.$bvModal.hide('modal-model')
		}, 
		// End of M-O-D-E-L block
		// Start of USER block
		GetUsers() {
			this.selected = [];
			this.modal_fields = [
				{key: 'index',label: '#', type: 'service'},
				{key: 'username',label: 'Username',type: 'text',default_value: this.userinfo.username,sortable: true},
				{key: 'role',label: 'Роль', type: 'select',default_value: this.userinfo.role},
				{key: 'firstname',label: 'Имя', type: 'text',default_value: this.userinfo.firstname},
				{key: 'lastname',label: 'Фамилия', type: 'text',default_value: this.userinfo.lastname},
				{key: 'email',label: 'Электронная почта', type: 'text',default_value: this.userinfo.email},
				{key:  'password', label: '', type: 'service'},	
				{key: 'selected',label: '', type: 'service'}] ;
			fetch(this.url+'userbase', { 
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
				console.log(data);
				this.modal_items = data;
				this.totalRows = this.modal_items.length
			 })
		},	
		DeleteUser() {
			this.selected.forEach(element => {
				fetch(this.url+"userbase/"+element.user_id, {
					method : "DELETE"
				}
				).then(response => response.json()).then(data=> {
					console.log(data);
					this.modal_items.splice(this.modal_items.indexOf(element),1);
				})
			});
		},
		EditUserBase(){
			Promise.all(this.selected.map(element=>{ 
				console.log(element);
				fetch(this.url+"userbase", {
					method : "PATCH",
					headers : {"Content-Type" : "application/json; charset=utf-8"},
					body : JSON.stringify(element)
				}
				).then(response => response.json()).then(data=>{
					console.log(data);
					this.modal_items.splice(this.modal_items.indexOf(element),1,data);
				})}))
		},
		AddUser(passwd,passwd2){
			var new_user = {};
			if (passwd === passwd2) {
				this.modal_fields.forEach(element => {
					if (element.type==='service') {}
					else { 
						if ( document.getElementById('new-user'+element.key).value!='') {
					new_user[element.key]=document.getElementById('new-user'+element.key).value;}
					}
				});
				new_user.password=passwd
				fetch(this.url+"userbase", {
					method : "POST",
					headers : {"Content-Type" : "application/json; charset=utf-8"},
					body : JSON.stringify(new_user)
				}
				).then(response => response.json()).then(data => { 
					console.log(data); 
					this.modal_items.push(data)
				})
			}
		},
		EditUser(passwd,passwd2){
			var user = {user_id:this.userinfo.user_id};
			this.modal_fields.forEach(element => {
				if (element.type==='service') {}
				else { 
					if ( document.getElementById('edit-user'+element.key).value!='') {
				user[element.key]=document.getElementById('edit-user'+element.key).value;}
				}
			});
			if (passwd == passwd2 & passwd != "") {user.password=passwd};
			fetch(this.url+"user", {
				method : "PATCH",
				headers : {"Content-Type" : "application/json; charset=utf-8"},
				body : JSON.stringify(user)
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				userinfo=data;
			})
		},
		SaveUserSettings() {
			var tmpArr=[];
			this.device_fields.forEach(element=>{ tmpArr.push(element.key)})
			this.userinfo.columns=tmpArr;
			fetch(this.url+"user", {
				method : "PATCH",
				headers : {"Content-Type" : "application/json; charset=utf-8"},
				body : JSON.stringify(this.userinfo)
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				this.userinfo=data;
			})
			this.$bvModal.hide('user-settings')
		}, 
		ErasePass(user){
				user['password']="e10adc3949ba59abbe56e057f20f883e";
				console.log(user);
				fetch(this.url+"userbase", {
					method : "PATCH",
					headers : {"Content-Type" : "application/json; charset=utf-8"},
					body : JSON.stringify(user)
				}
				).then(response => response.json()).then(data=>{
					console.log(data);
				})
		},
		logout() {
			window.location.href = this.url+'logout';
		},
		// End of USER block
		onRowSelected(devices) {
			this.selected = devices;
		  },
		selectAllRows() {
			this.$refs.selectableTable.selectAllRows()
		  },
		clearSelected() {
			this.$refs.selectableTable.clearSelected()
		  },
		onFiltered(filteredItems) {
			// Trigger pagination to update the number of buttons/pages due to filtering
			this.totalRows = filteredItems.length
			this.currentPage = 1
		  }
	},
	computed: {
		FilterConsole() {
			return this.mc_results.filter(result => {
				if (result.ip.includes(this.modal_search)) {
				  return result.ip.includes(this.modal_search);
				} else {
				  return result.output[0][0].toLowerCase().includes(this.modal_search.toLowerCase());
				} 
			})
		  },
		PassState() {
			if (this.user_pass1 === this.user_pass2 & this.user_pass1 != '') { return true}
			else {return false}
		 },
		SortedDevFields () {
			return this.device_fields.sort(function(a, b){return a.count - b.count})
		}

	  }
})
