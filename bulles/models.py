# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.db.models.fields.json import JSONField
from django.utils import timezone

class Site(models.Model):
    id_site = models.AutoField(
        db_column="Id_site", primary_key=True
    )  # Field name made lowercase.
    id_depot = models.FloatField(
        db_column="id_depot"
    )  # Field name made lowercase.
    nom = models.CharField(
        db_column="Nom", max_length=100
    )  # Field name made lowercase.
    vitesse_b = models.FloatField(db_column="Vitesse_b")  # Field name made lowercase.
    vitesse_c = models.FloatField(db_column="Vitesse_c")  # Field name made lowercase.
    ecart_type_b = models.FloatField(
        db_column="Ecart_type_b"
    )  # Field name made lowercase.
    ecart_type_c = models.FloatField(
        db_column="Ecart_type_c"
    )  # Field name made lowercase.
    type_site = models.CharField(
        db_column="Type_site", max_length=20
    )  # Field name made lowercase.
    longitude = models.FloatField(db_column="Longitude")  # Field name made lowercase.
    latitude = models.FloatField(db_column="Latitude")  # Field name made lowercase.
    nombre_bulles = models.IntegerField(
        db_column="Nombre_bulles"
    )  # Field name made lowercase.
    date_vidange = models.DateTimeField(
        db_column="Date_vidange", default=timezone.now
    )  # Field name made lowercase.
    #trajet = models.ManyToManyField(Trajet, related_name='site_moi')

    def __str__(self):
        return self.nom
    
    class Meta:
        db_table = "site"


class Bulles(models.Model):
    id_bulle = models.AutoField(primary_key=True)
    num_bulle = models.CharField(max_length=20)
    type_bulle = models.CharField(max_length=20)
    colories = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    date_vidange = models.DateField(
        db_column="date_vidange"
    ) 
    id_depot = models.ForeignKey(
        "Depot", on_delete=models.CASCADE, db_column="id_depot"
    )
    id_site = models.ForeignKey(
        "Site", related_name='bul', on_delete=models.CASCADE, db_column="Id_site"
    )  # Field name made lowercase.
    #camion = models.ManyToManyField(Camion)
    vitesse_remplissage_blanc= models.CharField(max_length=1000)
    vitesse_remplissage_colore=models.CharField(max_length=1000)
    def __str__(self):
        return f"{self.id_bulle} + {self.num_bulle} + {self.type_bulle} + {self.colories} + {self.latitude} + {self.longitude} + {self.date_vidange} + {self.id_depot} + {self.id_site}"
    
    class Meta:
        db_table = "bulles"



class Depot(models.Model):
    id_depot = models.AutoField(primary_key=True)
    nom_depot = models.CharField(max_length=20)
    lieu_recyclage = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        db_table = 'depot'
        
    def __str__(self):
        return self.nom_depot

class Profil_Param(models.Model):
    id = models.AutoField(db_column = "id", primary_key=True)
    Nom = models.CharField(max_length=45)
    parametre = models.JSONField(db_column = "parametre")

    class Meta :
        db_table = "profil_param"

class Simulation(models.Model):
    id_simu = models.AutoField(db_column='Id_simu', primary_key=True)  # Field name made lowercase.
    nom = models.CharField(db_column='Nom', max_length=30)  # Field name made lowercase.
    date_creation = models.CharField(max_length=10)
    date_debut = models.CharField(max_length=10)
    bulles_debordent = JSONField(db_column = "bulles_debordent")
    id_para = models.ForeignKey(Profil_Param, on_delete=models.CASCADE, db_column="id_para")

    class Meta:
        db_table = 'simulation'



class Tournee(models.Model):
    id_trajet = models.ForeignKey('Trajet', on_delete=models.CASCADE, db_column='Id_trajet')  # Field name made lowercase.
    id_site = models.ForeignKey(Site, on_delete=models.CASCADE, db_column='Id_site')  # Field name made lowercase.

    class Meta:
        db_table = 'tournee'


class Trajet(models.Model):
    id_trajet = models.AutoField(
        db_column="Id_trajet", primary_key=True
    )  # Field name made lowercase.
    semaine = models.IntegerField(db_column = "semaine")
    jour= models.IntegerField(db_column = "jour")
    
    id_simu = models.ForeignKey(
        Simulation, related_name = 'traj', on_delete=models.CASCADE, db_column="Id_simu"
    )  # Field name made lowercase.
    bulle = models.ManyToManyField(Bulles)

    class Meta:
        db_table = "trajet"


