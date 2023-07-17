class Calendar {
	constructor() {
		// Day selected after a click or when loading the window
		this.dateSelectedFull = localStorage.getItem("dateSelectedStorage"), // 281122
		this.yearSelected = parseInt("20" + this.dateSelectedFull.substring(4,6)), //2022
		this.monthSelected = parseInt(this.dateSelectedFull.substring(2,4)) - 1, // jan = 0, fev = 1
		this.daySelected = parseInt(this.dateSelectedFull.substring(0,2));

		// Month and year currently displayed
		this.monthDisplayed = this.monthSelected
		this.yearDisplayed = this.yearSelected

		// Today
		this.todayFull = new Date(), // full date of today
		this.yearToday = this.todayFull.getFullYear(),
		this.monthToday = this.todayFull.getMonth(),
		this.dayToday = this.todayFull.getDate(),
		this.monthTag = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Aout","Septembre","Octobre","Novembre","Décembre"],
		this.days = document.getElementsByTagName('td'),
		this.daysLen = this.days.length

		this.lesDatesAMettreEnVert = this.getCookie("lesDatesAMettreEnVert");
		this.lesDatesAMettreEnVert = this.lesDatesAMettreEnVert.split(",");

		this.reset = document.getElementById('reset'),
		this.pre = document.getElementsByClassName('pre-button'),
		this.next = document.getElementsByClassName('next-button');

		var that = this
		this.pre[0].addEventListener('click', function () {	
			that.preMonth()
		})
		this.next[0].addEventListener('click', function () {
			that.nextMonth()
		})

		this.draw()
	}
	draw() {
		this.drawDays()

		// When we click on "Today"
		this.reset.addEventListener('click', function () {
			this.reset()
		})

		var that = this
		while (this.daysLen--) {
			this.days[this.daysLen].addEventListener('click', function () {
				that.clickDay(this);
			});
		}
	}

	drawHeader() { // rectangle on the left
		var headDay = document.getElementsByClassName('head-day'),
			headMonth = document.getElementsByClassName('head-month')

		// headDay[0].innerHTML = todayFull.getDate();
		headDay[0].innerHTML = this.daySelected
		headMonth[0].innerHTML = this.monthTag[this.monthSelected] + " - " + this.yearSelected;
	}

	drawDays() {
		if (this.dateSelectedFull) { // if selected day
			var year = this.yearDisplayed
			var month = this.monthDisplayed
		}
		else { // today if no day selected
			var year = this.yearToday
			var month = this.monthToday
		}
		var startDay = new Date(year, month, 1).getDay(), // sunday = 0, monday = 1 ... saturday = 6
			nDays = new Date(year, month + 1, 0).getDate(),
			n // monday = 0, sunday = 6
		if (startDay == 0) {
			startDay = 6 // sunday
		} else {
			startDay = startDay - 1 // -1 cause start day considering sunday first day of the week
		}
		n = startDay

		// Draw header (rectange on left)
		this.drawHeader()
		this.drawMonth()

		// Reinit all
		for (var k = 0; k < 42; k++) {
			this.days[k].innerHTML = '';
			this.days[k].id = '';
			this.days[k].className = '';
		}

		// Definit le jour (1,2,3?4,ect) pour chaque case
		for (var i = 1; i <= nDays; i++) {
			this.days[n].innerHTML = i;
			n++;
		}

		// Get the days with simulations colored
		for (var j = 0; j < 42; j++) {
			if (this.days[j].innerHTML === "") { // On desactive les cases vides pour pas avoir un entourage de bulle lorsque on les survol
				this.days[j].id = "disabled";
			}
			
			// Iterate through the dates with a simulation
			for (var i = 0; i < this.lesDatesAMettreEnVert.length; i++) {
				let dayWithSimulation = this.lesDatesAMettreEnVert[i]
				// alert(dayWithSimulation)
				let yearSimu = dayWithSimulation.slice(4, 8);
				let monthSimu = dayWithSimulation.slice(2, 4);
				let daySimu = dayWithSimulation.slice(0, 2);
				dayWithSimulation = new Date(yearSimu, monthSimu - 1, daySimu)

				if (dayWithSimulation) {
					if ((j === dayWithSimulation.getDate() + startDay - 1) && (this.monthDisplayed === dayWithSimulation.getMonth()) && (this.yearDisplayed === dayWithSimulation.getFullYear())) { // On vérifie si on est au bon mois, bon jour et bonne annee
						this.days[j].classList.add("selectable")
						// If date selected
						if ((j == this.daySelected + startDay - 1) && (this.monthDisplayed == this.monthSelected) && (this.yearDisplayed == this.yearSelected)) {
							this.days[j].classList.add("selected")
						}
					}
				}
			}
		}
	}

	// Month currently displayed on calendar
	drawMonth() {
		var headDateDisplayed = document.getElementsByClassName('dateDisplayed')
		// headDateDisplayed[0].innerHTML = monthTag[monthDisplayed]
		headDateDisplayed[0].innerHTML = this.monthTag[this.monthDisplayed] + " " + this.yearDisplayed
	}

	clickDay(dayClicked) { // dayClicked = HTML day
		// Only if selectable date
		if (dayClicked.id != "disabled" & dayClicked.className == "selectable") {
			// delete class of old selected date
			let oldSelected = document.getElementsByClassName("selected")
			if(oldSelected.length !== 0){
				oldSelected[0].classList.remove("selected")
			}

			// select new date
			this.yearSelected = this.yearDisplayed
			this.monthSelected = this.monthDisplayed
			this.daySelected = parseInt(dayClicked.innerHTML)
			dayClicked.classList.add("selected")
			driver_app.dateSelected = String(this.daySelected).padStart(2, '0') + String(this.monthSelected+1).padStart(2, '0') + String(this.yearSelected).substring(2,4)
			// redraw header
			this.drawHeader()
		}

	}
	preMonth() {
		if (this.monthDisplayed == 0) {
			this.monthDisplayed = 11
			this.yearDisplayed -= 1
		}
		else {
			this.monthDisplayed -= 1
		}
		this.drawDays()
	}
	nextMonth() {
		if (this.monthDisplayed == 11) {
			this.monthDisplayed = 0
			this.yearDisplayed += 1
		} else {
			this.monthDisplayed += 1
		}
		this.drawDays();
	}
	reset() {
		this.monthToday = todayFull.getMonth();
		this.yearToday = todayFull.getFullYear();
		this.dayToday = todayFull.getDate();
		this.drawDays();
	}
		//Fct pour cookies
	getCookie(cname) {
		let name = cname + "=";
		let decodedCookie = decodeURIComponent(document.cookie);
		let ca = decodedCookie.split(';');
		for(let i = 0; i <ca.length; i++) {
			let c = ca[i];
			while (c.charAt(0) == ' ') {
				c = c.substring(1);
			}
			if (c.indexOf(name) == 0) {
				return c.substring(name.length, c.length);
			}
		}
		return "";
	}
	updateCalendar() {
		this.dateSelectedFull = localStorage.getItem("dateSelectedStorage"), // 281122
		this.yearSelected = parseInt("20" + this.dateSelectedFull.substring(4,6)), //2022
		this.monthSelected = parseInt(this.dateSelectedFull.substring(2,4)) - 1, // jan = 0, fev = 1
		this.daySelected = parseInt(this.dateSelectedFull.substring(0,2));

		// Month and year currently displayed
		this.monthDisplayed = this.monthSelected
		this.yearDisplayed = this.yearSelected

		this.daysLen = this.days.length

		this.lesDatesAMettreEnVert = this.getCookie("lesDatesAMettreEnVert");
		this.lesDatesAMettreEnVert = this.lesDatesAMettreEnVert.split(",");

		this.draw()
	}
}

// function to transform date in full format to short format for the ref
function transformDate (date) { // 2022-11-14 00:00:00 => 141122
	date = date.split(' ') // 2022-11-14 00:00:00 => 2022-11-14,00:00:00
	date = date[0] // 2022-11-14,00:00:00 => 2022-11-14
	date = date.split('-') // 2022-11-14 => 2022,11,14
	date[0] = date[0].substring(2,4) // 2022,11,14 => 22,11,14
	date = date.reverse() // 22,11,14 => 14,11,22
	date = date.join('') // 14,11,22 => 141122
	return date;
}

function setCookie(cname, cvalue, exdays) {
	const d = new Date();
	d.setTime(d.getTime() + (exdays*24*60*60*1000));
	let expires = "expires="+ d.toUTCString();
	document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}