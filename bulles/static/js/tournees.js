// Vue.component('l-map', window.Vue2Leaflet.LMap);
var driver_app = new Vue({
	el: '#driver-app',
	delimiters: ['[[', ']]'],
	data() {
		return {
			simulations: [], // list of simulations
			tournee: [], // list of tours
			bullesQuevy: [],
			bullesDottignies: [],
			bulles: [], // list of bottle banks
			validated: "", // Message of validation on page
			sim_success: "",
			idSelectedSimulation: {},
			dateSelected: null,
			calendarTournees: '',
			paramSets: [],
			selectedParams: {
				id: 0,
				Nom: "",
				Depot: "Quévy",
				vidange: "Minérale",
				Maxtime: 10,
				weeks: 1,
				days: 1,
				petit: 0,
				grand: 0,
				spike: "Désactivé",
				remplissage: 0.75,
				remplissageCamions: "auto",
				mode: "Désactivé",
			},
			selectedDepot: "Quévy",
			selectedVidange: "Quévy",
			optionsList: '<option value="Quévy">Quévy</option><option value="Minérale">Minérale</option><option value="Renaix">Renaix</option>',
		}
	},

	created: function () {
		this.fetchAllSim();
		this.fetchBulles();
		this.fetchAllParams(); // Fetch all simulations for preset list
	},

	watch: {
		dateSelected: function (val) {
			if (val != null) {
				this.changeDate() // do not call when date reseted
			}
		}
	},

	methods: {
		fetchBulles: function () {
			if (ONSERVER) {
				var fetchBullesAPI = "https://vanheede.ig.umons.ac.be/api_bulles/"
			} else {
				var fetchBullesAPI = "http://127.0.0.1:18080/api_bulles/"
			}
			fetch(fetchBullesAPI) // on récupère les données via l'api
				.then(response1 => response1.json()) // on formate les données en Json
				.then((bulles_fetched) => {
					for (let bulle of bulles_fetched) {
						if (bulle.id_depot == 1) { // 1 = Quévy
							this.bullesQuevy.push(bulle)
						} else if (bulle.id_depot == 2) {
							this.bullesDottignies.push(bulle)
						}
					}
				})
		},

		fetchAllSim: function () {
			if (ONSERVER) {
				var fetchAllSimAPI = "https://vanheede.ig.umons.ac.be/all_simu_infos/"
			} else {
				var fetchAllSimAPI = "http://127.0.0.1:18080/all_simu_infos/"
			}
			fetch(fetchAllSimAPI) // on récupère les données via l'api
				.then(response => response.json()) // on formate les données en Json
				.then((simulations_fetched) => {
					for (let simulation of simulations_fetched) {
						simulation.date_creation = simulation.date_creation.replace(/\//g, ''); // MM/jj/aaaa, HH:mm:ss => MMjjaaaa, HH:mm:ss
						simulation.date_creation = simulation.date_creation.substring(0, 8) // MMjjaaaa, HH:mm:ss => jjMMaaaa
						simulation.date_creation = simulation.date_creation.substring(2, 4) + simulation.date_creation.substring(0, 2) + simulation.date_creation.substring(5, 8).slice(-2) // jjMMaaaa => MMjjaaaa
						this.simulations.unshift(simulation); // add simulation to beginning of list
					}

					this.idSelectedSimulation = this.simulations[0].id_simu // Get the first simulation

					this.loadWindow() // Load the window only after fetching the simulations
				})
		},

		// Fetch all simulations for preset list
		fetchAllParams: function () {
			if (ONSERVER) {
				var fetchAllSettingsRequestAPI = "https://vanheede.ig.umons.ac.be/get_all_params/"
			} else {
				var fetchAllSettingsRequestAPI = "http://127.0.0.1:18080/get_all_params/"
			}
			fetch(fetchAllSettingsRequestAPI) // get data via api
				.then(response2 => response2.json()) // transform data to Json
				.then((simuWithParams) => {
					for (let simu of simuWithParams) {
						this.paramSets.push(simu);
					}

				})
		},

		fetchParam: function (event) {
			if (ONSERVER) {
				var fetchSettingsRequestAPI = "https://vanheede.ig.umons.ac.be/api/param/" + event.target.value + '/'
			} else {
				var fetchSettingsRequestAPI = "http://127.0.0.1:18080/api/param/" + event.target.value + '/'
			}
			fetch(fetchSettingsRequestAPI) // get data via api
				.then(response3 => response3.json()) // transform data to Json
				.then((data) => {
					this.selectedParams.id = data.id;
					this.selectedParams.Nom = data.Nom;
					this.selectedParams.Depot = data.parametre["Depot"];
					this.selectedParams.vidange = data.parametre["Vidange"];
					this.selectedParams.Maxtime = data.parametre["Max time"] / 3600;
					this.selectedParams.weeks = data.parametre["Number of weeks"];
					this.selectedParams.days = data.parametre["Number of days"];
					this.selectedParams.firstDay = data.parametre["date_debut"];
					this.selectedParams.petit = data.parametre["26 Tonnes"];
					this.selectedParams.grand = data.parametre["44 Tonnes"];
					this.selectedParams.spike = data.parametre["Spikes remplissage"] == 0 ? "Désactivé" : "Activé"; // 0 -> des | 1 -> act
					this.selectedParams.remplissage = data.parametre["Remplissage limite"];
					this.selectedParams.remplissageCamions = data.parametre["Remplissage limite camions"];
					this.selectedParams.mode = data.parametre["Mode camions adaptatifs"] == 0 ? "Désactivé" : "Activé"; // 0 -> des | 1 -> act

					this.selectedDepot = data.parametre["Depot"] // change the selected depot
					this.selectedVidange = data.parametre["Vidange"]
					this.changeDepot()
				})
		},

		changeDepot() {
			switch (this.selectedDepot) {
				case 'Quévy':
					this.optionsList = '<option value="Quévy">Quévy</option><option value="Minérale">Minérale</option><option value="Renaix">Renaix</option>'
					break;
				case 'Dottignies':
					this.optionsList = '<option value="Dottignies">Dottignies</option><option value="Minérale">Minérale</option><option value="Renaix">Renaix</option>'
					break;
			}
		},

		loadWindow: function () {
			if (ONSERVER) {
				var fetchAPI = "https://vanheede.ig.umons.ac.be/full_simu/" + this.idSelectedSimulation
			} else {
				var fetchAPI = "http://127.0.0.1:18080/full_simu/" + this.idSelectedSimulation
			}
			// alert(fetchAPI)
			fetch(fetchAPI) // get data via api
				.then(response => response.json()) // transform data into Json
				.then((data) => {
					var eventDates = {};
					const lesDatesAMettreEnVert = [];
					// Ici on récupère les dates ou on a associé des trajets (va permettre d'afficher sur le calendrier pour savoir quel jour il y a une tournée)
					for (const [_, value] of Object.entries(data["trajets"])) {
						eventDates[new Date(value["trajet_date"]).toLocaleDateString()] = new Date(value["trajet_date"]).toString();
						var test = new Date(value["trajet_date"]);

						// Je vais tenter de sauvgarder ca plus simplement sous format jour+mois+anne 
						var MyDateString = ('0' + test.getDate()).slice(-2) + ('0' + (test.getMonth() + 1)).slice(-2) + test.getFullYear();
						lesDatesAMettreEnVert.push(MyDateString);
					}
					setCookie("lesDatesAMettreEnVert", lesDatesAMettreEnVert, 7); // S'enregistre que quand on select une simulation
					// fill in the calendar with all the days with a simulation

					// get the depot for displaying the right bulles later
					let [key, trajet] = Object.entries(data["trajets"])[0]
					depotNb = JSON.parse(data["trajets"][key]["tournee"])[0][0]
					if (depotNb == ID_QUEVY) {
						this.bulles = this.bullesQuevy
					} else if (depotNb == ID_DOTTIGNIES) {
						this.bulles = this.bullesDottignies
					}

					// IF A DATE IS NOT SELECTED
					if (!this.dateSelected) {
						let firstDate = trajet.trajet_date
						this.dateSelected = transformDate(firstDate) // transform the date

						localStorage.setItem("dateSelectedStorage", this.dateSelected) // reset the simuId storage
					}

					const $select = document.querySelector('#simu')
					$select.value = this.idSelectedSimulation

					if (this.calendarTournees == "") {
						this.calendarTournees = new Calendar()
					} else {
						this.calendarTournees.updateCalendar()
					}
				})
		},

		changeSimulation: function () {
			this.dateSelected = null
			localStorage.setItem("dateSelectedStorage", null) // reset the simuId storage

			var valeurSimu = $("#simu").val()
			this.idSelectedSimulation = valeurSimu

			this.loadWindow()
		},

		changeDate: function () {
			if (ONSERVER) {
				var fetchCalAPI = "https://vanheede.ig.umons.ac.be/simu_infos/" + this.idSelectedSimulation + "/" + this.dateSelected
			} else {
				var fetchCalAPI = "http://127.0.0.1:18080/simu_infos/" + this.idSelectedSimulation + "/" + this.dateSelected
			}
			// alert(fetchCalAPI)
			fetch(fetchCalAPI) // get data via api
				.then(response => response.json()) // transform data into json
				.then((json) => {
					this.tournee = []
					for (const [key, _] of Object.entries(json["trajets"])) {
						var bins = JSON.parse(json["trajets"][key]["tournee"]);
						idx_bin = 0
						for (const bin of bins) {
							if (bin[0] != ID_DOTTIGNIES && bin[0] != ID_QUEVY && bin[0] != ID_MINERALE && bin[0] != ID_RENAIX) {
								var bulleTemp = {}
								let titre = "";
								try {
									titre = json["trajets"][key]["infos_bulles"][bin[0]]["num_bulle"]
									bulleTemp.id = titre;
									bulleTemp.type = json["trajets"][key]["infos_bulles"][bin[0]]["type_bulle"]
									bulleTemp.couleur = json["trajets"][key]["infos_bulles"][bin[0]]["colories"]
									bulleTemp.poidsB = json["trajets"][key]["liste_poids_blanc"][idx_bin]
									bulleTemp.poidsC = json["trajets"][key]["liste_poids_colore"][idx_bin]
									bulleTemp.position = json["trajets"][key]["bin_to_site"][titre];
								} catch (error) {
									console.log("Error : " + bin[0] + " not found")
									console.error(error)
									bulleTemp.id = "ERROR"
									bulleTemp.type = "ERROR"
									bulleTemp.couleur = "ERROR"
									bulleTemp.position = json["trajets"][key]["bin_to_site"][titre];
								}
								bulleTemp.status = 1;
								this.tournee.push(bulleTemp);
							}
							idx_bin++
						}
					}

				})
		},

		addDangerBin: function () {
			let dangerBin = document.getElementById("dangerBinName").value
			if (dangerBin != "") {
				binsDangerContainer = document.getElementById("bins-danger");
				var children = binsDangerContainer.children;
				let alreadyAdded = false;
				for (var i = 0; i < children.length; i++) {
					var boxChild = children[i];
					if (boxChild.innerHTML == dangerBin) {
						alreadyAdded = true;
					}
				}
				if (alreadyAdded == false) {
					var dangerBinDiv = document.createElement('div'); // is a node
					dangerBinDiv.innerHTML = dangerBin;
					binsDangerContainer.appendChild(dangerBinDiv)
				}
			}
		},
		addAjoutBin: function () {
			let ajoutBin = document.getElementById("ajoutBinName").value
			if (ajoutBin != "") {
				binsAjoutContainer = document.getElementById("bins-ajout");
				var children = binsAjoutContainer.children;
				let alreadyAdded = false;
				for (var i = 0; i < children.length; i++) {
					var boxChild = children[i];
					if (boxChild.innerHTML == ajoutBin) {
						alreadyAdded = true;
					}
				}
				if (alreadyAdded == false) {
					var ajoutBinDiv = document.createElement('div');// is a node
					ajoutBinDiv.className = "ajout";
					var ptext = document.createElement('p');
					ptext.innerHTML = ajoutBin;
					ptext.className = "pmarge";
					var poidsBInput = document.createElement('input');
					poidsBInput.id = "poidsbulle"
					poidsBInput.type = "number";
					poidsBInput.className = "inputpoids";
					poidsBInput.placeholder = "Poids Blanc";
					poidsBInput.required = true;
					var poidsCInput = document.createElement('input');
					poidsCInput.id = "poidsbulle"
					poidsCInput.type = "number";
					poidsCInput.className = "inputpoids";
					poidsCInput.placeholder = "Poids Coloré";
					poidsCInput.required = true;
					binsAjoutContainer.appendChild(ajoutBinDiv)
					ajoutBinDiv.appendChild(ptext)
					ajoutBinDiv.appendChild(poidsBInput)
					ajoutBinDiv.appendChild(poidsCInput)
				}
			}
		},

		validateTrip1: function () {
			binsAjoutContainer = document.getElementById("bins-ajout");
			var ChildrenAjout = binsAjoutContainer.children;
			binsDangerContainer = document.getElementById("bins-danger");
			var ChildrenDanger = binsDangerContainer.children;

			if (ChildrenAjout.length == 0 && ChildrenDanger.length == 0) {
				var verif = 0
				Pbulle = document.querySelectorAll("#poidsbulle")
				for (var i = 0; i < Pbulle.length; i++) {
					if (Pbulle[i].value == "") {
						verif = 1
					}
				}

				if (verif == 0) {
					document.getElementById("validate-trip-button").style.display = "none";
					let formData = new FormData();
					let bins_validate = [];
					let poidsB_validate = [];
					let poidsC_validate = [];
					var planning = document.getElementById("planning-body");

					for (var i = 0, row; row = planning.rows[i]; i++) {
						if (row.cells[6].firstChild.firstChild.checked == true) {
							document.getElementById("validate-trip-button").style.display = "flex";
							alert("Bulles non-vidées ? Veuillez alors recalculer la simulation");
							return;
						}
						if (row.cells[1].innerHTML != "") {
								bins_validate.push(row.cells[0].innerHTML);
								poidsB_validate.push(row.cells[4].children[0].value);
								poidsC_validate.push(row.cells[5].children[0].value);
							}
					}
					
					let dateFormData = "20" + this.dateSelected.substring(4, 6) + "-" + this.dateSelected.substring(2, 4) + "-" + this.dateSelected.substring(0, 2)
					formData.append('tripdate', dateFormData) // format YYYY-MM-DD
					formData.append('sim_id', document.querySelector("#simu").value);
					formData.append('bins_validate', bins_validate);
					formData.append('poidsB_validate', poidsB_validate);
					formData.append('poidsC_validate', poidsC_validate);
					if (ONSERVER) {
						var requestAPI = 'https://vanheede.ig.umons.ac.be/ValidateTrip/?format=json'
					} else {
						var requestAPI = 'http://127.0.0.1:18080/ValidateTrip/?format=json'
					}
					const request = new Request(requestAPI, { method: 'POST', body: formData });
					fetch(request)
						.then(response => response.json())
						.then(result => {
							sleep(5000)
							document.getElementById("validate-trip-button").style.display = "flex";
							document.getElementById("validate-trip-button").innerHTML = "<button type='button' class='btn btn-outline-success' onclick='driver_app.validateTrip()'>Valider la tournée</button>";
							this.validated = "La tournée à été validée.";
						})
						.catch((_) => {
							alert("Problème de connexion");
							document.getElementById("validate-trip-button").style.display = "flex";
						})
				} else {
					alert("Poids de(s) bulle(s) manquant(s)");
					}
			} else {
				alert("Bulles urgentes ou supplémentaires ? Veuillez alors recalculer la simulation");
			}

		},

		validateTrip: function () {
			var verif = 0
			Pbulle = document.querySelectorAll("#poidsbulle")
			for (var i = 0; i < Pbulle.length; i++) {
				if (Pbulle[i].value == "") {
					verif = 1
				}
			}

			if (verif == 0) {
				document.getElementById("validate-trip-button").style.display = "none";
				let formData = new FormData();

				// Functions and forms pour la mise à jour des données sauf pour les non checkées
				let bins_urgent = [];
				let bins_validate = [];
				let poidsB_validate = [];
				let poidsC_validate = [];
				var planning = document.getElementById("planning-body");

				for (var i = 0, row; row = planning.rows[i]; i++) {
					if (row.cells[1].innerHTML != "") {
						if (row.cells[6].firstChild.firstChild.checked == false) {
							bins_validate.push(row.cells[0].innerHTML);
							poidsB_validate.push(row.cells[4].children[0].value);
							poidsC_validate.push(row.cells[5].children[0].value);
						}
					}
				}
				binsAjoutContainer = document.getElementById("bins-ajout");
				var children = binsAjoutContainer.children;
				for (var i = 0; i < children.length; i++) {
					for (var j = 0; j < 3; j++) {
						var boxChild = children[i].children[j]
						if (j == 0) {
							bins_validate.push(boxChild.innerHTML)
						} else if (j == 1) {
							poidsB_validate.push(boxChild.value)
						} else if (j == 2) {
							poidsC_validate.push(boxChild.value)
						}

					}
				}

				let dateFormData = "20" + this.dateSelected.substring(4, 6) + "-" + this.dateSelected.substring(2, 4) + "-" + this.dateSelected.substring(0, 2)
				formData.append('tripdate', dateFormData);
				formData.append('sim_id', document.querySelector("#simu").value);
				formData.append('bins_validate', bins_validate);
				formData.append('poidsB_validate', poidsB_validate);
				formData.append('poidsC_validate', poidsC_validate);
				if (ONSERVER) {
					var requestAPI = 'https://vanheede.ig.umons.ac.be/ValidateTrip/?format=json'
				} else {
					var requestAPI = 'http://127.0.0.1:18080/ValidateTrip/?format=json'
				}
				const REQUEST = new Request(requestAPI, { method: 'POST', body: formData });
				fetch(REQUEST)
					.then(response => response.json())
					.then(result => {
						document.getElementById("validate-trip-button").style.display = "flex";
						document.getElementById("validate-trip-button").innerHTML = "<button type='button' class='btn btn-outline-success' onclick='driver_app.validateTrip()'>Valider la tournée</button>";
						this.validated = "La tournée à été validée.";
					})
					.catch((error) => {
						alert("Erreur")
						console.error(error)
						document.getElementById("validate-trip-button").style.display = "flex";
					})
			}
			else {
				alert("Poids de(s) bulle(s) manquant(s)");
			}
		},

		RestartSimulation: function () {
			var verif = 0
			Pbulle = document.querySelectorAll("#poidsbulle")
			for (var i = 0; i < Pbulle.length; i++) {
				if (Pbulle[i].value == "") {
					verif = 1
				}
			}

			if (verif == 0) {
				document.getElementById("Restartbutton").style.display = "none";
				let formData = new FormData();

				// Functions and forms pour la mise à jour des données sauf pour les non checkées
				let bins_urgent = [];
				let bins_validate = [];
				let poidsB_validate = [];
				let poidsC_validate = [];
				var planning = document.getElementById("planning-body");

				for (var i = 0, row; row = planning.rows[i]; i++) {
					if (row.cells[1].innerHTML != "") {

						if (row.cells[6].firstChild.firstChild.checked == false) {
							bins_validate.push(row.cells[0].innerHTML);
							poidsB_validate.push(row.cells[4].children[0].value);
							poidsC_validate.push(row.cells[5].children[0].value);
						}
					}
				}
				binsDangerContainer = document.getElementById("bins-danger");
				var children = binsDangerContainer.children;
				for (var i = 0; i < children.length; i++) {
					var boxChild = children[i]
					bins_urgent.push(boxChild.innerHTML)
				}
				binsAjoutContainer = document.getElementById("bins-ajout");
				var children = binsAjoutContainer.children;
				for (var i = 0; i < children.length; i++) {
					for (var j = 0; j < 3; j++) {
						var boxChild = children[i].children[j]
						if (j == 0) {
							bins_validate.push(boxChild.innerHTML)
						} else if (j == 1) {
							poidsB_validate.push(boxChild.value)
						} else if (j == 2) {
							poidsC_validate.push(boxChild.value)
						}

					}
				}

				let dateFormData = "20" + this.dateSelected.substring(4, 6) + "-" + this.dateSelected.substring(2, 4) + "-" + this.dateSelected.substring(0, 2)
				formData.append('tripdate', dateFormData);
				formData.append('sim_id', document.querySelector("#simu").value);
				formData.append('bins_validate', bins_validate);
				formData.append('poidsB_validate', poidsB_validate);
				formData.append('poidsC_validate', poidsC_validate);
				formData.append('bins_urgent', bins_urgent);
				if (verif == 0 && document.querySelector("#Nom").value != "" && document.querySelector("#jours").value != 0 && document.querySelector("#semaine").value != 0 && document.querySelector("#date-debut").value != "" && (document.querySelector("#petit").value + document.querySelector("#grand").value) != 0 && (document.querySelector("#petit").value != "") && (document.querySelector("#grand").value != "")) {
					formData.append('Nom', document.querySelector("#Nom").value);
					formData.append('depot', document.querySelector("#depot").value);
					formData.append('vidange', document.querySelector("#vidange").value);
					formData.append('jours', document.querySelector("#jours").value);
					formData.append('semaine', document.querySelector("#semaine").value);
					formData.append('date-debut', document.querySelector("#date-debut").value);
					formData.append('26T', document.querySelector("#petit").value);
					formData.append('44T', document.querySelector("#grand").value);
					formData.append('temps', document.querySelector("#temps").value);
					formData.append('spike', document.querySelector("#spike").value); // mode replissage aléatoire et capteurs
					formData.append('remplissage', document.querySelector("#remplissage").value); // limite bulles
					formData.append('remplissage-truck', document.querySelector("#remplissage-truck").value); // % max camion
					formData.append('mode', document.querySelector("#mode").value); // mode caminons adaptifs
					if (ONSERVER) {
						var runSimuRequestAPI = 'https://vanheede.ig.umons.ac.be/RunSimulation/?format=json'
					} else {
						var runSimuRequestAPI = 'http://127.0.0.1:18080/RunSimulation/?format=json'
					}
					const REQUEST = new Request(runSimuRequestAPI, { method: 'POST', body: formData });
					fetch(REQUEST)
						.then(response => response.json())
						.then(result => {
							console.log(result["simulation_result"]);
							alert("Simulation Recalculée")
							document.getElementById("Restartbutton").style.display = "inline-block";
							window.location.href = window.location.href
						})
						.catch((_) => {
							alert("Problème de connexion");
							document.getElementById("Restartbutton").style.display = "inline-block";
						})
				}
				else {
					alert("Paramètre(s) manquant(s)");
					document.getElementById("Restartbutton").style.display = "inline-block";
				}
			}
			else {
				alert("Poids de(s) bulle(s) manquant(s)");
				document.getElementById("Restartbutton").style.display = "inline-block";
			}

		},

		clearDangerBin: function () {
			document.getElementById("bins-danger").innerHTML = "";
		},
		clearAjoutBin: function () {
			document.getElementById("bins-ajout").innerHTML = "";
		}
	}
})

// To prevent the modal from closing after submission
$('#myModal').on('submit', function (e) {
	e.preventDefault()
})