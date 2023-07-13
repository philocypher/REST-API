#local imports
from decimal import Decimal
from django.db.models.query_utils import Q
from django.shortcuts import  get_object_or_404
from django.contrib.auth.models import User, Group
from .serializers import MenuItemsSerializer, CategorySerializer,CartSerializer
from .serializers import OrderSerializer, OrderItemSerializer
from .serializers import UserSerializer
from .models import MenuItems, Category, Order, OrderItem, Cart
from .pagination import StandardResultsSetPagination
from . import permissions as perm
from .throttles import BurstRateThrottle, SustainedRateThrottle
# #DRF imports
from rest_framework.response import Response
from rest_framework import status as status_codes
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view,permission_classes

# views.

## Admin Adding Managers.
@api_view(['GET','POST'])
@permission_classes([permissions.IsAdminUser])
def AddManager(request):
    if request.method == 'GET':
        managers = Group.objects.all()
        return Response({'Managers':managers},status=status_codes.HTTP_200_OK)
    username =  request.data['username']
    #adding user to the managers group
    if username:
        user = get_object_or_404(User, username=username)
        manager = Group.objects.get(name='managers')
        if request.method == 'POST':
             manager.user_set.add(user)
             return Response({'Message':f'{user} Added Successfully!'}, status=status_codes.HTTP_202_ACCEPTED)
        if request.method == 'DELETE':
             manager.user_set.remove(user)
             return Response({'Message':f'{user} Removed from Managers Successfully!'},status=status_codes.HTTP_200_OK)
    
## managing categories.

@api_view(['GET','POST'])
@permission_classes([perm.IsManagerOrAdmin])
def categories(req):
        if req.method == 'GET':
            categories = Category.objects.all()
            serializer = CategorySerializer(categories,many=True)
            return Response(serializer.data, status=status_codes.HTTP_200_OK)
        if req.method == 'POST':
            serializer = CategorySerializer(data=req.data)
            if serializer.is_valid():
                serializer.create(serializer.validated_data)
                return Response(serializer.data, status=status_codes.HTTP_201_CREATED)
            return Response(serializer.errors, status=status_codes.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status_codes.HTTP_403_FORBIDDEN)
    
