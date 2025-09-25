from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Food, Meal, MealItem
from .serializers import FoodSerializer, MealSerializer, MealItemSerializer


class FoodViewSet(viewsets.ModelViewSet):
    """Food database"""
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Food.objects.filter(
            Q(is_custom=False) | Q(created_by=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, is_custom=True)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """GET /foods/search?q=query - Search foods"""
        query = request.query_params.get('q', '')
        foods = self.get_queryset().filter(
            Q(name__icontains=query) | Q(brand__icontains=query)
        )[:20]
        return Response(FoodSerializer(foods, many=True).data)


class MealViewSet(viewsets.ModelViewSet):
    """Meal management"""
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Meal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """POST /meals/{id}/items - Add food item to meal"""
        meal = self.get_object()
        serializer = MealItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(meal=meal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

