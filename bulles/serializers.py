from rest_framework import serializers

from bulles.models import *


class DepotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depot
        fields = ['nom_depot']

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ["id_site","id_depot","nom", "date_vidange", "latitude", "longitude", "vitesse_c","vitesse_b", "type_site", "nombre_bulles"]


class BullesSerializer(serializers.ModelSerializer):
    # id_depot = serializers.SlugRelatedField(

    #     read_only =True,
    #     slug_field='nom_depot'
    # )

    # id_site = serializers.SlugRelatedField(

    #     read_only =True,
    #     slug_field='nom'
    # )

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Bulles.objects.create(**validated_data)


    class Meta:
        model = Bulles
        ordering = ['id']
        fields = ['id_bulle','num_bulle', 'type_bulle', 'date_vidange', 'colories', 'latitude', 'longitude', 'id_depot', 'id_site', 'vitesse_remplissage_blanc','vitesse_remplissage_colore']


class TrajetSerializer(serializers.ModelSerializer):
    bulle = BullesSerializer(many = True)
    

    class Meta:
        model = Trajet
        fields = ["id_trajet",
        "semaine",
        "jour","id_simu" ,"bulle"]
        #depth = 1

class SimulationSerializer(serializers.ModelSerializer):
    traj = TrajetSerializer(read_only=True, many =True)

    class Meta:
        model = Simulation
        fields = ["id_simu", "nom", "date_creation", "traj", "date_debut"]


class SimulationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Simulation
        fields = ["id_simu", "nom", "date_creation", "date_debut"]



class Profil_ParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profil_Param
        fields="__all__"
