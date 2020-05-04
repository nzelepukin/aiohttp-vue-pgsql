Vue.component("modal", {
	template: "#modal-template"
  });
var app = new Vue({
	el: "#switchbase",
	data: {
		search: "",
		checkedSwitches: [],
		showModal: false,
		url: "data/switch/",
		headVariant: "dark",
		switches_fields: [
			{
                key: 'ip',
                label: 'IP адрес',
                sortable: true
              },
            {
                key: 'hostname',
                label: 'Имя',
                sortable: true
              },
            {
                key: 'serial',
                label: 'Серийный номер',
                sortable: true
			  },
			  {
                key: 'model',
                label: 'Модель',
                sortable: true
              },
            {
                key: 'dev_ios',
                label: 'Версия ПО',
                sortable: true
			  },
			  {
                key: 'place',
                label: 'Объект',
                sortable: true
              },
            {
                key: 'building',
                label: 'Здание',
                sortable: true
              },      
	],
		switches: [],
		file: ""
	},
	created: 
		function() {
			fetch(this.url, {
				mode : "no-cors", 
				method : "GET"
			}
			).then(response => response.json()).then(data => { this.switches = data });		
	},
	methods: {
		snmpinfo: function() {
			console.log(this.checkedSwitches);
			fetch("/data/snmpinfo/", {
				mode : "no-cors", 
				method : "POST",
				headers : {"Content-Type" : "application/json; charset=utf-8"},
				body : JSON.stringify(this.checkedSwitches)
			}
			).then(response => response.json()).then(data => console.log(data))
			.then(fetch(this.url, {
				mode : "no-cors", 
				method : "GET"
			}
			).then(response => response.json()).then(data => { this.switches = data }))
		},	
		handleFileUpload:function(){
			this.file = this.$refs.file.files[0];
			console.log(this.file);
			let formData = new FormData();
			formData.append('file', this.file);
			return fetch("/data/xlstobase/", {
				mode : "no-cors", 
				method : "POST",
				body: formData
			}
			).then(response => response.json()).then(data => console.log(data))
			.then(fetch(this.url, {
				mode : "no-cors", 
				method : "GET"
			}
			).then(response => response.json()).then(data => { this.switches = data })
		)}
	},
	computed: {
	  }
})
