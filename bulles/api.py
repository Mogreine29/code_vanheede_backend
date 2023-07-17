from rest_framework.response    import Response
from rest_framework.views       import APIView
from bulles.models              import Bulles,Site
from .serializers               import BullesSerializer,SiteSerializer
from rest_framework.viewsets    import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser


class BullesReturn(APIView):
    def get(self,request,*args,**kwargs):
        qs=Bulles.objects.all()
        serializer = BullesSerializer(qs, many=True)
        return Response(serializer.data)
    
    def post(self,request, *args, **kwargs):
        serializer = BullesSerializer(data = request.data )
        serializer.is_valid(raise_exception = True)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)



class BullesViewSet(APIView):
    def get(self,request, *args,**kwargs):
        queryset = Bulles.objects.prefetch_related('id_site')
        bulles = Bulles.objects.select_related('id_site').all()
        
        id_to_addresse = {}
        for bulle in bulles:
            id_to_addresse[bulle.id_bulle] = bulle.id_site.nom
        serializer = BullesSerializer(queryset,many=True)
        
        for value in serializer.data:
            value["addresse"] = id_to_addresse[value["id_bulle"]]
            
        return Response(serializer.data)

    def post(self,request, *args, **kwargs):
        serializer = BullesSerializer(data = request.data )
        serializer.is_valid(raise_exception = True)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)

class SitesReturn(APIView):
    def get(self,request,*args,**kwargs):
        qs=Site.objects.all()
        serializer = SiteSerializer(qs, many=True)
        return Response(serializer.data)

class SiteViewSet(APIView):
     def get(self,request, *args,**kwargs):
        queryset = Site.objects.all()
        serializer = SiteSerializer(queryset,many=True)
        return Response(serializer.data)