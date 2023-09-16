from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializer import RoomSerializer


@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api/'
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ] 
    return Response(routes) #safe = False意思是并不强制要求是可以序列化的py对象

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms,many=True) #设置many表示是一堆room的set
    return Response(serializer.data)

@api_view(['GET'])
def getRoom(request,pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room) #设置many表示是一堆room的set
    return Response(serializer.data)