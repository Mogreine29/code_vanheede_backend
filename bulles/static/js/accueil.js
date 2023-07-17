var selected = null;
$(document).ready(function() {
    var selected = null;
    $('#date').datepicker({
        multidate : true,
        uiLibrary: 'bootstrap4',
        format: 'dd/mm/yyyy',
        startDate: '0d',
        endDate: '+180d',
    }).on("change",function() {
        selected = $(this).val();  // get the selected date(s)
        selected = selected.split(",") // split the var into a table
        $("#datao").html(selected);
    })
})
 
var app = new Vue({
    el: "#app",
    delimiters: ['[[', ']]'],
	data : {
        selected: null,
    },
    data() {
        return {
            simulations : [], 
            paramSets : [],
            selectedParams : {
                id : 0,
                Nom : "",
                Depot : "Quévy" ,
                vidange : "Minérale",
                Maxtime: 11,
                weeks : 1,
                days : 1,
                petit : 0,
                grand : 0,
                spike : "Désactivé",
                remplissage : 0.75,
                remplissageCamions : "auto",
                mode: "Désactivé",
            },
            selectedDepot : "Quévy",
            selectedVidange : "Quévy",
            optionsList: '<option value="Quévy">Quévy</option><option value="Minérale">Minérale</option><option value="Renaix">Renaix</option>',
        }
    },

    // le created hook peut être utilisé pour exécuter du code après la création d'une instance
    created: function() {
        this.fetchAllParams(); // Fetch all simulations for preset list
        this.fetchAllSim();
        // this.fecthLastVidange()
    },
    methods:{
        // Fetch last vidange : not implemented yet => to unable user from choosing date before the last vidange from all bins from the depot
        // fecthLastVidange: function () {
        //     if (this.selectedDepot == "Quévy") {
        //         depot = 1
        //     }
        //     else if (this.selectedDepot == "Dottignies") {
        //         depot = 2
        //     }
        //     if (ONSERVER) {
        //         var fetchLastVidangeAPI = "https://vanheede.ig.umons.ac.be/last_vidange/" + depot + "/"
        //     } else {
        //         var fetchLastVidangeAPI = "http://127.0.0.1:18080/last_vidange/" + depot + "/"
        //     }
        //     fetch(fetchLastVidangeAPI) // get data via api
        //     .then(response => response.json()) // transform data to json
        //     .then((result) => {
                
        //     })	
        // },

        changeDepot () {
            switch (this.selectedDepot) {
                case 'Quévy':
                  this.optionsList = '<option value="Quévy">Quévy</option><option value="Minérale">Minérale</option><option value="Renaix">Renaix</option>'
                  break;
                case 'Dottignies':
                  this.optionsList = '<option value="Dottignies">Dottignies</option><option value="Minérale">Minérale</option><option value="Renaix">Renaix</option>'
                  break;
            }
        },

        RunSimulation: function(event) {
            event.preventDefault();
            let formData = new FormData();
            const button = document.querySelector("#button");
            const gif_button_simulation = document.querySelector("#gif_button_simulation")

            // Conditions :
            // -     Name not empty
            // -     Nb of days not null
            // -     Nb of weeks not null
            // -     Day selected
            // -     At least one truck selected
            // -     No ""
            if (document.querySelector("#Nom").value != "" && document.querySelector("#jours").value != 0 && document.querySelector("#semaine").value != 0 && document.querySelector("#date-debut").value != "" && (document.querySelector("#petit").value + document.querySelector("#grand").value) != 0 && (document.querySelector("#petit").value != "") && (document.querySelector("#grand").value != "")) {
                // Make sure the selected date is after the last vidange
                

                button.style.display = "none";
                gif_button_simulation.style.display = "flex";
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
                        button.style.display = "flex";
                        gif_button_simulation.style.display = "none";
                        window.location.href=window.location.href;
                    })
                    .catch((_) => {
                        alert("Problème de connexion");
                        button.style.display = "flex";
                        gif_button_simulation.style.display = "none";
                    })
            // Alert if all fields not completed
            } else {
                alert("Paramètre(s) manquant(s)");
            }
        },

        // Fetch all simulations
        fetchAllSim: function () {
            if (ONSERVER) {
                var fetchAllSimuRequestAPI = "https://vanheede.ig.umons.ac.be/all_simu_infos/"
            } else {
                var fetchAllSimuRequestAPI = "http://127.0.0.1:18080/all_simu_infos/"
            }
			fetch(fetchAllSimuRequestAPI) // get data via api
			.then(response => response.json()) // transform data to json
			.then((allSimulations) => {
				for (let simu of allSimulations){
                    simu.date_creation = simu.date_creation.replace(/\//g, '');
                    simu.date_creation = simu.date_creation.substring(0,8)
                    simu.date_creation = simu.date_creation.substring(2,4) + simu.date_creation.substring(0,2) + simu.date_creation.substring(5,8).slice(-2)
                    this.simulations.unshift(simu);
				}
			})	
		},

        // Fetch all simulations for preset list
        fetchAllParams : function () {
            if (ONSERVER) {
                var fetchAllSettingsRequestAPI = "https://vanheede.ig.umons.ac.be/get_all_params/"
            } else {
                var fetchAllSettingsRequestAPI = "http://127.0.0.1:18080/get_all_params/"
            }
			fetch(fetchAllSettingsRequestAPI) // get data via api
			.then(response2 => response2.json()) // transform data to Json
			.then((simuWithParams) => {
				for (let simu of simuWithParams){
                    this.paramSets.push(simu);
                }
               
			})
		},

        fetchParam : function (event){
            this.set = event.target.value;
            if (ONSERVER) {
                var fetchSettingsRequestAPI = "https://vanheede.ig.umons.ac.be/api/param/"+this.set+'/'
            } else {
                var fetchSettingsRequestAPI = "http://127.0.0.1:18080/api/param/"+this.set+'/'
            }
            // alert(fetchSettingsRequestAPI)
			fetch(fetchSettingsRequestAPI) // get data via api
			.then(response3 => response3.json()) // transform data to Json
			.then((data) => {
                this.selectedParams.id = data.id;
                this.selectedParams.Nom = data.Nom;
                this.selectedParams.Depot = data.parametre["Depot"];
                this.selectedParams.vidange = data.parametre["Vidange"];
                this.selectedParams.Maxtime = data.parametre["Max time"]/3600;
                this.selectedParams.weeks = data.parametre["Number of weeks"];
                this.selectedParams.days = data.parametre["Number of days"];
                this.selectedParams.firstDay = data.parametre["date_debut"];
                this.selectedParams.petit = data.parametre["26 Tonnes"];
                this.selectedParams.grand = data.parametre["44 Tonnes"];
                this.selectedParams.spike = data.parametre["Spikes remplissage"]==0 ? "Désactivé" : "Activé"; // 0 -> des | 1 -> act
                this.selectedParams.remplissage = data.parametre["Remplissage limite"];
                this.selectedParams.remplissageCamions = data.parametre["Remplissage limite camions"];
                this.selectedParams.mode = data.parametre["Mode camions adaptatifs"]==0 ? "Désactivé" : "Activé"; // 0 -> des | 1 -> act

                this.selectedDepot = data.parametre["Depot"] // change the selected depot
                this.selectedVidange = data.parametre["Vidange"]
                this.changeDepot()
            })
		},

        deleteSimulation : function (simulation) {
            if (confirm("Etes-vous sûr de vouloir supprimer la simulation " + simulation.nom + "?")) {
                location.replace("/delete_simu/"+simulation.id_simu);
            }
            else {
                console.log("You pressed Cancel!")
            }
        },
    },
})

function viewSimulation(simulation) {
    localStorage.setItem("idSelectedSimulationStorage",simulation.id_simu);
    window.location.href = "/simulations/"
}
