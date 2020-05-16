var app = new Vue({
	el: "#models",
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
			{key: 'model',label: 'Модель',type: 'select',default_value: '',sortable: true},
			{key: 'ios',label: 'Версия ПО', type: 'select',default_value: ''},
            {key: 'power',label: 'Мощность', type: 'select',default_value: ''},	
			{key: 'selected',label: '', type: 'service'}],
		models_fields: [],
		selected: [],
		models: []
	},
	created: 
		function() {
			fetch(this.url+'model/', {
				mode : "no-cors", 
				method : "GET"
			}
			).then(response => response.json()).then(data => { 
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
				del_array.push(element.id)
			});
			fetch(this.url+"model/"+del_array.join("+"), {
				method : "DELETE"
			}
			).then(response => response.json()).then(data => { 
				console.log(data); 
				fetch(this.url+'model/', {
					mode : "no-cors", 
					method : "GET"
				}
				).then(response => response.json()).then(data => { this.models = data })
			})
		},
		EditModel(){
				fetch(this.url+"model/", {
					mode : "no-cors", 
					method : "POST",
					headers : {"Content-Type" : "application/json; charset=utf-8"},
					body : JSON.stringify(this.selected)
				}
				).then(response => response.json()).then(data => { 
					console.log(data); 
					fetch(this.url+'model/', {
						mode : "no-cors", 
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
