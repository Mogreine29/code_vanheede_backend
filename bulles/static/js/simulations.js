var driver_app = new Vue({
	el : '#driver-app',
	delimiters: ['[[', ']]'],
    data() {
        return {
            simulations : [], // list of simulations
			idSelectedSimulation : null, // id of the selected simulation
			dateSelected : null, // date of the simulation to display
			calendar : '', // datepicker
			leafletMap : {},
			markersLayer : null,
			polylineLayer : null,
        }
    },

    created: function () {
        this.fetchAllSim() // fetch all simulations -> fetch infos of the 1st simulation -> get first date to display + selectable days -> watcher detects and load all infos of the simulation at this date
    },

	watch: {
		dateSelected: function (val) { // when a date is picked or automatically selected on load
			if (val != null) {
				this.changeDate() // do not call when date is reseted
			}
		}
	},

	methods: {
		fetchAllSim : function () {
			if (ONSERVER) {
				var fetchAllSimAPI = "https://vanheede.ig.umons.ac.be/all_simu_infos/"
			} else {
				var fetchAllSimAPI = "http://127.0.0.1:18080/all_simu_infos/"
			}
			fetch(fetchAllSimAPI) // get all simulations data via api
			.then(response => response.json()) // transform data into json
			.then((allSimulations) => { // transform date of data into readable format??
				for (let simulation of allSimulations) {
					simulation.date_creation = simulation.date_creation.replace(/\//g, '').substring(0,8)
					simulation.date_creation = simulation.date_creation.substring(2,4) + simulation.date_creation.substring(0,2) + simulation.date_creation.substring(5,8).slice(-2)
					this.simulations.unshift(simulation);
				}

				// NOT FROM HOMEPAGE => first simu
				if (localStorage.getItem("idSelectedSimulationStorage") == "null") {
					this.idSelectedSimulation = this.simulations[0].id_simu // Get the first simulation
				}
				// FROM HOMEPAGE => selected simu
				else {
					this.idSelectedSimulation = localStorage.getItem("idSelectedSimulationStorage") // Get the simulation from homepage
					localStorage.setItem("idSelectedSimulationStorage",null) // reset the simuId storage
				}

				// Map
				this.leafletMap = L.map('mapTest')
				// leafletMap.dragging.enable()

				// attribution for OpenStreetMap
				const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
				const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
				const tiles = L.tileLayer(tileUrl,{ attribution });
				tiles.addTo(this.leafletMap);

				this.loadWindow() // Load the window only after fetching the simulations
			}).catch((error) => alert(error))
		},

		loadWindow: function () {
			if (ONSERVER) {
				var fetchAPI = "https://vanheede.ig.umons.ac.be/full_simu/"+this.idSelectedSimulation
			} else {
				var fetchAPI = "http://127.0.0.1:18080/full_simu/"+this.idSelectedSimulation
			}
			fetch(fetchAPI) // get data via api
			.then(response => response.json()) // transform data into Json
			.then((data) => {
				// IF A DATE IS NOT SELECTED
				if (!this.dateSelected) {
					let [_, trajet] = Object.entries(data["trajets"])[0]
					let firstDate = trajet.trajet_date
					this.dateSelected = transformDate(firstDate) // transform the date
					localStorage.setItem("dateSelectedStorage",this.dateSelected) // reset the simuId storage
				}
				var eventDates = {};
				const lesDatesAMettreEnVert = [];
				// Ici on récupère les dates ou on a associé des trajets (va permettre d'afficher sur le calendrier pour savoir quel jour il y a une tournée)
				for (const [_, value] of Object.entries(data["trajets"])) {
					eventDates[ new Date( value["trajet_date"] ).toLocaleDateString()] = new Date( value["trajet_date"] ).toString();
					var test =  new Date( value["trajet_date"] );
		
					// Je vais tenter de sauvgarder ca plus simplement sous format jour+mois+anne 
					var MyDateString = ('0' + test.getDate()).slice(-2) + ('0' + (test.getMonth()+1)).slice(-2) + test.getFullYear();
					lesDatesAMettreEnVert.push(MyDateString);
				}
				
				setCookie("lesDatesAMettreEnVert",lesDatesAMettreEnVert,7); // S'enregistre que quand on select une simulation
				// fill in the calendar with all the days with a simulation

				const $select = document.querySelector('#simu')
				$select.value = this.idSelectedSimulation

				if (this.calendar == "") {
					this.calendar = new Calendar()
				} else {
					this.calendar.updateCalendar()
				}
			})
		},

		changeSimulation: function () {
			this.dateSelected = null
			localStorage.setItem("dateSelectedStorage",null) // reset the simuId storage

			var valeurSimu = $("#simu").val()
			this.idSelectedSimulation = valeurSimu

			this.loadWindow()
		},

		changeDate: function () {
			// layers for marker
			if (this.markersLayer != null) {
				this.markersLayer.clearLayers()
			}
			if (this.polylineLayer != null) {
				this.polylineLayer.clearLayers()
			}
			// Leaflet markers
			this.markersLayer = new L.LayerGroup()
			this.polylineLayer = new L.LayerGroup()
			this.leafletMap.addLayer(this.markersLayer); // layer for markers
			this.leafletMap.addLayer(this.polylineLayer); // layer for markers
		
			var colors=["red", "blue", "black", "green", "purple", "orange", "yellow", "pink"]
			if (ONSERVER) {
				var fetchCalAPI = "https://vanheede.ig.umons.ac.be/simu_infos/"+this.idSelectedSimulation+"/"+this.dateSelected
			} else {
				var fetchCalAPI = "http://127.0.0.1:18080/simu_infos/"+this.idSelectedSimulation+"/"+this.dateSelected
			}
			// alert(fetchCalAPI)
			fetch(fetchCalAPI) // get data via api
			.then(response => response.json()) // transform data into json
			.then((json) => {
				let totalListLat = []
				var idx_route = 0
				document.getElementById("info-area").innerHTML = '' // Removing all old trjacts infos
				
				for (const [key, trajet] of Object.entries(json["trajets"])) {
					var oldIdxRoute = idx_route
					let nbQuevy = 0
					let nbDottignies = 0
					let listLat = []
					var bins = JSON.parse(trajet["tournee"])
					for (const bin of bins) {
						let titre = ""
						let weightBinPopup = ""
						// Dépôt Dottignies
						if (bin[0] == ID_DOTTIGNIES) {
							titre = "Dépôt Dottignies";
							var isDepot = true;
							nbDottignies ++
							if (nbDottignies >= 2) {
								let marker = L.marker([bin[2], bin[3]],{title : titre}).addTo(this.markersLayer);
								listLat.push([bin[2], bin[3]])
								totalListLat.push([bin[2], bin[3]])
								var popupText = titre
								
								// Popup of marker
								marker.bindPopup(popupText);

								// Line of the markers
								var polyline = L.polyline(listLat, {color: colors[idx_route]})
								this.polylineLayer.addLayer(polyline)

								listLat = []
								idx_route++
							}
						// Dépôt Quévy
						} else if (bin[0] == ID_QUEVY) {
							titre = "Dépôt Quévy";
							var isDepot = true;
							nbQuevy ++
							if (nbQuevy >= 2) {
								let marker = L.marker([bin[2], bin[3]],{title : titre}).addTo(this.markersLayer);
								listLat.push([bin[2], bin[3]])
								totalListLat.push([bin[2], bin[3]])
								var popupText = titre
								
								// Popup of marker
								marker.bindPopup(popupText);

								// Line of the markers
								var polyline = L.polyline(listLat, {color: colors[idx_route]})
								this.polylineLayer.addLayer(polyline)

								listLat = []
								idx_route++
							}
						// Dépôt Minérales
						} else if (bin[0] == ID_MINERALE) {
							titre = "Dépôt Minérale";
							var isDepot = true;
						} else if (bin[0] == ID_RENAIX) {
							titre = "Dépôt Renaix";
							var isDepot = true;
						} else { // Bulle
							isDepot = false;
							try {
								titre = json["trajets"][key]["infos_bulles"][bin[0]]["num_bulle"];
							} catch (error) {
								console.log("Error : " + bin[0] + " not found")
								console.error(error)
							}
							weightBinPopup = bin[1] + " kg";
						}
						let marker = L.marker([bin[2], bin[3]],{title : titre}).addTo(this.markersLayer);
						listLat.push([bin[2], bin[3]])
						totalListLat.push([bin[2], bin[3]])
						var popupText = titre + '<br/>' + weightBinPopup;
		
						// trajet["type"] = type de camion -> 1 : 26T and 2 : 44T
						// 44T (and not a trailer depot) -> adding option to change the depot of the trailer manually
						if (trajet["type"] == 2 && isDepot == false) {
							popupText += '<br/><div id="'+ titre +'" > <button type="button" onclick="driver_app.Change44T(\''+ titre +'\', '+key+')" class="transform-button">Transformer en dépôt remorque</button> </div>'
						}
						
						// Popup of marker
						marker.bindPopup(popupText);
					}
					
					if (!isDepot) {
						// Line of the markers
						var polyline = L.polyline(listLat, {color: colors[idx_route]})
						this.polylineLayer.addLayer(polyline)
					}
						// infos about the traject
						const infos = document.createElement("div")
						infos.classList.add("result-text-block")
						
						let durationTotalMinutes = parseFloat(trajet["temps"])/60
						let durationMinutes = (durationTotalMinutes%60).toFixed(0).padStart(2, '0')
						let durationHours = Math.trunc((durationTotalMinutes/60).toFixed(2))
						duration = durationHours + "h" + durationMinutes

						if (json["trajets"][key]["type"] === 1) {
							var type = "26 Tonnes";
							var capacite = capacite_26T
						} else {
							var type = "44 Tonnes";
							var capacite = capacite_44T
						}
			
						// Informations about the truck journey
						infos.innerHTML = "Type de camion : " + type + " </br>"
						infos.innerHTML += "Temps de trajet du camion : " + duration + "</br>"
						infos.innerHTML += "Poids blanc du camion : " + trajet["poidsb"] + " kg </br>"
						infos.innerHTML += "Poids coloré du camion : " + trajet["poidsc"] + " kg </br>"
						infos.innerHTML += "Poids total : " + parseFloat(trajet["poidsc"] + trajet["poidsb"]) + " kg </br>"
						
						// // Surcharge
						// if (json["trajets"][key]["poidsb"] > capacite/2){
						// 	infos.innerHTML += "<span style='color:red;'>surcharge du blanc " + parseFloat(json["trajets"][key]["poidsb"] - capacite/2) + "</span>"
						// } else if (json["trajets"][key]["poidsc"] > capacite/2){
						// 	infos.innerHTML += "<span style='color:red;'>surcharge du coloré " + parseFloat(json["trajets"][key]["poidsc"] - capacite/2) + "</span>"
						// }
			
						// One color
						if (oldIdxRoute+1 == idx_route) {
							infos.style.borderLeft = "thick solid " + colors[oldIdxRoute]
						}
						else { // More than 1 color
							let nbColors = idx_route - oldIdxRoute
							let stepPercent = (100/nbColors).toFixed(0)
							infos.style.borderLeft = "thick solid"

							let linearGrad = "linear-gradient(" + colors[oldIdxRoute] + " 0%, " + colors[oldIdxRoute] + " " + stepPercent + "%"
							for (let i = oldIdxRoute+1; i < idx_route; i++) { // from the 2nd color
								i - oldIdxRoute
								if (i == idx_route-1) {
									lastPercent = 100
								} else {
									lastPercent = (i - oldIdxRoute + 1)*stepPercent
								}
								linearGrad = linearGrad.concat(", " + colors[i] + " " + (i - oldIdxRoute)*stepPercent + "%, " + colors[i] + " " + lastPercent + "%")
							}
							linearGrad = linearGrad.concat(") 1")
							infos.style.borderImage = linearGrad
						}

						const container = document.createElement("div")
						container.classList.add("flex-container")
						container.appendChild(infos)

						// Scrolling list
						const driver = document.createElement("div");
						driver.classList.add("driver");
						container.appendChild(driver)
						document.getElementById("info-area").appendChild(container);

			
						// Type of truck
						const driver_name = document.createElement("div");
						driver_name.classList.add("driver-name");
						driver_name.innerHTML = type;
						driver.appendChild(driver_name);
			
						// List of bulles
						const driver_bulles = document.createElement("table");
						driver_bulles.classList.add("driver-bulles");
						driver_bulles.id = "table-bulles-"+idx_route;
						driver.appendChild(driver_bulles);
						
						// each bin in list
						for (const bin of bins) {
							if (bin[0] != ID_QUEVY && bin[0] != ID_DOTTIGNIES && bin[0] != ID_MINERALE && bin[0] != ID_RENAIX) {
								const tr = document.createElement("tr");
								const td = document.createElement("td");
								try {
									td.innerHTML = json["trajets"][key]["infos_bulles"][bin[0]]["num_bulle"] + "</br>";
								} catch (error) {
									console.log("Error : " + bin[0] + " for the list of bins")
									console.error(error)
								}
								driver_bulles.appendChild(tr);
								tr.appendChild(td);
							}
						}
				}
				// zoom to fit all markers in the view
				this.leafletMap.fitBounds(totalListLat)
			})
		},

		// // Change the place of the remorque for 44T
		// Change44T: function (binId, trajet_id) {
		// 	document.getElementById(binId).innerHTML = "<img src='images/loading.gif'/>";
		// 	let formData = new FormData();
        //     formData.append('bin_id', binId);
        //     formData.append('trajet_id', trajet_id);;
		// 	if (ONSERVER) {
		// 		var requestAPI = 'http://vanheede.ig.umons.ac.be/Change44T/?format=json'
		// 	} else {
		// 		var requestAPI = 'http:///Change44T/?format=json'
		// 	}
        //     const request = new Request(requestAPI, {method: 'POST', body: formData});
		// 	fetch(request)
		// 	.then(response => response.json()) // transform data into Json
		// 	.then((data) => {
		// 		document.getElementById(binId).innerHTML = data["status"];
		// 	})
		// }
	}
})

function ExportToExcel() {
	const NB_WEEKS = document.getElementById('nbr_weeks').value // nbr of weeks to extract

	const DEPOTS_IDS = [ID_QUEVY, ID_DOTTIGNIES, ID_MINERALE, ID_RENAIX] // to check if it's a depot

	const DEPOTS_NAMES = {}
	DEPOTS_NAMES[ID_QUEVY] = "Quévy"
	DEPOTS_NAMES[ID_DOTTIGNIES] = "Dottignies"
	DEPOTS_NAMES[ID_MINERALE] = "Minérale"
	DEPOTS_NAMES[ID_RENAIX] = "Renaix"

	// Get the simulation id from the url
	let simuId = driver_app.idSelectedSimulation
	// let simuId = parseInt(window.location.href.split('?')[1].split('&')[0].split('=')[1])

	// Header of Excel
	const WORKSHEET_HEADER_1 = ["", "Chauffeur", "______________________________", "", "Vidange à Minérale", "", "______________________________"]
	const WORKSHEET_HEADER_2 = ["", "Date de collecte", "______________________________", "", "Chauffeur", "", "______________________________"]
	const WORKSHEET_HEADER_3 = ["", "Numéro conteneur", "______________________________", "", "Numéro conteneur", "", "______________________________"]
	const WORKSHEET_HEADER_4 = ["", "Conteneur", "Rempli / A compléter" , "", "Date", "", "______________________________"]
	const WORKSHEET_COLUMN_NAMES_1 = ["", "", "", "", "Kg estimés", "", "Kg collectés", "", "Etat bulle"]
	const WORKSHEET_COLUMN_NAMES_2 = ["", "Sites + adresses", "Net", "Num Bulles", "Blanc", "Couleur", "Blanc", "Couleur", "Pollution", "Dommage", "Bris de verre sur le sol", "Récipients (sacs, carton...)", "Céramique, pierre, porcelaine", "Vitrocéramiques, pyrex", "Verre creux", "Verre plat", "Déchets ménagers, encomb"]
	
	let currentWeek = 0
	
	let stepRows = [] // each step of the trajet (depot, bulle)

	const FILENAME_BEGIN = 'semaine_' // beginning of name of Excel file

	// Button to extract
	const button = document.querySelector("#button")

	if (ONSERVER) {
		var fetchSimuDataAPI = "https://vanheede.ig.umons.ac.be/full_simu/" + simuId
	} else {
		var fetchSimuDataAPI = "http://127.0.0.1:18080/full_simu/" + simuId
	}
	fetch(fetchSimuDataAPI)
		.then(function (response) {
			return response.json()
		})
		.then(function (json) {
			// button
			button.disabled = true
			animation()

			// Get first day
			let dateFirstDayToExport = Object.values(json["trajets"])[0].trajet_date.split(' ')[0].split('-').reverse().join('/')
			// Name
			let dateForWorkbookName = dateFirstDayToExport.replaceAll('/','.')
			// Create Excel file
			workBook = XLSX.utils.book_new()

			// Loop through all days of trajet
			nb_truck = 1 // to separate Excel for each trajet
			old_date = dateFirstDayToExport
			for (const [_, trajetData] of Object.entries(json["trajets"])) { // all the trajects of all days of the week				
				// Break when we reach unwanted week
				if (trajetData.semaine > NB_WEEKS - 1) {
					break
				}
				
				// Get current date
				let date = trajetData.trajet_date.split(' ')[0].split('-').reverse().join('/')
				if (date != old_date) {
					nb_truck = 1
					old_date = date
				}

				// Check if we need to create new Excel file == new week
				if (trajetData.semaine != currentWeek) {
					XLSX.writeFile(workBook, FILENAME_BEGIN + dateForWorkbookName + '.xlsx') // (content, filename)
					
					// new Excel file for new week
					workBook = XLSX.utils.book_new()
					dateForWorkbookName = date.replaceAll('/','.') // new name
					currentWeek ++ // next week
				}
				// Get white and coloured lists
				let liste_poids_blanc = trajetData.liste_poids_blanc
				let liste_poids_colore = trajetData.liste_poids_colore

				// 2x in a row the same bulle => depot fictif
				let prevBulle = ""

				indice_bulle = 0
				for (const [_, bulleArray] of Object.entries(eval(trajetData.tournee))) { // Loop through all steps of tournee
					// IF depot
					if (DEPOTS_IDS.includes(bulleArray[0])) {
						stepRows.push([
							indice_bulle + 1,
							DEPOTS_NAMES[bulleArray[0]],
							"DEPOT",
						])
						indice_bulle++
					}
					// IF depot fictif for trailer
					else if (bulleArray[0] == prevBulle) {
						stepRows.push([
							indice_bulle + 1,
							trajetData.bin_to_site[trajetData.infos_bulles[bulleArray[0]].num_bulle], // Adresse bulle
							"DEPOT FICTIF",
						])
						indice_bulle++
					}
					// IF bottle bank
					else {
						try {
							stepRows.push([
							indice_bulle + 1,
							trajetData.bin_to_site[trajetData.infos_bulles[bulleArray[0]].num_bulle], // Adresse bulle
							trajetData.infos_bulles[bulleArray[0]].type_bulle == "Double" ? "DUO" : "MONO " + (trajetData.infos_bulles[bulleArray[0]].colories == "White" ? "BL" : "COL"), // Type + color bulle
							trajetData.infos_bulles[bulleArray[0]].num_bulle, // N° bulle
							liste_poids_blanc != null ? liste_poids_blanc[indice_bulle] : "poids total :", // Total weight estimated
							liste_poids_colore != null ? liste_poids_colore[indice_bulle] : bulleArray[1],
							])
						} catch (error) {
							stepRows.push([
								indice_bulle + 1,
								"ERROR", // Adresse bulle
								"ERROR", // Type + color bulle
								"ERROR", // N° bulle
								liste_poids_blanc != null ? liste_poids_blanc[indice_bulle] : "poids total :", // Total weight estimated
								liste_poids_colore != null ? liste_poids_colore[indice_bulle] : bulleArray[1],
							])
							console.error(error)
						}
						
						indice_bulle++
					}
					prevBulle = bulleArray[0]
				}

				// Name of the Excel sheet
				// type de camion
				// console.log('trajetData.type_camion = ' + trajetData.type_camion)
				if (trajetData.type_camion == 1) {
					camion = "26T"
				}
				else if (trajetData.type_camion == 2) {
					camion = "44T"
				}
				else {
					camion = "No info"
				}
				let workSheetName = date.replaceAll('/','.') + "_" + camion + "(" + nb_truck + ")"
				const workSheetData = [
					WORKSHEET_HEADER_1, // Headers rows
					WORKSHEET_HEADER_2,
					WORKSHEET_HEADER_3,
					WORKSHEET_HEADER_4,
					["", "Date", date], // Date row
					["", "Type", camion], // Truck type row
					[""], // Empty row
					WORKSHEET_COLUMN_NAMES_1, // Column names row
					WORKSHEET_COLUMN_NAMES_2, // Column names row					
					...stepRows // All data
				]

				// Create the sheet filled with data
				const workSheet = XLSX.utils.aoa_to_sheet(workSheetData)

				// Merge "kg" cells
				let mergeVidange = XLSX.utils.decode_range("E1:F1") // to merge those 2 cells
				let mergeChauffeur = XLSX.utils.decode_range("E2:F2") // to merge those 2 cells
				let mergeNumero = XLSX.utils.decode_range("E3:F3") // to merge those 2 cells
				let mergeDate = XLSX.utils.decode_range("E4:F4") // to merge those 2 cells
				let mergeKgEstimes = XLSX.utils.decode_range("E7:F7") // to merge those 2 cells
				let mergeKgCollectes = XLSX.utils.decode_range("G7:H7")
				let mergeEtatBulle = XLSX.utils.decode_range("I7:J7")
				workSheet['!merges'] = [] // create list of cells to merge
				workSheet['!merges'].push(mergeVidange,mergeChauffeur,mergeNumero,mergeDate,mergeKgEstimes,mergeKgCollectes,mergeEtatBulle) // add all cells to merge

				// Auto width of columns
				const nbRowWithMaxColumns = 8
				workSheet['!cols'] = workSheetData[nbRowWithMaxColumns].map((_, i) => ({
					wch: Math.max(...workSheetData.map(a2 => a2[i] ? a2[i].toString().length : 0))
				}))

				// Append complete day sheet to Excel file
				XLSX.utils.book_append_sheet(workBook, workSheet, workSheetName)
				// reset data
				stepRows = []
				
				nb_truck++
			} // End of loop through days

			XLSX.writeFile(workBook, FILENAME_BEGIN + dateForWorkbookName + '.xlsx') // (content, filename)

			setTimeout(() => {
                button.disabled = false;
                downloading = false;
            }, 5000);

	}).catch((error) => {
		alert("Problème de téléchargement");
		console.error(error)
	})
}

///////////////////////////////
// Animation button extract
/////////////////////////////

let tl,downloading = false,points = [],
    btn = document.querySelector('.btn'),
    dot = document.querySelector('.dot'),
    text = document.querySelector('.text'),
    mainCirc = document.querySelector('.mainCircle'),
    subCirc = document.querySelector('.subCircle'),
    mainCircFill = document.querySelector('.mainCircleFill'),
    arrow = document.querySelector('.arrow'),
	rect = document.querySelector('.rect');

   //TweenLite.set(rect, { transformOrigin: '50% 50%', rotation: 45 });

function animation() {
	if (downloading) return;
    downloading = !downloading;
    let downloadTime = Math.random() * .5 + .7;
    tl = new gsap.timeline({});
    
    tl.play().
        to(arrow, .35, { y: 2.5, ease: CustomEase.create('custom', 'M0,0,C0.042,0.14,0.374,1,0.5,1,0.64,1,0.964,0.11,1,0') }, 'click+=0.01').
        to(text, .3, { svgOrigin: '55% 20%', scale: .77, ease: CustomEase.create('custom', 'M0,0,C0.042,0.14,0.374,1,0.5,1,0.64,1,0.964,0.11,1,0') }, 'click+=.05').
        to(btn, .7, { attr: { d: 'M50,6.25 h0 a10,10 0 0,1 10,10 a10,10 0 0,1 -10,10 s0,0 0,0  a10,10 0 0,1 -10,-10 a10,10 0 0,1 10,-10 h0' }, ease: Sine.easeOut }, 'squeeze').
        to([mainCirc, mainCircFill, rect, arrow], .7, { x: 30, ease: Sine.easeOut }, 'squeeze').
        to(rect, .7, { fill: 'transparent', rotation: 270, ease: Sine.easeOut }, 'squeeze').
        to(text, .3, { autoAlpha: 0, y: 10, onComplete: changeText }, 'squeeze').
		to(arrow, .7, { attr: { d: 'M20,20 l3.5,-3.5 l-3.5,-3.5 M20,20 l-3.5,-3.5 l3.5,-3.5 M20, 20 l0,0' }, fill: 'white', transformOrigin: '47% 55%', rotation: 225, ease: Sine.easeOut }, 'squeeze').
        to(dot, .4, { attr: { r: 1.5 }, ease: Back.easeOut.config(7) }).
        to(dot, downloadTime, { bezier: { type: 'cubic', values: points }, attr: { r: 2.7 }, ease: Power2.easeIn }, 'fill').
        to('.gradient', downloadTime, { attr: { offset: '0%' }, ease: Power2.easeIn }, 'fill').
        to(dot, .44, { fill: '#FFC700', y: -17, ease: Power1.easeOut }, 'stretch-=.01').
        to(dot, .27, { transformOrigin: '50% 50%', scaleX: .5, ease: SlowMo.ease.config(0.1, 2, true) }, 'stretch+=.04').
        to(dot, .3, { scaleY: .6, ease: SlowMo.ease.config(0.1, 2, true) }, 'stretch+=.31').
        to(dot, .44, { scaleX: .4, y: 22, ease: Power2.easeIn }, 'stretch+=.45').
        to([mainCirc, subCirc, arrow, rect, mainCircFill], .33, { opacity: 0, ease: Power2.easeOut }, 'stretch+=.2').
        to(btn, .4, { attr: { d: 'M50,6.5 h20 a10,10 0 0,1 10,10 a10,10 0 0,1 -10,10 s-20,0 -40,0 a10,10 0 0,1 -10,-10 a10,10 0 0,1 10,-10 h20' }, ease: Power1.easeOut }, 'stretch+=.2').
        set(dot, { opacity: 0 }, 'stretch+=.875').
        to(btn, .01, { stroke: '#FFC700', ease: Power2.easeIn }, 'stretch+=.87').
        to(btn, .3, {
            attr: { d: 'M50, 6.5 h20 a10,10 0 0,1 10,10 a10,10 0 0,1 -10,10 s0,0 -40,0 a10,10 0 0,1 -10,-10 a10,10 0 0,1 10,-10 h20' },
            ease: CustomEase.create('custom', 'M0,0 C0.046,0.062 0.018,1 0.286,1 0.532,1 0.489,-0.206 0.734,-0.206 0.784,-0.206 0.832,-0.174 1,0')
        }, 'stretch+=.869').
        to(text, .45, { autoAlpha: 1, y: 0, ease: Back.easeOut.config(2.5) }, 'stretch+=.855');       
};

function restart() {
	tl.reverse();
		text.textContent = 'Extraire Excel';
		TweenLite.set(text, { x: 0 });
		downloading = false;
};

function changeText() {
	text.textContent = 'ouvrir';
	text.fill = "#FFC700";
	TweenLite.set(text, { x: -5 });
}

$('mapTest').mouseup( function() {
    map.dragging.enable();
});
