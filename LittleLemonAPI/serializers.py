from .models import Category, MenuItems, Cart
from rest_framework import serializers
from rest_framework.validators import UniqueValidator,UniqueTogetherValidator
# Third-Party imports
import bleach

## Serializing managers.
from rest_framework import serializers

from django.contrib.auth.models import User, Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model where the group name is Managers.
    """
    groups = GroupSerializer(read_only=True, many=True )
    
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "is_active",
            "groups",
        )
        
class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    slug = serializers.SlugField(max_length=200)
    def create(self, validated_data):
        return Category.objects.create(**validated_data)
    
    def update(self, instance, **validated_data):
        return super().update(instance, **validated_data)
  
class MenuItemsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200)
    price = serializers.DecimalField(max_digits=6, decimal_places=2,)
    featured = serializers.BooleanField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    def validate(self, attrs):
        attrs['title'] = bleach.clean(attrs['title'])
        title = attrs['title']
        if(attrs['price']<2):
            raise serializers.ValidationError('Price cannot be less than 2')
        # Check if the item already exists in MenuItem
        if MenuItems.objects.filter(title__icontains=title).exists():
            raise serializers.ValidationError("This item already exists in the menu.")
        return super().validate(attrs)

    class Meta:
        model = MenuItems
        fields = ['id','title', 'price', 'featured','category','category_id']
        validators = [
            #validating the uniqueness of multiple fields
            UniqueTogetherValidator(
            queryset=MenuItems.objects.all(),
            fields=['title'])
        ]
        # depth = 1
        
class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.CharField(max_length=200)
    delivery_crew = serializers.CharField(max_length=200)
    status = serializers.BooleanField()
    total = serializers.DecimalField(max_digits=6, decimal_places=2)
    date = serializers.DateTimeField()

    
class OrderItemSerializer(serializers.Serializer):
    order = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    menuitem = MenuItemsSerializer(read_only=True)
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    
class CartSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.CharField(max_length=200)
    menuitem = serializers.StringRelatedField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    # total = serializers.SerializerMethodField(method_name='calc_total')
    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    def calc_total(self, instance:MenuItems):
        return instance.price * instance.quantity
         
    def create(self, validated_data):
        return Cart.objects.create(**validated_data)
    
    def update(self, instance, **validated_data):
        return super().update(instance, **validated_data)
    class Meta:
        model = Cart
        fields = ['id']
  
    
