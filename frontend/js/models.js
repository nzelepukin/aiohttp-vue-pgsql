var app = new Vue({
	el: "#models",
	data: {
		userinfo: {username:'',password:'',role:'',firstname:'',lastname:'',email:''},
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
			{key: 'model',label: 'Модель',type: 'select',default_value: '',sortable: true},
			{key: 'rec_ios',label: 'Версия ПО', type: 'select',default_value: ''},
            {key: 'power',label: 'Мощность', type: 'select',default_value: ''},	
			{key: 'selected',label: '', type: 'service'}],
		models_fields: [],
		selected: [],
		models: []
	},
	created: 
		function() {
			fetch(this.url+'user', {
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
				console.log(data);
				this.userinfo = data;
			 });
			fetch(this.url+'model', { 
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
				console.log(data);
				this.models = data;
				this.totalRows = this.models.length
			 });					
	},

	methods: {	
		onRowSelected(models) {
			this.selected = models;
		  },
		selectAllRows() {
			this.$refs.selectableTable.selectAllRows()
		  },
		clearSelected() {
			this.$refs.selectableTable.clearSelected()
		  },
		DeleteModel() {
			var del_array = [];
			this.selected.forEach(element => {
				del_array.push(element.model_id)
			});
			fetch(this.url+"model/"+del_array.join("+"), {
				method : "DELETE"
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				fetch(this.url+'model', {
					method : "GET"
				}
				).then(response => response.json()).then(data => { this.models = data })
			})
		},
		EditModel(){
			Promise.all(this.selected.map(element=>
				fetch(this.url+"model", {
					method : "PATCH",
					headers : {"Content-Type" : "application/json; charset=utf-8"},
					body : JSON.stringify(element)
				}
				).then(response => response.json()))).then(data => { 
					console.log(data); 
					fetch(this.url+'model', {
						method : "GET"
					}
					).then(response => response.json()).then(data => { this.models = data })
				})
		},
		onFiltered(filteredItems) {
			// Trigger pagination to update the number of buttons/pages due to filtering
			this.totalRows = filteredItems.length;
			this.currentPage = 1
		}
	},
	computed: {

	  }
})
