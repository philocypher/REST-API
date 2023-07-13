from django.urls import path
# local
from . import views
app_name = 'api'

urlpatterns = [
    # Adding managers as admin.
    path('add-manager',views.AddManager, name='add-manager'),
    # Adding Categories
    path('categories',views.categories, name='categories'),
    # Menu Items Mapping
    path('menu-items', views.MenuItemsViewSet.as_view({
        'get': 'list',
        'post': 'create',
    })),
    path('menu-items/<int:pk>', views.MenuItemsViewSet.as_view({
        'get':'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
        })),
    # Managers management
    path('groups/manager/users', views.ManagerViewSet.as_view({
        'get': 'list',
        'post': 'create',
        })),
    path('groups/manager/users/<int:pk>', views.ManagerViewSet.as_view({
        'delete': 'destroy',
    })),
    ## Delivery Crew Management.
    path('groups/delivery-crew/users',views.DeliveryCrewViewSet.as_view({
        'get':'list',
        'post':'create',
        })),
    path('groups/delivery-crew/users/<int:pk>',views.DeliveryCrewViewSet.as_view({
        'delete':'destroy',
        })),
    ## Cart Management.
    path('cart/menu-items',views.CartViewSet.as_view({
         'get':'list',
         'post':'create',
         'delete':'destroy',
        })),
    ## Order Management.
    path('orders',views.OrderViewSet.as_view({
        'get':'list',
        'post':'create',
        })),
    path('orders/<int:pk>',views.OrderViewSet.as_view({
        'get':'retrieve',
        'put':'update',
        'patch':'partial_update',
        'delete':'destroy',
    })
    )
]
