
var app = new Vue({
	el: "#app",
	delimiters: ['[[', ']]'],
	data : {
		idKey: '',
		passwordKey: '',
		users: [],
	},
	created: function () {
		const button = document.querySelector("#button");
		const gif_camion = document.querySelector("#gif_camion")
		button.style.display = "flex";
		gif_camion.style.display = "none";
	},
	methods: {
		Chargement: function () {
			if (document.querySelector("#id_username").value != '' && document.querySelector("#id_password").value != '') {
				button.style.display = "none";
				gif_camion.style.display = "flex";
			}
			else {
				alert("Username or Password Manquant");
            }
		}
	},
	
	
})