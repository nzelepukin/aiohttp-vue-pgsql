var app = new Vue({
	el: "#rconsole",
	data: {
        search: "",
		username: "",
		password: "",
		cli: "",
		ip: "192.168.101.3",
		url: "data/multiconsole/",
		results: [ {ip:"IP", output:[["Пожалуйста заполните форму и нажмите Выполнить "]] } ],
	},
	methods: {
		sendip: function() {
			fetch(this.url, {
				mode : "no-cors", 
				method : "POST",
				headers : ({"Content-Type" : "application/json; charset=utf-8"}),
				body : JSON.stringify({"command" : this.cli, "username" : this.username, "password" : this.password, "ip" : this.ip })
			}
			).then(response => response.json()).then(data => { this.results = data })			
			}
	},
	computed: {
		filteredList() {
		  return this.results.filter(result => {
			  if (result.ip.includes(this.search)) {
				return result.ip.includes(this.search);
			  } else {
				return result.output[0][0].toLowerCase().includes(this.search.toLowerCase());
			  } 
		  })
		}
	  }
})
