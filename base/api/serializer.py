from rest_framework.serializers import ModelSerializer
from base.models import Room

class RoomSerializer(ModelSerializer):  #将Room对象设置序列化
    class Meta:
        model = Room
        fields = '__all__'