## Menu Items View
class MenuItemsViewSet(viewsets.ModelViewSet):
    items = MenuItems.objects.select_related('category').all()
    serializer_class = MenuItemsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    def get_throttles(self):
        throttle_classes = self.throttle_classes
        if self.action == 'list':
            if self.request.user.groups.filter(name='managers').exists() or self.request.user.is_superuser:
                throttle_classes = [BurstRateThrottle]
            else:
                throttle_classes = [SustainedRateThrottle]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            throttle_classes = [BurstRateThrottle]
        return [throttle() for throttle in throttle_classes]        
    def list(self, request):
        #filtering, seaching, and ordering implementation
        category_name = request.query_params.get('category')
        price = request.query_params.get('price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        if category_name:
            self.items = self.items.filter(category__title__icontains=category_name)
        if search:
            self.items = self.items.filter(Q(title__icontains=search) | Q(category__title__icontains=search))
        if price:
            self.items = self.items.filter(price__gte=price)
        if ordering:
            ordering_fields = ordering.split(',') 
            self.items = self.items.order_by(*ordering_fields)
        # Serializing and returning the data
        page = self.paginate_queryset(self.items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
    def create(self, request):
        if request.user.groups.filter(name='managers').exists() or request.user.is_superuser:
            category_obj = get_object_or_404(Category,pk=request.data['category_id'])
            serializer = MenuItemsSerializer(data=request.data)
            category = CategorySerializer(category_obj)
          # User belongs to 'Admin' group, allow the create action
            if serializer.is_valid():
                serializer.create(serializer.validated_data)
                return Response({
                    'message': 'Created Successfully',
                    'data': serializer.data,
                    'category': category.data
                    },
                    status=status_codes.HTTP_201_CREATED)
        else:
            # User doesn't belong to the required group, return an error response
            return Response({'detail': 'Permission denied.'}, status=status_codes.HTTP_403_FORBIDDEN)
        
        return Response(serializer.errors, status=status_codes.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        item = get_object_or_404(MenuItems, pk=pk)
        serilialized = MenuItemsSerializer(item)
        return Response(serilialized.data, status_codes.HTTP_200_OK)
            
    def update(self, request, pk=None):
        if request.user.groups.filter(name='managers').exists():
            item = get_object_or_404(MenuItems, pk=pk)
            serialized = MenuItemsSerializer(item, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return Response(serialized.data, status=status_codes.HTTP_201_CREATED)
            return Response(status= status_codes.HTTP_400_BAD_REQUEST)
        else:
            return Response(status= status_codes.HTTP_403_FORBIDDEN)
    def partial_update(self, request, pk=None):
        if request.user.groups.filter(name='managers').exists() or request.user.is_superuser:
            item = get_object_or_404(MenuItems, pk=pk)
            valid = MenuItemsSerializer(item, data=request.data, partial=True)
            if valid.is_valid():
                valid.save()
                return Response({'updated':valid.data},status_codes.HTTP_201_CREATED)
            else:
                return Response(status= status_codes.HTTP_400_BAD_REQUEST)
        else:
            return Response(status= status_codes.HTTP_403_FORBIDDEN)
    def destroy(self, request, pk=None):
        if request.user.groups.filter(name='managers').exists() or request.user.is_superuser:
            item = get_object_or_404(MenuItems, pk=pk)
            item.delete()
            return Response({"message":"Deleted Successfully"}, status_codes.HTTP_200_OK)
    
## User Management View. Adding and Removing managers.
class ManagerViewSet(viewsets.ModelViewSet):
    throttle_classes = [BurstRateThrottle]
    permission_classes = [perm.IsManager]
    def list(self, request):
            managers = User.objects.filter(groups__name="managers")
            serialized_managers = UserSerializer(managers,many=True)
            return Response({'Managers':serialized_managers.data},status=status_codes.HTTP_200_OK)
    def create(self, request):
            username =  request.data['username']
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='managers')
            managers.user_set.add(user)
            return Response({'Message': f'{user} Added Successfully!'},status=status_codes.HTTP_201_CREATED)
    def destroy(self, request,pk=None, *args, **kwargs):
            user = get_object_or_404(User, pk=pk)
            managers = Group.objects.get(name='managers')
            managers.user_set.remove(user)
            return Response({'Message': f'{user} Removed Successfully!'},status=status_codes.HTTP_200_OK)


## Delivery crew management View. Adding & Removing delivery crew members
class DeliveryCrewViewSet(viewsets.ModelViewSet):
    throttle_classes = [BurstRateThrottle]
    permission_classes = [perm.IsManager]
    groupset = Group.objects.get(name="delivery_crew")
    def list(self,request):
        deliveryCrewGroup =self.groupset.user_set.all()
        return Response({'Delivery Crew Members': UserSerializer(deliveryCrewGroup, many=True).data}, status=status_codes.HTTP_200_OK)
    def create(self, request):
            username =  request.data['username']
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name='delivery_crew')
            delivery_crew.user_set.add(user)
            return Response({'Message': f'{user} Added Successfully!'},status=status_codes.HTTP_200_OK)
    def destroy(self, request,pk=None, *args, **kwargs):
            user = get_object_or_404(User, pk=pk)
            delivery_crew = Group.objects.get(name='delivery_crew')
            delivery_crew.user_set.remove(user)
            return Response({'Message': f'{user} Removed Successfully!'},status=status_codes.HTTP_200_OK)


## Cart Management
class CartViewSet(viewsets.ModelViewSet):
    throttle_classes = [SustainedRateThrottle]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    def list(self, request):
        set = Cart.objects.filter(user=request.user.id)
        if set.count() == 0:
            return Response({'details': "Your cart is empty. Add item's titles and quantity value."})
        queryset = Cart.objects.filter(user=request.user.id)
        total = sum(cart.price for cart in set)
        return Response({
            "Cart":CartSerializer(queryset,many=True).data,
            "Total Price":total
            },
            status=status_codes.HTTP_200_OK)
    def create(self, request):
        try:
            title = request.data['title']
        except:
            return Response({'detail': 'Missing Menu Item title.'}, status=status_codes.HTTP_400_BAD_REQUEST)
        try:
            quant = request.data['quantity']
        except:
            return Response({'detail': 'Missing quantity of the Item.'}, status=status_codes.HTTP_400_BAD_REQUEST)
        user_id = request.user.id
        try:
            cart = Cart.objects.get(user_id=user_id, menuitem__title__icontains=title)
            # Update the existing cart item with new quantity, price, etc.
            cart.quantity += int(quant)
            cart.price = round(cart.unit_price * Decimal(cart.quantity), 2)
            cart.save()
            seri_cart = CartSerializer(cart)
            return Response(seri_cart.data, status=status_codes.HTTP_200_OK)
        except Cart.DoesNotExist:
            try:
                item = MenuItems.objects.get(title__icontains=title)
                menuitem = item
                unit_price = item.price
                price = round(unit_price * Decimal(quant), 2)

                # Create a new cart item
                cart = Cart.objects.create(user_id=user_id, menuitem=menuitem, price=price, quantity=quant, unit_price=unit_price)
                seri_cart = CartSerializer(cart)
                return Response(seri_cart.data, status=status_codes.HTTP_201_CREATED)
            except MenuItems.DoesNotExist:
                return Response({'detail': 'Menu item not found.'}, status=status_codes.HTTP_404_NOT_FOUND)
        
    def destroy(self, request, *args, **kwargs):
       carts = Cart.objects.filter(user=request.user.id)
       carts.delete()
       return Response(status=status_codes.HTTP_204_NO_CONTENT)
        
        
## Order Management
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
  
    def list(self,request):            
        if request.user.groups.filter(name='managers').exists() or request.user.is_superuser:
            orders = Order.objects.all()
            items = OrderItem.objects.all()
            seri_orders = OrderSerializer(orders,many=True)
            seri_items = OrderItemSerializer(items,many=True)
            return Response({'order':seri_orders.data,'items':seri_items.data}, status=status_codes.HTTP_200_OK)
        elif request.user.groups.filter(name='delivery_crew').exists():
            delivery_crew = User.objects.get(pk=request.user.id)
            orders = Order.objects.filter(delivery_crew=delivery_crew)
            items = OrderItem.objects.filter(order__delivery_crew=delivery_crew)
            seri_orders = OrderSerializer(orders,many=True)
            seri_items = OrderItemSerializer(items,many=True)
            return Response({'order':seri_orders.data,'items':seri_items.data}, status=status_codes.HTTP_200_OK)
        else:
            user = request.user
            orders = Order.objects.filter(user=user)
            items = OrderItem.objects.filter(order__user=user)
            seri_orders = OrderSerializer(orders,many=True)
            seri_items = OrderItemSerializer(items,many=True)
            return Response({'order':seri_orders.data,'items':seri_items.data}, status=status_codes.HTTP_200_OK)
       
    def create(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        if cart_items.count() != 0:
            total = sum(cart.price for cart in cart_items)
            # Create the order
            order = Order.objects.create(user=user,total=total)
            # Create order items for each cart item
            order_items = []
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    menuitem=cart_item.menuitem,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    price=cart_item.price
                )
                order_items.append(order_item)
            # Delete the user's cart items
            cart_items.delete()

            # Return the order details
            serializer = OrderSerializer(order)
            return Response(serializer.data,
                            status=status_codes.HTTP_201_CREATED)
        else:
            return Response({'detail': 'No items in your cart to order.'}, status=status_codes.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request,pk=None, *args, **kwargs):
        if request.user.groups.filter(name='managers').exists() or request.user.is_superuser:
                orders = Order.objects.get(pk=pk)
                items = OrderItem.objects.filter(order__pk=pk)
                seri_orders = OrderSerializer(orders)
                seri_items = OrderItemSerializer(items,many=True)
                return Response({'order':seri_orders.data,'items':seri_items.data}, status=status_codes.HTTP_200_OK)
        elif request.user.groups.filter(name='delivery_crew').exists():
                delivery_crew = User.objects.get(pk=request.user.id)
                orders = Order.objects.filter(delivery_crew=delivery_crew)
                items = OrderItem.objects.filter(order__delivery_crew=delivery_crew)
                seri_orders = OrderSerializer(orders,many=True)
                seri_items = OrderItemSerializer(items,many=True)
                return Response({'order':seri_orders.data,'items':seri_items.data}, status=status_codes.HTTP_200_OK)
        else:
            user = request.user
            orders = Order.objects.filter(user=user)
            items = OrderItem.objects.filter(order__user=user)
            seri_orders = OrderSerializer(orders,many=True)
            seri_items = OrderItemSerializer(items,many=True)
            return Response({'order':seri_orders.data,'items':seri_items.data}, status=status_codes.HTTP_200_OK)
    def update(self, request,pk=None, *args, **kwargs):
            if request.user.groups.filter(name='managers').exists() or request.user.is_superuser:
                try:
                    delivery_crew_name = request.data['delivery_crew']
                except:
                    return Response({'detail': 'Missing delivery_crew.'}, status=status_codes.HTTP_400_BAD_REQUEST)
                try:
                    status = request.data['status']
                except:
                    return Response({'detail': 'Missing status, 1 or 0.'}, status=status_codes.HTTP_400_BAD_REQUEST)
                crew_member = User.objects.get(username=delivery_crew_name)
                order = get_object_or_404(Order, pk=pk)
                order.status = status
                order.delivery_crew = crew_member
                order.save()
                return Response({"Updated Order":OrderSerializer(order).data},status=status_codes.HTTP_202_ACCEPTED)
    def partial_update(self, request, pk=None, *args, **kwargs):
        if request.user.groups.filter(name='managers').exists() or request.user.is_superuser:
                order = get_object_or_404(Order, pk=pk)
                try:
                    delivery_crew_name = request.data['delivery_crew']
                except:
                    return Response({'detail': 'Missing delivery_crew.'}, status=status_codes.HTTP_400_BAD_REQUEST)
                try:
                    status = request.data['status']
                except:
                    return Response({'detail': 'Missing status, 1 or 0.'}, status=status_codes.HTTP_400_BAD_REQUEST)
                crew_member = User.objects.get(username=delivery_crew_name)
                order.status = status
                order.delivery_crew = crew_member
                order.save()
                return Response({
                    "Updated Order":OrderSerializer(order).data,
                    },
                    status=202)
        
        elif request.user.groups.filter(name='delivery_crew').exists():
                order = get_object_or_404(Order, pk=pk)
                try:
                    status = request.data['status']
                except:
                    return Response({'detail': 'Missing status, 1 or 0.'}, status=status_codes.HTTP_400_BAD_REQUEST)
                order.status = status
                order.save()
                seri_order = OrderSerializer(order)
                return Response(seri_order.data, status=200)
            
                
    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name='managers').exists() or request.user.is_superuser:
            return super().destroy(request, *args, **kwargs)
        else:        
           return Response({'detail': 'Permission denied.'}, status=status_codes.HTTP_403_FORBIDDEN)
    def get_throttles(self):
        throttle_classes = self.throttle_classes
        if self.action == 'list':
            if self.request.user.groups.filter(name='managers').exists() or self.request.user.is_superuser:
                throttle_classes = [BurstRateThrottle]
            else:
                throttle_classes = [SustainedRateThrottle]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            throttle_classes = [BurstRateThrottle]
        return [throttle() for throttle in throttle_classes]