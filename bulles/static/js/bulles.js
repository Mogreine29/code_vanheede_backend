
// Ici je recupere l'url pour obtenir l'adresse et la mettre dans la barre de recherche et ainsi montrer les bonne bulles
var url = window.location.href;
var url = url.split('/'); //url = ["serverName","app",...,"bb65efd50ade4b3591dcf7f4c693042b"]
var url = url.pop();      //url = "bb65efd50ade4b3591dcf7f4c693042b"
var url = url.replace(/%20/g, " ");
var url = url.replace(/%27/g, "'");
var url = url.replace(/%C3%A9/g, "é");
var url = url.replace(/%C3%A8/g, "è");
var url = url.replace(/%C2%B0/g, "°");
var url = url.replace(/%C3%A2/g, "â");
var url = url.replace(/%C3%A0/g, "à");
var url = url.replace("?", "");




var idsite = "";

var rechercheParAdresse
if (url == "") {
	rechercheParAdresse = "off";
}
else {
	rechercheParAdresse = "on";
}

var app = new Vue({
	el: "#app",
	delimiters: ['[[', ']]'],
	data: {
		searchKey: '',
		bulles: [],
		request: '',
		b: "aaaaa",
		searchKey_S: '',
		sites: [],
	},


	created: function () {
		this.fetchBulles_Sites();
		idsite = "";
	},
	methods: {
		async validation_supprimer(index) {
			//this.bulles1.splice(index,1)
			if (ONSERVER) {
				var fetchAPI = 'https://vanheede.ig.umons.ac.be/api_bulles/' + index + '/'
			} else {
				var fetchAPI = 'http://127.0.0.1:18080/api_bulles/' + index + '/'
			}
			fetch(fetchAPI, {
				method: 'DELETE'
			}).then(response => {
				return response.json()
			}).then(data => console.log("ok")
				// this is the data we get after putting our data,
				// console.log(data)
			);
			this.bulles1.splice(index, 1)
			console.log("pour suppimer.....")
		},
		async validation_supprimer_S(index) {
			//this.bulles1.splice(index,1)
			if (ONSERVER) {
				var fetchAPISites = 'https://vanheede.ig.umons.ac.be/api_sites/' + index + '/'
			} else {
				var fetchAPISites = 'http://127.0.0.1:18080/api_sites/' + index + '/'
			}
			fetch(fetchAPISites, {
				method: 'DELETE'
			}).then(response => {
				return response.json()
			}).then(data2 => console.log("ok")
				// this is the data we get after putting our data,
				// console.log(data)
			);
			this.bulles1.splice(index, 1)
			console.log("pour suppimer.....")
		},
		supprimerBulle: function (num_bulle, id_bulle) {
			var txt;
			if (confirm("êtes-vous sûr de vouloir supprimer la bulle ayant le numéro " + num_bulle + "?")) {
				this.validation_supprimer(id_bulle)
				txt = "suppression enregistrée!";
				//location.reload()
				console.log("suppression enregistrée!")
			} else {
				txt = "You pressed Cancel!";
				console.log("You pressed Cancel!")
			}
			//document.getElementById("demo").innerHTML = txt;
		},
		supprimerSite: function (nom, id_site) {
			var txt;
			if (confirm("êtes-vous sûr de vouloir supprimer le site ayant comme nom " + nom + "?")) {
				this.validation_supprimer2(id_site)
				txt = "suppression enregistrée!";
				//location.reload()
			} else {
				txt = "You pressed Cancel!";
				console.log("id_site=", id_site)
			}
			//document.getElementById("demo").innerHTML = txt;
		},
		suppbulle:function(nom,id_bulle){
			if(confirm("Êtes-vous sûr de vouloir supprimer la bulle : "+nom+" ?")){
				location.replace("/suppbulle/"+ id_bulle);
			}
			else
			{
				
			}
		},
		suppsite:function(nom,id_site){
			if(confirm("Êtes-vous sûr de vouloir supprimer le site : "+nom+" ?")){
				location.replace("/suppsite/"+id_site);
			}
			else
			{

			}
		},
		editsite: function (id_site) {

			if (ONSERVER) {
				var fetchAPI = "https://vanheede.ig.umons.ac.be/update_site/" + id_site
			} else {
				var fetchAPI = "http://127.0.0.1:18080/update_site/" + id_site
			}
			fetch(fetchAPI) // get data via api
				.then(response => response.json()) // transform data into Json
				.then((data) => {
					date = data.date_vidange.substr(0, 10)
					idsite = data.id_site
					document.getElementById("Nom_Modif").value = data.nom; 
					document.getElementById("Id_depot_Modif").value = data.id_depot == 1 ? "Quévy" : "Dottignies";
					document.getElementById("Type_site_Modif").value = data.type_site;
					document.getElementById("longitude_Modif").value = data.longitude;
					document.getElementById("latitude_Modif").value = data.latitude;
					document.getElementById("date_vidange_Modif").value = date;
					
				})
		},

		editsite2: function () {

			let formData = new FormData();

			formData.append('Id_site_M', idsite);
			formData.append('Nom_M', document.getElementById("Nom_Modif").value);
			formData.append('Id_depot_M', document.getElementById("Id_depot_Modif").value);
			formData.append('Type_site_M', document.getElementById("Type_site_Modif").value);
			formData.append('longitude_M', document.getElementById("longitude_Modif").value);
			formData.append('latitude_M', document.getElementById("latitude_Modif").value);
			formData.append('date_vidange_M', document.getElementById("date_vidange_Modif").value);

			if (ONSERVER) {
				var runSimuRequestAPI = 'https://vanheede.ig.umons.ac.be/update_site2/?format=json'
			} else {
				var runSimuRequestAPI = 'http://127.0.0.1:18080/update_site2/?format=json'
			}
			const REQUEST = new Request(runSimuRequestAPI, { method: 'POST', body: formData });
			fetch(REQUEST) 
				.then((data) => {
					window.location.href = window.location.href;
				}).catch((error) => alert(error))


		},

		editbulle: function (id_bulle) {

			if (ONSERVER) {
				var fetchAPI = "https://vanheede.ig.umons.ac.be/update_bin/" + id_bulle
			} else {
				var fetchAPI = "http://127.0.0.1:18080/update_bin/" + id_bulle
			}
			fetch(fetchAPI) // get data via api
				.then(response => response.json()) // transform data into Json
				.then((data) => {

					idbulle = data.id_bulle
					document.getElementById("Nom_Modif").value = data.num_bulle;
					document.getElementById("Type_bulle_Modif").value = data.type_bulle;
					document.getElementById("Colories_Modif").value = data.colories;
					document.getElementById("latitude_Modif").value = data.latitude;
					document.getElementById("longitude_Modif").value = data.longitude;
					document.getElementById("date_vidange_Modif").value = data.date_vidange;
					document.getElementById("Id_depot_Modif").value = data.id_depot == 1 ? "Quévy" : "Dottignies";
					document.getElementById("Id_site_Modif").value = data.id_site;

				})
		},

		editbulle2: function () {

			let formData = new FormData();

			formData.append('Id_bulle_M', idbulle);
			formData.append('Nom_M', document.getElementById("Nom_Modif").value);
			formData.append('Type_bulle_M', document.getElementById("Type_bulle_Modif").value);
			formData.append('Colories_M', document.getElementById("Colories_Modif").value);
			formData.append('latitude_M', document.getElementById("latitude_Modif").value);
			formData.append('longitude_M', document.getElementById("longitude_Modif").value);
			formData.append('date_vidange_M', document.getElementById("date_vidange_Modif").value);
			formData.append('Id_depot_M', document.getElementById("Id_depot_Modif").value);
			formData.append('Id_site_M', document.getElementById("Id_site_Modif").value);

			if (ONSERVER) {
				var runSimuRequestAPI = 'https://vanheede.ig.umons.ac.be/update_bin2/?format=json'
			} else {
				var runSimuRequestAPI = 'http://127.0.0.1:18080/update_bin2/?format=json'
			}
			const REQUEST = new Request(runSimuRequestAPI, { method: 'POST', body: formData });
			fetch(REQUEST)
				.then((data) => {
					window.location.href = window.location.href;
				}).catch((error) => alert(error))


		},
		/*
		editbulle:function(id_bulle){
			location.replace("/update_bin/"+id_bulle);
		},*/
		uploadBons: function () {
			let formData = new FormData();
			var input = document.querySelector('input[type="file"]')
			formData.append("file", input.files[0])
			formData.append("test", "test")
			console.log(formData)
			console.log(input.files[0])
			if (ONSERVER) {
				var requestAPI = 'http://vanheede.ig.umons.ac.be/upload/test.txt'
			} else {
				var requestAPI = 'http://127.0.0.1:18080/upload/test.txt'
			}
			const request = new Request(requestAPI, { method: 'PUT', body: formData });
			fetch(request) // on récupère les données via l'api
				.then(response => response.json()) // on formate  les données en Json
				.then((data) => {
					console.log(data);
				})
		},
		fetchBulles_Sites: function () {
			//console.log('fetching')
			if (ONSERVER) {
				var fetchBullesAPI = "https://vanheede.ig.umons.ac.be/api_bulles/"
			} else {
				var fetchBullesAPI = "http://127.0.0.1:18080/api_bulles/"
			}
			fetch(fetchBullesAPI) // on récupère les données (bulles) via l'api
				.then(response1 => response1.json()) // on formate  les données en Json
				.then((data) => {
					for (let i of data) {
						this.bulles.push(i);
					}

					// console.table("voici le tableau des bulles",this.bulles)
					//this.$emit('load',this.bulles)
					// console.log("voici la taille du tableau des bulles:",this.bulles.length)
				})

			if (ONSERVER) {
				var fetchSitesAPI = "https://vanheede.ig.umons.ac.be/api_sites/"
			}
			else {
				var fetchSitesAPI = "http://127.0.0.1:18080/api_sites/"
			}
			fetch(fetchSitesAPI) // on récupère les données (sites) via l'api
				.then(response1 => response1.json()) // on formate  les données en Json
				.then((data) => {

					for (let i of data) {
						if(i.vitesse_c ==null && i.vitesse_b==null){
							i.vitesse_c=0;
							i.vitesse_b=0;
						}	
						this.sites.push(i);
					}


					//console.log("voici la taille du tableau des Sites:",this.sites.length)
				})
		},
		switchBullesSites: function () {
			window.location.href = '/sites';
		},

		switchSitesBulles : function() {
			window.location.href = '/bulles';
		},

		
		
	},
	computed: {
		filteredList() {
			recherche = this.searchKey.toLowerCase();

			if (rechercheParAdresse == "on") {
				recherche = url;
				return this.bulles.filter((bulles) => {
					return bulles.addresse.toLowerCase().includes(recherche)
				})
			}
			else {
				return this.bulles.filter((bulles) => {
					return bulles.num_bulle.toLowerCase().includes(recherche)
				})
			}
		},
		filteredList_S() {

			return this.sites.filter((sites) => {
				return sites.nom.toLowerCase().includes(this.searchKey_S.toLowerCase())

			})
		},


	},
	
	
})

function afficherBulles(test) {
	site_Selectione = test.id;
	location.replace("/bulles/?" + site_Selectione);
}